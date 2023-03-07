from datetime import datetime, timedelta
from os import environ

import requests
from redis import Redis

from logs.logs import setup_train_loger

REDIS_HOST_NAME = environ.get("REDIS_HOST_NAME", "localhost")
REDIS_PORT = environ.get("REDIS_PORT", 6379)
STREAM_KEY = environ.get("STREAM_KEY", "stream")
API_URI = environ.get("API_URI", "")


class TrainStreamConsumer:
    """Redis stream consumer class for central"""

    OPEN: str = "open"
    CLOSE: str = "close"
    GATE_TIMEOUT_SECONDS: int = 10

    def __init__(
        self,
        redis_host: str,
        redis_port: str,
        stream_key: str,
        last_job_id: int = 0,
    ) -> None:
        self.redis_host = redis_host
        self.redis_port = redis_port
        self.stream_key = stream_key
        self.last_job_id = last_job_id
        self.gate_last_close_state_time = ""
        self.flag_gate_to_be_open = False

    def connect_to_redis(self) -> None:
        """Config redis connection"""
        hostname = self.redis_host
        port = self.redis_port
        self.redis_connection = Redis(hostname, port, decode_responses=True)

    def setup_logers(self) -> None:
        """Setup train logers to files <name>.log"""
        self.slow_log = setup_train_loger("SLOW")
        self.normal_log = setup_train_loger("NORMAL")
        self.fast_log = setup_train_loger("FAST")
        self.station_log = setup_train_loger("STATION")

    def listener(self, sleep_ms: int = 1000) -> None:
        """Redis stream consumer listener.

        Gets train (producer) data and logs it to files.
        Logs train current speed depending on the value to separate files
        (slow.log, normal.log, fast.log). Logs train near station (station.log)
        and request Lineman about current gate status.
        If gate is open request Lineman to close the gate.
        If gate is closed logs warning message.
        After 10 seconds request Lineman to open the gate.

        Args:
            sleep_ms (int, optional): number of milliseconds to wait,
            if no new jobs avaible in the redis stream. Defaults to 5000.
        """
        while True:
            try:
                # Open gate after timeout
                self.gate_to_be_open(self.GATE_TIMEOUT_SECONDS)
                # stream consumer - listen for jobs in redis stream
                response = self.redis_connection.xread(
                    {self.stream_key: self.last_job_id}, count=1, block=sleep_ms
                )
                if response:
                    job = response[0]
                    self.current_job_id = job[1][0][0]
                    self.current_job_data = job[1][0][1]
                    print(self.current_job_id, self.current_job_data)

                    # Log train current speed
                    if "current_speed" in self.current_job_data:
                        train_current_speed = float(
                            self.current_job_data["current_speed"]
                        )
                        if 0 <= train_current_speed < 40:
                            self.slow_log.info(
                                f"Train current speed: {train_current_speed}"
                            )
                        elif 40 <= train_current_speed < 140:
                            self.normal_log.info(
                                f"Train current speed: {train_current_speed}"
                            )
                        elif 140 <= train_current_speed < 180:
                            self.fast_log.info(
                                f"Train current speed: {train_current_speed}"
                            )

                    # Log train near station
                    elif "near_station" in self.current_job_data:
                        train_near_station = self.current_job_data["near_station"]
                        self.station_log.info(
                            f"Train is approaching: {train_near_station} station"
                        )

                        # Request Lineman for gate state
                        response = self.get_lineman_state()
                        gate_is_open = response.get("is_open", "")
                        self.gate_last_close_state_time = response.get("timestamp", "")

                        if gate_is_open:
                            print(
                                f"Gate is closed:\n{self.gate_last_close_state_time}\n{datetime.now()}"
                            )
                            self.close_gate()
                            self.gate_last_close_state_time = (
                                self.get_lineman_state().get("timestamp", "")
                            )

                        else:
                            self.station_log.warning("Gate was already closed!")
                            self.flag_gate_to_be_open = True
                            self.gate_last_close_state_time = str(datetime.now())
                    # Update last job id
                    self.last_job_id = self.current_job_id

            except ConnectionError as error:
                print("ERROR REDIS CONNECTION: {}".format(error))

    def get_lineman_state(self) -> dict:
        """Lineamn API GET request. Returns gate json data.

        Returns:
            dict: {"is_open": <Bool>, "timestamp": <str>}
        """
        response = requests.get(API_URI)
        return response.json()

    def _change_lineman_state(self, msg: str) -> None:
        """Lineman API PUT request with payload to toggle the gate.

        Args:
            msg (str): "open" or "close"
        """
        requests.put(API_URI, json={"toggle": msg})

    def open_gate(self) -> None:
        """API open gate wraper with log (station.log)."""
        self._change_lineman_state(self.OPEN)
        self.flag_gate_to_be_open = False
        self.station_log.info("Gate is opened")

    def close_gate(self) -> None:
        """API close gate wraper with log (station.log)."""
        self._change_lineman_state(self.CLOSE)
        self.flag_gate_to_be_open = True
        self.station_log.info("Gate is closed")

    def gate_to_be_open(
        self,
        seconds: int,
    ) -> None:
        """Open gate wrapper after fixed amount of seconds.

        Args:
            seconds (int): Amount of seconds after which sends request.
        """
        if self.flag_gate_to_be_open:
            now = datetime.now()
            previous = datetime.strptime(
                self.gate_last_close_state_time, "%Y-%m-%d %H:%M:%S.%f"
            )
            if (now - previous) >= timedelta(seconds=seconds):
                print(f"OPEN GATE AFTER 10 sec:\n{previous}\n{now}")
                self.open_gate()


if __name__ == "__main__":
    CentralConsumer = TrainStreamConsumer(REDIS_HOST_NAME, REDIS_PORT, STREAM_KEY)
    CentralConsumer.connect_to_redis()
    CentralConsumer.setup_logers()
    CentralConsumer.listener()

from redis import Redis
from os import environ
import requests
import json
from logs.logs import setup_train_loger


REDIS_HOST_NAME = environ.get("REDIS_HOST_NAME", "localhost")
REDIS_PORT = environ.get("REDIS_PORT", 6379)
STREAM_KEY = environ.get("STREAM_KEY", "stream")
BASE = "http://127.0.0.1:5000/api/v1/"


class TrainStreamConsumer:
    """Redis stream consumer class"""

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

    def connect_to_redis(self) -> None:
        hostname = self.redis_host
        port = self.redis_port
        self.redis_connection = Redis(hostname, port, decode_responses=True)

    def setup_logers(self) -> None:
        self.slow_log = setup_train_loger("SLOW")
        self.normal_log = setup_train_loger("NORMAL")
        self.fast_log = setup_train_loger("FAST")
        self.station_log = setup_train_loger("STATION")

    def listen_for_data(self, sleep_ms: int = 5000) -> None:
        while True:
            try:
                response = self.redis_connection.xread(
                    {self.stream_key: self.last_job_id}, count=1, block=sleep_ms
                )
                if response:
                    job = response[0]
                    self.current_job_id = job[1][0][0]
                    self.current_job_data = job[1][0][1]
                    print(self.current_job_id, self.current_job_data)

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
                    elif "near_station" in self.current_job_data:
                        train_near_station = self.current_job_data["near_station"]
                        self.station_log.info(
                            f"Train is approaching: {train_near_station} station"
                        )
                        # self.request_lineman()
                    self.last_job_id = self.current_job_id

            except ConnectionError as error:
                print("ERROR REDIS CONNECTION: {}".format(error))

    def get_lineman_state(self):
        response = requests.get(BASE + "state")
        response = json.loads(response)
        print(response)
        pass

    def post_lineman_state(self, msg):
        data = {"": "Open"}
        data = json.dumps(data)
        response = requests.get(BASE + "state/" + msg)


if __name__ == "__main__":
    CentralConsumer = TrainStreamConsumer(REDIS_HOST_NAME, REDIS_PORT, STREAM_KEY)
    CentralConsumer.connect_to_redis()
    CentralConsumer.setup_logers()
    CentralConsumer.listen_for_data()

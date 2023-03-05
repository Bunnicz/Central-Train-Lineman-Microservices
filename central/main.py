from redis import Redis
import logging
from os import environ

REDIS_HOST_NAME = environ.get("REDIS_HOST_NAME", "localhost")
REDIS_PORT = environ.get("REDIS_PORT", 6379)
STREAM_KEY = environ.get("STREAM_KEY", "stream")


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

    def get_train_data(self, sleep_ms: int = 5000):
        try:
            response = self.redis_connection.xread(
                {self.stream_key: self.last_job_id}, count=1, block=sleep_ms
            )
            if response:
                job = response[0]
                self.current_job_id = job[1][0][0]
                self.current_job_data = job[1][0][1]
                if "current_speed" in self.current_job_data:
                    self.train_current_speed = float(
                        self.current_job_data["current_speed"]
                    )
                elif "near_station" in self.current_job_data:
                    self.train_near_station = str(self.current_job_data["near_station"])
                self.last_job_id = self.current_job_id

        except ConnectionError as e:
            print("ERROR REDIS CONNECTION: {}".format(e))

    def listen_for_data(self):
        while True:
            self.get_train_data()
            if 0 <= self.train_current_speed < 40:
                # self.log_to_file("logs/slow.log", self.train_current_speed)
                slow = self.create_loger("slow")
                # slow = logging.getLogger('slow')
                # fh = logging.FileHandler('slow.log')
                # slow.addHandler(fh)
                slow.info(self.train_current_speed)
            elif 40 <= self.train_current_speed < 140:
                # self.log_to_file("logs/normal.log", self.train_current_speed)
                normal = self.create_loger("normal")
                normal.info(self.train_current_speed)
            elif 140 <= self.train_current_speed < 180:
                # self.log_to_file("logs/fast.log", self.train_current_speed)
                fast = self.create_loger("fast")
                fast.info(self.train_current_speed)
            elif self.train_near_station:
                # self.log_to_file("logs/station.log", self.train_near_station)
                station = self.create_loger("station")
                station.info(self.train_near_station)
                # GET
            # print(self.current_job_id, self.current_job_data)

    def create_loger(file_name: str) -> callable[logging]:
        logging.basicConfig(
            format="%(asctime)s %(levelname)s %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
            encoding="utf-8",
        )
        logger = logging.getLogger(file_name)
        fh = logging.FileHandler(file_name + ".log")
        logger.addHandler(fh)
        return logger


if __name__ == "__main__":
    CentralConsumer = TrainStreamConsumer(REDIS_HOST_NAME, REDIS_PORT, STREAM_KEY)
    CentralConsumer.connect_to_redis()
    CentralConsumer.listen_for_data()

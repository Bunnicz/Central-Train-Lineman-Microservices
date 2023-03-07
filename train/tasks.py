from celery import shared_task
import random
from redis import Redis
from os import environ


STATION_NAMES = [
    "Pławna Dolna",
    "Bogumiłowice",
    "Sędziny",
    "Krępa Koszalińska",
    "Kępa Potocka",
    "Klara",
    "Kosowo Wielkopolskie",
    "Nakomiady",
    "Siódmak",
    "Piekary Śląskie",
    "Czarnca",
    "Malce",
    "Garzyn",
    "Kalisz Pomorski Miasto",
    "Czastary",
]

REDIS_HOST_NAME = environ.get("REDIS_HOST_NAME", "localhost")
REDIS_PORT = environ.get("REDIS_PORT", 6379)
STREAM_KEY = environ.get("STREAM_KEY", "stream")


def _stream_send_data(
    REDIS_HOST_NAME: str, REDIS_PORT: str, STREAM_KEY: str, data: dict
) -> None:
    try:
        redis = Redis(
            host=REDIS_HOST_NAME,
            port=REDIS_PORT,
            decode_responses=True,
        )
        job_id = redis.xadd(STREAM_KEY, data)
        print(f"Created job {job_id}: {data}")

    except ConnectionError as error:
        print("ERROR REDIS CONNECTION: {}".format(error))


@shared_task
def stream_train_current_speed() -> None:
    data = {"current_speed": round(random.uniform(0, 180), 1)}
    _stream_send_data(REDIS_HOST_NAME, REDIS_PORT, STREAM_KEY, data)


@shared_task
def stream_train_near_station() -> None:
    data = {"near_station": random.choice(STATION_NAMES)}
    _stream_send_data(REDIS_HOST_NAME, REDIS_PORT, STREAM_KEY, data)

import random
from os import environ

from celery import shared_task
from redis import Redis

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
    """Connects to Redis stream and adds job with data.

    Args:
        REDIS_HOST_NAME (str): Redis hostname.
        REDIS_PORT (str): Redis port.
        STREAM_KEY (str): Redis stream key.
        data (dict): dict data.
    """
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
    """Add job with data: random current_speed intiger (0-180) to redis stream."""
    data = {"current_speed": round(random.uniform(0, 180), 1)}
    _stream_send_data(REDIS_HOST_NAME, REDIS_PORT, STREAM_KEY, data)


@shared_task
def stream_train_near_station() -> None:
    """Add job with data: random near_station string station name to redis stream."""
    data = {"near_station": random.choice(STATION_NAMES)}
    _stream_send_data(REDIS_HOST_NAME, REDIS_PORT, STREAM_KEY, data)

from os import environ

REDIS_HOST_NAME = environ.get("REDIS_HOST_NAME", "redis")
REDIS_PORT = environ.get("REDIS_PORT", "6379")


broker_url = f"redis://{REDIS_HOST_NAME}:{REDIS_PORT}"
result_backend = f"redis://{REDIS_HOST_NAME}:{REDIS_PORT}"

task_serializer = "json"
result_serializer = "json"
accept_content = ["json"]
timezone = "Europe/Warsaw"
enable_utc = True

imports = ("tasks",)

beat_schedule = {
    "stream-train-current-speed": {
        "task": "tasks.stream_train_current_speed",
        "schedule": 10.0,
    },
    "stream-train-near-station": {
        "task": "tasks.stream_train_near_station",
        "schedule": 20.0,
    },
}

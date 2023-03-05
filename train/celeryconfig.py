broker_url = "redis://redis:6379"
result_backend = "redis://redis:6379"

task_serializer = "json"
result_serializer = "json"
accept_content = ["json"]
timezone = "Europe/Warsaw"
enable_utc = True

imports = ("tasks",)

beat_schedule = {
    "stream-train-current-speed": {
        "task": "tasks.stream_train_current_speed",
        "schedule": 5.0,
    },
    "stream-train-near-station": {
        "task": "tasks.stream_train_near_station",
        "schedule": 15.0,
    },
}

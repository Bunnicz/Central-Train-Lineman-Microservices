# Micro Train

## How to run the project

1. clone the repo
2. create .env file based on .env.example
3. Run docker compose

```bash
docker-compose up --build
```

NOTE: Lineman API will create table inside of basic postgreSQL database called 'postgres', if you want to change that edit your .env file and after running docker-compose you need to manually create database with your custom name inside postgres docker image.

You can do it with:

```bash
docker ps # copy postgre container ID
docker exec -it <postgres_container_ID> bash
psql -U postgres
CREATE DATABASE <database_name>;
```

## API endpoints

1. You can check detailed swagger documentation at localhost:5000/apidocs

2. GET "/api/v1/state" - returns current gate status with timestamp:

```json
{
    "is_open": <bool>,
    "timestamp": <timestamp>
}
```

3. POST "/api/v1/state" - changes current gate status and records it in database:

```json
{
    "toggle": <str> // "open" or "close"
}
```

## Micro Train architecture

Repo consists of services:

1. postgreSQL (Database for Lineman API)
2. Redis (Redis stream)
3. central (redis stream consumer, logging)
4. Lineman API (Railroad crossing gate)
5. train (redis stream producer, Celery, Celery Beat)

# Microservices example project

## How to run the project

1. clone the repo.
2. create .env file based on .env.example
3. Run docker compose command.

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

## Project architecture

Project consists of microservices:

1. postgreSQL (Database for Lineman API).
2. Redis (Redis stream).
3. "Train" service (redis stream producer, Celery, Celery Beat).
4. "Central" service (redis stream consumer, logging).
5. "Lineman" service API (Railroad crossing gate).

## Project description

### Train (microservice 1)

It simulates the work of a train locomotive in a simplified way.

The microservice announces in the queuing system:

- information about the current speed of the train every 10 seconds. The value is a random number in the range [0.0, 180.0]
- every 180 seconds information on which station the train is approaching. The value is a random station name from the defined list.

### Central (microservice 2)

The central is responsible for monitoring the work of trains.

Based on the information broadcast by the train, it implements the following business rules:

#### Train speed message handling

- information about the current speed of the train along with the current time are saved to the following files:
  - slow.log when speed in range [0.0, 40.)
  - normal.log when speed in range [40.0, 140.)
  - fast.log when speed in range [140.0, 180.0]

#### Handling the message about approaching the station

- information about approaching the station is logged by the logging module and contains information about the station to which the train is approaching and the current time.

- when receiving information about the approach of the train to the station, the microservice asks the Lineman service about the condition of the crossing gate.
  - if it is open, it sends a message to the Lineman to lower the crossing gate.
  - if it is closed, it logs the anomaly and goes to the next point.
- 10 seconds after closing the crossing gate, sends a message to the Lineman to raise the crossing gate.
- information about raising and lowering the crossing gate is logged with the INFO level.

Communication with the Lineman takes place via REST+JSON.

### Lineman (microservice 3)

It simulates in a simplified way the work of a railway crossing.

The microservice provides a REST+JSON interface that enables:

- checking the current status of the crossing gate (open/closed, information about the last change).
- changing the current state of the crossing gate.

The microservice stores information about the state of the crossing gate and information about the last change in the database.

"""The entry point into the project."""

import logging
import asyncio
from contextlib import asynccontextmanager
from systemd.journal import JournalHandler

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from controller import Controller
from database import Database
import models
import config

log = logging.getLogger("thermostat")
log.addHandler(JournalHandler())
log.setLevel(logging.INFO)

database = Database(log)
controller = Controller(log)

@asynccontextmanager
async def lifespan(_app: FastAPI):
    """Run when the program starts/terminates"""
    await _startup()
    yield
    await _shutdown()

app = FastAPI(lifespan=lifespan)

origins = [
    "*",
    "https://raspberrypi.local"
]


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

async def _startup():
    try:
        config.load_config()
    except Exception as e:
        log.info("Loading dot env file failed %s", str(e))
        print("Loading dot env file failed " + str(e))
    if config.config["DATABASE"]["DB_ENABLED"] == "True":
        try:
            await database.connect_db(config.config["DATABASE"]["DB_USER"],
                                      config.config["DATABASE"]["DB_PASSWORD"],
                                      config.config["DATABASE"]["DB_DATABASE"],
                                      config.config["DATABASE"]["DB_HOST"])
        except Exception as e:
            log.info("Connecting to database failed with %s", str(e))
            print("Connecting to database failed with " + str(e))
    else:
        log.info("Database disabled in config")
        print("Database disabled in config")
    print("the lifespan is happening")
    asyncio.create_task(drive_status_loop())
    asyncio.create_task(drive_history_loop())


async def _shutdown():
    if config.config["DATABASE"]["DB_ENABLED"] == "True":
        await database.disconnect_db()


async def drive_status_loop():
    """
    Creates a heartbeat driving the thermostat's status every 'interval_seconds'.
    Also logs the status to the database if available.

    Caution: Will block forever if awaited. Use as async task instead.
    """
    interval_seconds = 10
    while True:
        print("Driving status loop")
        controller.drive_status()
        if config.config["DATABASE"]["DB_ENABLED"] == "True":
            await database.update_averages(controller.status.average_temp,
                                           controller.status.target_temp)
            await database.update_pins(controller.status.pins, controller.status.usable)
        await asyncio.sleep(interval_seconds)


async def drive_history_loop():
    """
    Creates a heartbeat to update history data.

    Caution: Will block forever if awaited. Use as async task instead.
    """
    while True:
        print("Driving history loop")
        controller.update_history()
        await asyncio.sleep(120)


@app.get("/", response_model=models.StatusObject)
async def root() -> dict:
    """Returns the current status of the thermostat."""
    return models.StatusObject(status = controller.get_status())


@app.get("/history")
async def get_history() -> models.HistoryObject:
    """
    Gets the history of the average temperatures
    Returns: list of tuples containing timestamps and temperature.
    """
    return models.HistoryObject(history = controller.get_history())


@app.put("/sensor-status")
async def update_sensor_status(name: str, temperature: float, humidity: float):
    """Adds or updates an entry to the sensors list keyed by `name`."""
    controller.update_sensor_status(name, temperature, humidity)
    if config.config["DATABASE"]["DB_ENABLED"] == "True":
        await database.update_sensors(name, temperature, humidity)

    return "Success"


@app.put("/target_temperature")
async def set_target_temp(temperature: int) -> str:
    """Sets the temperature the thermostat aims for."""
    controller.set_target_temp(temperature)
    return f"Temperature set to f{temperature} degrees fahrenheit"


@app.put("/usable")
async def set_usable(ac: bool, cooler: bool, furnace: bool):
    """Set which systems the thermostat can use."""
    controller.set_usable(ac, cooler, furnace)
    return "Success"


@app.put("/manual_override")
async def manual_override(override: bool, pins: models.Pins):
    """
    Overrides the pins to manually turn them on or off.

    Be careful using this if the system is hooked up to a real HVAC system.
    """
    print(override, pins)
    controller.set_manual_override(override, pins)
    return "Success"

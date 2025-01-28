from fastapi import FastAPI, Response, status
from fastapi_utils.tasks import repeat_every
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from pydantic import BaseModel
import asyncio

from controller import Controller
from database import Database
import models
import logging
from systemd.journal import JournalHandler
import dotenv
import os

log = logging.getLogger("thermostat")
log.addHandler(JournalHandler())
log.setLevel(logging.INFO)

app = FastAPI()
database = Database(log)
controller = Controller(log)

is_shutdown = False

@asynccontextmanager
async def lifespan(app: FastAPI):
  try:
    dotenv.load_dotenv()
  except Exception as e:
    log.info("Loading dot env file failed" + str(e))
    print("Loading dot env file failed " + str(e))
  if os.getenv("RPI_DB_ENABLED") == "true":
    try:
      await database.connect_db(os.getenv("RPI_DB_USER"), os.getenv("RPI_DB_PASSWORD"),
                                os.getenv("RPI_DB_DATABASE"), os.getenv("RPI_DB_HOST"))
    except Exception as e:
      log.info("Connecting to database failed with " + str(e))
      print("Connecting to database failed with " + str(e))
  global is_shutdown
  print("the lifespan is happening")
  asyncio.create_task(drive_status_loop())
  asyncio.create_task(drive_history_loop())
  yield
  print("post-yield")
  if os.getenv("RPI_DB_ENABLED") == "true":
    await database.disconnect_db()
  is_shutdown = True

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


async def drive_status_loop():
  global is_shutdown
  while (not is_shutdown):
    print("Driving status loop")
    drive_status()
    if os.getenv("RPI_DB_ENABLED") == "true":
      await database.update_averages(controller.status.average_temp, controller.status.target_temp)
      await database.update_pins(controller.status.pins, controller.status.usable)
    await asyncio.sleep(10)


async def drive_history_loop():
  global is_shutdown
  while (not is_shutdown):
    print("Driving history loop")
    controller.update_history()
    await asyncio.sleep(120)


def drive_status():
  try:
    controller.drive_status()
  except asyncio.CancelledError:
    pass


@app.get("/", response_model=models.StatusObject)
async def root() -> dict:
  return models.StatusObject(status = controller.get_status())


@app.get("/history")
async def get_history() -> models.HistoryObject:
  return models.HistoryObject(history = controller.get_history())


@app.put("/sensor-status")
async def update_sensor_status(name: str, temperature: float, humidity: float):
  controller.update_sensor_status(name, temperature, humidity)
  if os.getenv("RPI_DB_ENABLED") == "true":
    await database.update_sensors(name, temperature, humidity)

  return "Success"


@app.put("/target_temperature")
async def set_target_temp(temperature: int) -> str:
  controller.set_target_temp(temperature)
  return "Temperature set to {} degrees fahrenheit".format(temperature)


@app.put("/usable")
async def set_usable(ac: bool, cooler: bool, furnace: bool):
  controller.set_usable(ac, cooler, furnace)
  return "Success"


@app.put("/manual_override")
async def manual_override(override: bool, pins: models.Pins):
  print(override, pins)
  controller.set_manual_override(override, pins)
  return "Success"

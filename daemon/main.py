from fastapi import FastAPI, Response, status
from fastapi_utils.tasks import repeat_every
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from pydantic import BaseModel
import asyncio

from controller import Controller
import models


is_shutdown = False
controller = Controller()

@asynccontextmanager
async def lifespan(app: FastAPI):
    global is_shutdown
    print("the lifespan is happening")
    asyncio.create_task(drive_status_loop())
    asyncio.create_task(drive_history_loop())
    yield
    print("post-yield")
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

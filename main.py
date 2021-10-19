from fastapi import FastAPI, Response, status
from fastapi_restful.tasks import repeat_every
from pydantic import BaseModel

from controller import Controller

app = FastAPI()
controller = Controller()


class Status(BaseModel):
  pump: bool
  fan_low: bool
  fan_high: bool
  furnace: bool
  temp: int
  humidity: int


@app.on_event("startup")
@repeat_every(seconds=10)
async def drive_status():
  controller.drive_status()


@app.get("/", response_model=Status)
#@app.get("/")
async def root() -> dict:
  return controller.get_status()


@app.get("/get_temperature")
async def get_temperature() -> float:
  return controller.get_temperature()


@app.put("/set_temperature")
async def set_temperature(temperature: int) -> str:
  controller.set_target_temp(temperature)
  return "Temperature set to {} degrees fahrenheit".format(temperature)

@app.get("/usable")
async def get_usable() -> dict:
  return { "cooler": controller.cooler_usable, "furnace": controller.furnace_usable }


@app.put("/usable")
async def set_usable(cooler: bool, furnace: bool):
  controller.cooler_usable = cooler
  controller.furnace_usable = furnace
  return "Success"


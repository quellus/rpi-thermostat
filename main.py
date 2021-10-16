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


@app.on_event("startup")
@repeat_every(seconds=1)
async def drive_status():
  controller.drive_status()


@app.get("/", response_model=Status)
async def root() -> dict:
  return controller.get_status()


@app.get("/get_temperature")
async def get_temperature() -> float:
  return controller.get_temperature()


@app.put("/set_temperature")
async def set_temperature(temperature: int) -> str:
  controller.set_target_temp(temperature)
  return "Temperature set to {} degrees fahrenheit".format(temperature)


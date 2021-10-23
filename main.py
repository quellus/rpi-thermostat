from fastapi import FastAPI, Response, status
from fastapi_restful.tasks import repeat_every
from pydantic import BaseModel

from controller import Controller
import models

app = FastAPI()
controller = Controller()


@app.on_event("startup")
@repeat_every(seconds=10)
async def drive_status():
  controller.drive_status()


@app.get("/", response_model=models.Status)
async def root() -> dict:
  return controller.get_status()


@app.get("/temperature")
async def get_temperature() -> float:
  return controller.get_temperature()


@app.put("/target_temperature")
async def set_target_temp(temperature: int) -> str:
  controller.set_target_temp(temperature)
  return "Temperature set to {} degrees fahrenheit".format(temperature)


@app.put("/usable")
async def set_usable(cooler: bool, furnace: bool):
  controller.set_usable(cooler, furnace)
  return "Success"


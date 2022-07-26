from fastapi import FastAPI, Response, status
from fastapi_restful.tasks import repeat_every
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from controller import Controller
import models

app = FastAPI()
controller = Controller()

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

@app.on_event("startup")
@repeat_every(seconds=10)
async def drive_status():
  controller.drive_status()


@app.get("/", response_model=object)
async def root() -> dict:
  return {"status": controller.get_status()}


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


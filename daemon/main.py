from fastapi import FastAPI, Response, status
from fastapi_restful.tasks import repeat_every
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from controller import Controller
import ssl
import models

app = FastAPI()
controller = Controller()

origins = [
  "*",
  "https://raspberrypi.local"
]

ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
ssl_context.load_cert_chain('/home/pi/daemon-selfsigned.crt', keyfile='/home/pi/daemon-selfsigned.key')

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


@app.on_event("startup")
@repeat_every(seconds=120)
async def drive_history():
  controller.update_history()


@app.get("/", response_model=models.StatusObject)
async def root() -> dict:
  return models.StatusObject(status = controller.get_status())


@app.get("/temperature")
async def get_temperature() -> float:
  return controller.get_temperature()

@app.get("/history")
async def get_history() -> dict:
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


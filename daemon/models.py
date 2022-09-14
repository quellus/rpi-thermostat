from pydantic import BaseModel

class Pins(BaseModel):
  pump: bool
  fan_on: bool
  fan_speed: bool
  furnace: bool


class Usable(BaseModel):
  cooler: bool
  furnace: bool


class Status(BaseModel):
  pins: Pins
  usable: Usable
  target_temp: int
  temp: float
  humidity: int
  manual_override: bool


class StatusObject(BaseModel):
  status: Status


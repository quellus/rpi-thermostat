from pydantic import BaseModel

class Pins(BaseModel):
  pump: bool
  fan_low: bool
  fan_high: bool
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


class StatusObject(BaseModel):
  status: Status


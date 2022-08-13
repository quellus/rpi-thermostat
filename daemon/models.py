from pydantic import BaseModel

class Pins(BaseModel):
  pump: bool
  fan_low: bool
  fan_high: bool
  furnace: bool


class Usable(BaseModel):
  cooler: bool
  furnace: bool


class Temperature(BaseModel):
  temperature: float
  timestamp: float


class Status(BaseModel):
  pins: Pins
  usable: Usable
  target_temp: int
  temperatures: dict[str, Temperature]
  humidity: int
  manual_override: bool


class StatusObject(BaseModel):
  status: Status


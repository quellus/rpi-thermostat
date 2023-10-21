from pydantic import BaseModel

class Pins(BaseModel):
  pump: bool
  fan_on: bool
  ac: bool
  furnace: bool


class Usable(BaseModel):
  ac: bool
  cooler: bool
  furnace: bool


class Status(BaseModel):
  pins: Pins
  usable: Usable
  target_temp: int
  average_temp: float
  humidity: int
  manual_override: bool
  sensors: dict[str, dict]


class StatusObject(BaseModel):
  status: Status


class HistoryObject(BaseModel):
  history: list 

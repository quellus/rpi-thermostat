"""Defines datatypes FastAPI can send/receive."""

from pydantic import BaseModel


class Pins(BaseModel):
    """GPIO pin state."""
    pump: bool
    fan_on: bool
    ac: bool
    furnace: bool


class Usable(BaseModel):
    """Whether each system can be turned on."""
    ac: bool
    cooler: bool
    furnace: bool


class Status(BaseModel):
    """Entire state of thermostat"""
    pins: Pins
    usable: Usable
    target_temp: int
    average_temp: float
    manual_override: bool
    sensors: dict[str, dict]


class StatusObject(BaseModel):
    status: Status


class HistoryObject(BaseModel):
    history: list

from datetime import datetime
import asyncpg
import os
import dotenv

class Database:
  def __init__(self, log):
    self.db_connection = None
    self.log = log
    dotenv.load_dotenv()


  async def connect_db(self):
    self.log.info("Connecting to database")
    print("Connecting to database")
    try:
      dotenv.load_dotenv()
      self.db_connection = await asyncpg.connect(user=os.getenv("DB_USER"), password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_DATABASE"), host=os.getenv("DB_HOST"))
    except Exception as e:
      self.log.error("Database connection failed with:\n" + e)
      print("Database connection failed with:")
      print(e)
    else:
      self.log.error("Database connection successful")
      print("Database connection successful")


  async def disconnect_db(self):
    self.log.info("Disconnecting from database")
    print("Disonnecting from database")
    if self.db_connection:
      await self.db_connection.close()


  async def update_sensors(self, name, temperature, humidity):
    self.log.info("Sending sensor status to database")
    print("Sending sensor status to database")

    try:
      dt = datetime.now()

      await self.db_connection.execute(
        "INSERT INTO sensors VALUES ($1, $2, $3, $4)",
        dt, name, temperature, humidity
      )
    except Exception as e:
      self.log.error("Database query failed with:\n" + e)
      print("Database query failed with:")
      print(e)


  async def update_averages(self, avg_temp, target_temp):
    self.log.info("Sending averages to database")
    print("Sending averages to database")

    try:
      dt = datetime.now()

      await self.db_connection.execute(
        "INSERT INTO averages VALUES ($1, $2, $3)",
        dt, avg_temp, target_temp
      )
    except Exception as e:
      self.log.error("Database query failed with:\n" + e)
      print("Database query failed with:")
      print(e)


  async def update_pins(self, pins, usable):
    self.log.info("Sending pins to database")
    print("Sending pins to database")

    try:
      dt = datetime.now()

      await self.db_connection.execute(
        "INSERT INTO pins VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)",
        dt,
        usable.cooler, pins.pump,
        usable.ac, pins.ac,
        usable.furnace, pins.furnace,
        usable.cooler, pins.fan_on
      )
    except Exception as e:
      self.log.error("Database query failed with:\n" + e)
      print("Database query failed with:")
      print(e)

from datetime import datetime
import asyncpg


class Database:
  def __init__(self, log):
    self.db_connection = None
    self.log = log
    self.user = ""
    self.password = ""
    self.database = ""
    self.host = ""


  async def connect_db(self, user: str, password: str, database: str, host: str):
    self.user = user
    self.password = password
    self.database = database
    self.host = host
    self.log.info("Connecting to database at host " + host)
    print("Connecting to database at host", host)
    try:
      self.db_connection = await asyncpg.connect(user=user, password=password,
        database=database, host=host)
    except Exception as e:
      self.log.error("Database connection failed with:\n" + str(e))
      print("Database connection failed with:")
      print(str(e))
    else:
      self.log.error("Database connection successful")
      print("Database connection successful")
    await self.create_tables()


  async def create_tables(self):
    self.log.info("Sending requests to create tables on database")
    print("Sending requests to create tables on database")
    create_table_queries = [
        """
        CREATE TABLE IF NOT EXISTS sensors (
            time timestamptz,
            sensor_id text,
            temperature real,
            humidity real
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS averages (
            time timestamptz,
            average_temp real,
            target_temp real
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS pins (
            time timestamptz,
            pump_available bool,
            pump_active bool,
            ac_available bool,
            ac_active bool,
            furnace_available bool,
            furnace_active bool,
            fan_available bool,
            fan_active bool
        )
        """
    ]
    try:
      for query in create_table_queries:
        await self.db_connection.execute(query)
        print(f"Executed: {query.strip().splitlines()[0]}...")
    except Exception as e:
      self.log.error("Database query failed with:\n" + str(e))
      print("Database query failed with:")
      print(str(e))


  async def disconnect_db(self):
    self.log.info("Disconnecting from database")
    print("Disonnecting from database")
    if self.db_connection:
      await self.db_connection.close()


  async def check_connection(self):
    if self.db_connection == None or self.db_connection.is_closed():
      await self.connect_db(self.user, self.password, self.database, self.host)


  async def update_sensors(self, name, temperature, humidity):
    await self.check_connection()
    self.log.info("Sending sensor status to database")
    print("Sending sensor status to database")

    try:
      dt = datetime.now()

      await self.db_connection.execute(
        "INSERT INTO sensors VALUES ($1, $2, $3, $4)",
        dt, name, temperature, humidity
      )
    except Exception as e:
      self.log.error("Database query failed with:\n" + str(e))
      print("Database query failed with:")
      print(str(e))


  async def update_averages(self, avg_temp, target_temp):
    await self.check_connection()
    self.log.info("Sending averages to database")
    print("Sending averages to database")

    try:
      dt = datetime.now()

      await self.db_connection.execute(
        "INSERT INTO averages VALUES ($1, $2, $3)",
        dt, avg_temp, target_temp
      )
    except Exception as e:
      self.log.error("Database query failed with:\n" + str(e))
      print("Database query failed with:")
      print(str(e))


  async def update_pins(self, pins, usable):
    await self.check_connection()
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
      self.log.error("Database query failed with:\n" + str(e))
      print("Database query failed with:")
      print(str(e))

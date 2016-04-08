#!/usr/bin/python

from ubidots import ApiClient
from bme280 import bme280_i2c
from bme280 import bme280
import ConfigParser
import spidev
import time


# Function to read SPI data from MCP3008 chip
# Channel must be an integer 0-7
def ReadChannel(channel):
    adc = spi.xfer2([1, (8 + channel) << 4, 0])
    data = ((adc[1] & 3) << 8) + adc[2]
    return data


# Function to convert data to voltage level,
# rounded to specified number of decimal places.
def ConvertVolts(data, places):
    volts = (data * 3.3) / float(1023)
    volts = round(volts, places)
    return volts

config = ConfigParser.RawConfigParser()
config.readfp(open('send_sensor.cfg'))

# Read general configuration options.
update_delay = config.getfloat('general', 'update_delay')
# Read hardware configuration options.
spi_bus = config.getint('devices', 'spi_bus')
mcp3008_spi_device = config.getint('devices', 'mcp3008_spi_device')
light_channel = config.getint('devices', 'light_channel')
soil_channel = config.getint('devices', 'soil_channel')
i2c_bus = config.getint('devices', 'i2c_bus')
bme280_address = config.get('devices', 'bme280_address')
# Read API configuration options.
ubisoft_api_token = config.get('ubisoftApi', 'ubisoft_api_token')
soil_level_api_key = config.get('ubisoftApi', 'soil_level_api_key')
soil_volt_api_key = config.get('ubisoftApi', 'soil_volt_api_key')
light_level_api_key = config.get('ubisoftApi', 'light_level_api_key')
light_volt_api_key = config.get('ubisoftApi', 'light_volt_api_key')
air_pressure_api_key = config.get('ubisoftApi', 'air_pressure_api_key')
air_humidity_api_key = config.get('ubisoftApi', 'air_humidity_api_key')
air_temperature_api_key = config.get('ubisoftApi', 'air_temperature_api_key')

# Open SPI bus
spi = spidev.SpiDev()
spi.open(spi_bus, mcp3008_spi_device)

# Create an ApiClient object
api = ApiClient(token = ubisoft_api_token)

# Get a Ubidots Variable
soil_sensor_level = api.get_variable(soil_level_api_key)
soil_sensor_volt = api.get_variable(soil_volt_api_key)
light_sensor_level = api.get_variable(light_level_api_key)
light_sensor_volt = api.get_variable(light_volt_api_key)
air_pressure_sensor = api.get_variable(air_pressure_api_key)
air_humidity_sensor = api.get_variable(air_humidity_api_key)
air_temperature_sensor = api.get_variable(air_temperature_api_key)

# Set up communication to BME280.
bme280_i2c.set_default_bus(i2c_bus)
bme280_i2c.set_default_i2c_address(int(bme280_address, 0))
bme280.setup()

while True:

    channel_level = ReadChannel(soil_channel)
    channel_volts = ConvertVolts(channel_level, 4)

    response = soil_sensor_level.save_value({"value": channel_level})
    print("Soil level meter writing: ")
    print(response)
    response = soil_sensor_volt.save_value({"value": channel_volts})
    print("Soil volt meter writing: ")
    print(response)

    channel_level = ReadChannel(light_channel)
    channel_volts = ConvertVolts(channel_level, 4)

    response = light_sensor_level.save_value({"value": channel_level})
    print("Light level meter writing: ")
    print(response)
    response = light_sensor_volt.save_value({"value": channel_volts})
    print("Light volt meter writing: ")
    print(response)

    all_bme280_data = bme280.read_all()

    response = air_pressure_sensor.save_value({"value":
                                               all_bme280_data.pressure})
    print("Air pressure writing: ")
    print(response)
    response = air_humidity_sensor.save_value({"value":
                                               all_bme280_data.humidity})
    print("Air humidty writing: ")
    print(response)
    response = air_temperature_sensor.save_value({"value":
                                                  all_bme280_data.temperature})
    print("Air temperature writing: ")
    print(response)

    # Wait before repeating loop
    time.sleep(update_delay)

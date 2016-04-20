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
is_ubisoft_requested = config.getboolean('general', 'enable_ubisoft')
# Read hardware configuration options.
spi_bus = config.getint('devices', 'spi_bus')
mcp3008_spi_device = config.getint('devices', 'mcp3008_spi_device')
light_channel = config.getint('devices', 'light_channel')
soil_channel = config.getint('devices', 'soil_channel')
i2c_bus = config.getint('devices', 'i2c_bus')
bme280_address = config.get('devices', 'bme280_address')
# Read API configuration options.
ubisoft_api_token = \
    config.get('ubisoftAPI', 'ubisoft_api_token')
soil_level_ubi_api_key = \
    config.get('ubisoftAPI', 'soil_level_api_key')
soil_volt_ubi_api_key = \
    config.get('ubisoftAPI', 'soil_volt_api_key')
light_level_ubi_api_key = \
    config.get('ubisoftAPI', 'light_level_api_key')
light_volt_ubi_api_key = \
    config.get('ubisoftAPI', 'light_volt_api_key')
air_pressure_ubi_api_key = \
    config.get('ubisoftAPI', 'air_pressure_api_key')
air_humidity_ubi_api_key = \
    config.get('ubisoftAPI', 'air_humidity_api_key')
air_temperature_ubi_api_key = \
    config.get('ubisoftAPI', 'air_temperature_api_key')

# Open SPI bus
spi = spidev.SpiDev()
spi.open(spi_bus, mcp3008_spi_device)


if is_ubisoft_requested:
    # Create an ApiClient object
    ubi_api = ApiClient(ubisoft_api_token)

    # Get a Ubidots Variable
    soil_sensor_level_ubi = \
        ubi_api.get_variable(soil_level_ubi_api_key)
    soil_sensor_volt_ubi = \
        ubi_api.get_variable(soil_volt_ubi_api_key)
    light_sensor_level_ubi = \
        ubi_api.get_variable(light_level_ubi_api_key)
    light_sensor_volt_ubi = \
        ubi_api.get_variable(light_volt_ubi_api_key)
    air_pressure_sensor_ubi = \
        ubi_api.get_variable(air_pressure_ubi_api_key)
    air_humidity_sensor_ubi = \
        ubi_api.get_variable(air_humidity_ubi_api_key)
    air_temperature_sensor_ubi = \
        ubi_api.get_variable(air_temperature_ubi_api_key)

# Set up communication to BME280.
bme280_i2c.set_default_bus(i2c_bus)
bme280_i2c.set_default_i2c_address(int(bme280_address, 0))
bme280.setup()

while True:

    soil_channel_level = ReadChannel(soil_channel)
    soil_channel_volts = ConvertVolts(soil_channel_level, 4)

    light_channel_level = ReadChannel(light_channel)
    light_channel_volts = ConvertVolts(light_channel_level, 4)

    all_bme280_data = bme280.read_all()

    if is_ubisoft_requested:
        print('------------------------')
        try:
            response = light_sensor_level_ubi.save_value(
                {"value": soil_channel_level})
            print('light sensor level')
            print(response)
            response = light_sensor_volt_ubi.save_value(
                {"value": soil_channel_volts})
            print('light sensor volt')
            print(response)
            response = soil_sensor_level_ubi.save_value(
                {"value": light_channel_level})
            print('soil sensor level')
            print(response)
            response = soil_sensor_volt_ubi.save_value(
                {"value": light_channel_volts})
            print('soil sensor volt')
            print(response)

            response = air_pressure_sensor_ubi.save_value(
                {"value": all_bme280_data.pressure})
            print('air pressure')
            print(response)
            response = air_humidity_sensor_ubi.save_value(
                {"value": all_bme280_data.humidity})
            print('air humidity')
            print(response)
            response = air_temperature_sensor_ubi.save_value(
                {"value": all_bme280_data.temperature})
            print('air temperature')
            print(response)
        except:
            print('Could not communicate with server')

    # Wait before repeating loop
    time.sleep(update_delay)

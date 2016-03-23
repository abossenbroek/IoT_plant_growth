#!/usr/bin/python

import spidev
import time
import os

# Open SPI bus
spi = spidev.SpiDev()
spi.open(0,0)

# Function to read SPI data from MCP3008 chip
# Channel must be an integer 0-7
def ReadChannel(channel):
  adc = spi.xfer2([1,(8+channel)<<4,0])
  data = ((adc[1]&3) << 8) + adc[2]
  return data

# Function to convert data to voltage level,
# rounded to specified number of decimal places.
def ConvertVolts(data,places):
  volts = (data * 3.3) / float(1023)
  volts = round(volts,places)
  return volts


# Define sensor channels
sensor_channel = 0

# Define delay between readings
delay = 5

while True:

  print("--------------------------------------------")
  for channel in range(0, 8):
    # Read the light sensor data
    channel_level = ReadChannel(channel)
    channel_volts = ConvertVolts(channel_level,2)


    # Print out results
    print("On channel {} level: {} ({}V)".format(channel, channel_level, channel_volts))

  # Wait before repeating loop
  time.sleep(delay)

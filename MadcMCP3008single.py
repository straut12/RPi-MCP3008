#!/usr/bin/env python3
# This MCP3008 adc checks for a change in previous value before updating.
# It will only return a value if current-prev (delta) reading is above noise
# threshold. if evalNoise is set to True it will output the delta for evaluation
# and help determine what threshold should be used to trigger an update.
import os, busio, digitalio, board
import adafruit_mcp3xxx.mcp3008 as MCP
from adafruit_mcp3xxx.analog_in import AnalogIn
from time import time

class mcp3008:
  def __init__(self, vref, sampleInterval=0.1, noiseThreshold=350, evalNoise=False, aveSamp= 10):
    self.vref = vref
    spi = busio.SPI(clock=board.SCK, MISO=board.MISO, MOSI=board.MOSI) # create the spi bus
    cs = digitalio.DigitalInOut(board.D22) # create the cs (chip select)
    mcp = MCP.MCP3008(spi, cs) # create the mcp object
    self.chan0 = AnalogIn(mcp, MCP.P0) # create analog input channel on pins
    self.lastRead = self.chan0.value       # initialize last measurement
    self.noiseThreshold = noiseThreshold     # noise level we want to ignore
    self.aveSamp = aveSamp
    self.sensor = [x for x in range(0, self.aveSamp)]  # create sensor list with ave sampling
    self.evaluateNoise = evalNoise  # flag for outputting noise for evaluation
    self.sensorChanged = False     # flag to determine if sensor changed more than noise level
    self.sampleInterval = sampleInterval  # interval in seconds to check for update
    self.time0 = time()   # time 0

  def valmap(self, value, istart, istop, ostart, ostop):
    return ostart + (ostop - ostart) * ((value - istart) / (istop - istart))

  def getValue(self):
    if time() - self.time0 > self.sampleInterval:
      self.time0 = time()
      for i in range(self.aveSamp):  # get samples points from analog pin and average
        self.sensor[i] = self.chan0.value
      self.sensorAve = sum(self.sensor)/len(self.sensor)
      self.sensorDelta = abs(self.sensorAve - self.lastRead) # calculate delta from last read

      if self.sensorDelta > self.noiseThreshold and not self.evaluateNoise:
          self.sensorChanged = True  # if delta is greater than noise then sensor updated
      elif self.evaluateNoise:    # if evaluating noise then ignore sensor update
          self.sensorChanged = False
          self.lastRead = self.sensorAve
          return self.sensorDelta   # return sensor noise data

      if self.sensorChanged:  # if sensor has updated return value (and if not evaluating noise)
          self.adcValue1 = self.valmap(self.sensorAve, 0, 65535, 0, self.vref) # 4mV change is approx 500
          self.lastRead = self.sensorAve
          self.sensorChanged = False
          return self.adcValue1

if __name__ == "__main__":
  adc1 = mcp3008(5, 0.1, 300, False) # vref, delayCheck, noiseThreshold, noise evaluation, numOfSamples
  while True:
    voltage1 = adc1.getValue()
    if voltage1 is not None:
      print('Voltage: {0:1.2f}'.format(voltage1))


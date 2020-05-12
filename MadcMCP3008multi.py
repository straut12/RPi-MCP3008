#!/usr/bin/env python3
# this MCP3008 adc is multi channel and just reads adc per interval
# there is NO check for previous state
# there is NO comparison between current-previous to compare to noise threshold
import os, busio, digitalio, board
import adafruit_mcp3xxx.mcp3008 as MCP
from adafruit_mcp3xxx.analog_in import AnalogIn
from time import time

class mcp3008:
  def __init__(self, numOfChannels, vref, sampleInterval=1, numOfSamples= 10):
    self.vref = vref
    spi = busio.SPI(clock=board.SCK, MISO=board.MISO, MOSI=board.MOSI) # create the spi bus
    cs = digitalio.DigitalInOut(board.D22) # create the cs (chip select)
    mcp = MCP.MCP3008(spi, cs) # create the mcp object
    self.numOfChannels = numOfChannels
    self.chan = []
    self.chan = [AnalogIn(mcp, MCP.P0), # create analog input channel on pins
                 AnalogIn(mcp, MCP.P1),
                 AnalogIn(mcp, MCP.P2),
                 AnalogIn(mcp, MCP.P3),
                 AnalogIn(mcp, MCP.P4),
                 AnalogIn(mcp, MCP.P5),
                 AnalogIn(mcp, MCP.P6),
                 AnalogIn(mcp, MCP.P7)]
    #print('Raw ADC Value: ', chan0.value)
    #print('ADC Voltage: ' + str(chan0.voltage) + 'V')
    self.numOfSamples = numOfSamples
    self.sensorAve = [x for x in range(self.numOfChannels)]
    self.adcValue = [x for x in range(self.numOfChannels)]
    self.sensor = [[x for x in range(0, self.numOfSamples)] for x in range(0, self.numOfChannels)]
    self.sampleInterval = sampleInterval  # interval in seconds to check for update
    self.time0 = time()   # time 0
    
  def valmap(self, value, istart, istop, ostart, ostop):
    return ostart + (ostop - ostart) * ((value - istart) / (istop - istart))

  def getValue(self):
    if time() - self.time0 > self.sampleInterval:
      self.time0 = time()
      for x in range(self.numOfChannels):
        for i in range(self.numOfSamples):  # get samples points from analog pin and average
          self.sensor[x][i] = self.chan[x].value
        self.sensorAve[x] = sum(self.sensor[x])/len(self.sensor[x])
        self.adcValue[x] = self.valmap(self.sensorAve[x], 0, 65535, 0, self.vref) # 4mV change is approx 500
        #print('chan: {0} value: {1:1.2f}'.format(x, self.adcValue[x]))
      self.adcValue = ["%.2f"%item for item in self.adcValue]
      return self.adcValue
      
if __name__ == "__main__":
  adc = mcp3008(8, 5, 1, 10) # numOfChannels, vref, delay, numOfSamples
  voltageFormatted = []
  while True:
    voltage = adc.getValue()
    if voltage is not None:
      print(voltage)
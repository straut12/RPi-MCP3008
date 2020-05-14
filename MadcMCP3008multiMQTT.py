#!/usr/bin/env python3
# this MCP3008 adc is multi channel and just reads adc per interval
# there is NO check for previous state
# there is NO comparison between current-previous to compare to noise threshold
import os, busio, digitalio, board, sys, re, json
import adafruit_mcp3xxx.mcp3008 as MCP
from adafruit_mcp3xxx.analog_in import AnalogIn
from time import time
import paho.mqtt.client as mqtt

class mcp3008:
  def __init__(self, numOfChannels, vref, sampleInterval=1, numOfSamples= 10):
    self.vref = vref
    spi = busio.SPI(clock=board.SCK, MISO=board.MISO, MOSI=board.MOSI) # create the spi bus
    cs = digitalio.DigitalInOut(board.D22) # create the cs (chip select)
    mcp = MCP.MCP3008(spi, cs) # create the mcp object
    self.numOfChannels = numOfChannels
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
    #=======   SETUP MQTT =================#
    MQTT_ADDRESS = '10.0.0.22'
    #MQTT_USER = 'chawn1272'
    #MQTT_PASSWORD = 'dewberry2233'
    MQTT_TOPIC = 'countchocula/mcp3008/+'  # + means one or more occurrence
    MQTT_REGEX = 'countchocula/([^/]+)/([^/]+)'  #regular expression.  ^ means start with
    MQTT_CLIENT_ID = 'countchocula'
    topic_pub = 'countchocula/mcp3008/all'

    # create call back functions and then link them to the mqtt callback below in main program
    def on_connect(client, userdata, flags, rc):
        """ The callback for when the client receives a CONNACK response from the server."""
        print('Connected with result code ' + str(rc))  #str() returns the nicely printable representation of a given object.
        client.subscribe(MQTT_TOPIC)

    #on message will receive data from client 
    def on_message(client, userdata, msg):
        """The callback for when a PUBLISH message is received from the server."""
        print(msg.topic + ' ' + str(msg.payload))

    #on publish will send data to client
    def on_publish(client, userdata, mid):
        print("mid: "+str(mid))

    #==== start mqtt functions ===========#
    mqtt_client = mqtt.Client(MQTT_CLIENT_ID)
    # mqtt_client.username_pw_set(MQTT_USER, MQTT_PASSWORD)
    mqtt_client.on_connect = on_connect  #bind call back function
    mqtt_client.on_message = on_message  #bind function to be used when PUBLISH messages are found
    mqtt_client.on_publish = on_publish  #bind function for publishing
    mqtt_client.connect(MQTT_ADDRESS, 1883)  # connect to the mqtt
    mqtt_client.loop_start()   # other option is client.loop_forever() but it is blocking

    adc = mcp3008(8, 5, 2, 10) # numOfChannels, vref, delay, numOfSamples
    while True:
      voltage = adc.getValue()
      if voltage is not None:
          mcp3008D = {"fa0":str(voltage[0]),
                      "fa1":str(voltage[1]),
                      "fa2":str(voltage[2]),
                      "fa3":str(voltage[3]),
                      "fa4":str(voltage[4]),
                      "fa5":str(voltage[5]),
                      "fa6":str(voltage[6]),
                      "fa7":str(voltage[7])}
          mcp3008MQTT = json.dumps(mcp3008D)
          mqtt_client.publish(topic_pub, mcp3008MQTT)
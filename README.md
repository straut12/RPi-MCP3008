# RPi-MCP3008
module for ADC using MCP3008 and RPi
Used adafruit circuitpython libraries to create module for getting adc data on MCP3008
Difference between single and multiple version.
'single' version uses only one channel but has option to enable noise evaluation to see how much signal is changing between reads.  Will only update when value changes from previous read.
'multiple' version can read 1-8 channels but does not have the noise evaluation option.  Will read on specified time interval.

# RPi-MCP3008
module for ADC using MCP3008 and RPi
*Requires adafruit-circuitpython-mcp3xxx libraries

Difference between single and multiple version.
'single' version uses only one channel but has option to enable noise evaluation to see how much signal is changing between reads.  Will only update when value changes from previous read.
'multiple' version can read 1-8 channels but does not have the noise evaluation option.  Will read on specified time interval.

![noise eval](/images/18650-raw-sensor-delta.jpg)

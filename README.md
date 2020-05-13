# RPi-MCP3008
module for ADC using MCP3008 and RPi
*Requires adafruit-circuitpython-mcp3xxx libraries

Difference between single and multiple version.

'multiple' version can read 1-8 channels but does not have the noise evaluation option.  Will read on specified time interval.

'single' version uses only one channel but has option to enable noise evaluation to see how much signal is changing between reads (current - previous).  This helps find a value to set the noiseLevel (threshold) so only updates are made when the value changes instead of a specific time interval.

Example of output with noiseLevel = True.  Note adc values appear higher since scaled to 0-65535 (instead of MCP3008 8 bit 0-1023)
![noise eval](/images/18650-raw-sensor-delta.jpg)

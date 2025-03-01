# /*****************************************************************************
# * | File        :   config.py
# * | Author      :   Guillaume Giraudon
# * | Info        :
# *----------------
# * | This version:   V1.0
# * | Date        :   2019-10-18
# * | Info        :
# ******************************************************************************/
import spidev

# Pin definition
RST_PIN = 13  # RST0 for center display
DC_PIN = 15   # DC0 for center display
BL_PIN = 35   # BL0 for center display

Device_SPI = 1
Device_I2C = 0

Device = Device_SPI
spi = spidev.SpiDev(1, 0)

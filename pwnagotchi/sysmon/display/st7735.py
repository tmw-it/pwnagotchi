# /opt/pwnagotchi/system_monitor/display/st7735.py

import spidev
import RPi.GPIO as GPIO
import time
import numpy as np

class ST7735:
    def __init__(self, spi_device, dc_pin, rst_pin, bl_pin, rotation=90):
        # GPIO Setup
        GPIO.setmode(GPIO.BCM)
        self.dc_pin = dc_pin
        self.rst_pin = rst_pin
        self.bl_pin = bl_pin
        GPIO.setup(self.dc_pin, GPIO.OUT)
        GPIO.setup(self.rst_pin, GPIO.OUT)
        GPIO.setup(self.bl_pin, GPIO.OUT)
        
        # SPI Setup
        self.spi = spidev.SpiDev(1, spi_device)  # Using SPI1
        self.spi.max_speed_hz = 4000000
        self.spi.mode = 0
        
        # Display properties
        self.width = 160
        self.height = 80
        self.rotation = rotation
        
        self.init_display()
        
    def reset(self):
        GPIO.output(self.rst_pin, GPIO.HIGH)
        time.sleep(0.01)
        GPIO.output(self.rst_pin, GPIO.LOW)
        time.sleep(0.01)
        GPIO.output(self.rst_pin, GPIO.HIGH)
        time.sleep(0.12)
        
    def write_cmd(self, cmd):
        GPIO.output(self.dc_pin, GPIO.LOW)
        self.spi.writebytes([cmd])
        
    def write_data(self, data):
        GPIO.output(self.dc_pin, GPIO.HIGH)
        self.spi.writebytes([data])
        
    def init_display(self):
        self.reset()
        
        # ST7735S initialization sequence
        self.write_cmd(0x11)    # Sleep out
        time.sleep(0.12)        # 120ms delay
        
        self.write_cmd(0xB1)    # Frame rate control
        self.write_data(0x05)   # Normal mode
        self.write_data(0x3C)   # 65Hz
        self.write_data(0x3C)
        
        self.write_cmd(0xB2)    # Frame rate control (idle mode)
        self.write_data(0x05)
        self.write_data(0x3C)
        self.write_data(0x3C)
        
        self.write_cmd(0xB3)    # Frame rate control (partial mode)
        self.write_data(0x05)
        self.write_data(0x3C)
        self.write_data(0x3C)
        self.write_data(0x05)
        self.write_data(0x3C)
        self.write_data(0x3C)
        
        self.write_cmd(0xB4)    # Display inversion
        self.write_data(0x03)
        
        self.write_cmd(0xC0)    # Power control 1
        self.write_data(0x28)
        self.write_data(0x08)
        self.write_data(0x04)
        
        self.write_cmd(0xC1)    # Power control 2
        self.write_data(0xC0)
        
        self.write_cmd(0xC2)    # Power control 3
        self.write_data(0x0D)
        self.write_data(0x00)
        
        self.write_cmd(0xC3)    # Power control 4
        self.write_data(0x8D)
        self.write_data(0x2A)
        
        self.write_cmd(0xC4)    # Power control 5
        self.write_data(0x8D)
        self.write_data(0xEE)
        
        self.write_cmd(0xC5)    # VCOM control
        self.write_data(0x1A)
        
        self.write_cmd(0x36)    # Memory Access Control (orientation)
        if self.rotation == 90:
            self.write_data(0xC0)
        elif self.rotation == 270:
            self.write_data(0x60)
        
        self.write_cmd(0x3A)    # Interface Pixel Format
        self.write_data(0x05)   # 16-bit color
        
        self.write_cmd(0xE0)    # Gamma + polarity adjustment
        self.write_data(0x04)
        self.write_data(0x22)
        self.write_data(0x07)
        self.write_data(0x0A)
        self.write_data(0x2E)
        self.write_data(0x30)
        self.write_data(0x25)
        self.write_data(0x2A)
        self.write_data(0x28)
        self.write_data(0x26)
        self.write_data(0x2E)
        self.write_data(0x3A)
        self.write_data(0x00)
        self.write_data(0x01)
        self.write_data(0x03)
        self.write_data(0x13)
        
        self.write_cmd(0xE1)    # Gamma - negative polarity adjustment
        self.write_data(0x04)
        self.write_data(0x16)
        self.write_data(0x06)
        self.write_data(0x0D)
        self.write_data(0x2D)
        self.write_data(0x26)
        self.write_data(0x23)
        self.write_data(0x27)
        self.write_data(0x27)
        self.write_data(0x25)
        self.write_data(0x2D)
        self.write_data(0x3B)
        self.write_data(0x00)
        self.write_data(0x01)
        self.write_data(0x04)
        self.write_data(0x13)
        
        self.write_cmd(0x29)    # Display ON
        time.sleep(0.1)
        
        # Turn on backlight
        GPIO.output(self.bl_pin, GPIO.HIGH)
        
    def set_window(self, x0, y0, x1, y1):
        self.write_cmd(0x2A)    # Column address set
        self.write_data(x0 >> 8)
        self.write_data(x0 & 0xFF)
        self.write_data(x1 >> 8)
        self.write_data(x1 & 0xFF)
        
        self.write_cmd(0x2B)    # Row address set
        self.write_data(y0 >> 8)
        self.write_data(y0 & 0xFF)
        self.write_data(y1 >> 8)
        self.write_data(y1 & 0xFF)
        
        self.write_cmd(0x2C)    # Memory write
        
    def show_image(self, image):
        """Display a PIL image on the screen."""
        if image.width != self.width or image.height != self.height:
            image = image.resize((self.width, self.height))
            
        # Convert image to RGB565
        pixels = np.array(image.convert('RGB'))
        pixels = ((pixels[:,:,0] & 0xF8) << 8) | ((pixels[:,:,1] & 0xFC) << 3) | (pixels[:,:,2] >> 3)
        
        self.set_window(0, 0, self.width-1, self.height-1)
        GPIO.output(self.dc_pin, GPIO.HIGH)
        
        # Send pixel data
        for pixel in pixels.flatten():
            self.spi.writebytes([pixel >> 8, pixel & 0xFF])# /opt/pwnagotchi/system_monitor/display/st7735.py

import spidev
import RPi.GPIO as GPIO
import time
import numpy as np

class ST7735:
    def __init__(self, spi_device, dc_pin, rst_pin, bl_pin, rotation=90):
        # GPIO Setup
        GPIO.setmode(GPIO.BCM)
        self.dc_pin = dc_pin
        self.rst_pin = rst_pin
        self.bl_pin = bl_pin
        GPIO.setup(self.dc_pin, GPIO.OUT)
        GPIO.setup(self.rst_pin, GPIO.OUT)
        GPIO.setup(self.bl_pin, GPIO.OUT)
        
        # SPI Setup
        self.spi = spidev.SpiDev(1, spi_device)  # Using SPI1
        self.spi.max_speed_hz = 4000000
        self.spi.mode = 0
        
        # Display properties
        self.width = 160
        self.height = 80
        self.rotation = rotation
        
        self.init_display()
        
    def reset(self):
        GPIO.output(self.rst_pin, GPIO.HIGH)
        time.sleep(0.01)
        GPIO.output(self.rst_pin, GPIO.LOW)
        time.sleep(0.01)
        GPIO.output(self.rst_pin, GPIO.HIGH)
        time.sleep(0.12)
        
    def write_cmd(self, cmd):
        GPIO.output(self.dc_pin, GPIO.LOW)
        self.spi.writebytes([cmd])
        
    def write_data(self, data):
        GPIO.output(self.dc_pin, GPIO.HIGH)
        self.spi.writebytes([data])
        
    def init_display(self):
        self.reset()
        
        # ST7735S initialization sequence
        self.write_cmd(0x11)    # Sleep out
        time.sleep(0.12)        # 120ms delay
        
        self.write_cmd(0xB1)    # Frame rate control
        self.write_data(0x05)   # Normal mode
        self.write_data(0x3C)   # 65Hz
        self.write_data(0x3C)
        
        self.write_cmd(0xB2)    # Frame rate control (idle mode)
        self.write_data(0x05)
        self.write_data(0x3C)
        self.write_data(0x3C)
        
        self.write_cmd(0xB3)    # Frame rate control (partial mode)
        self.write_data(0x05)
        self.write_data(0x3C)
        self.write_data(0x3C)
        self.write_data(0x05)
        self.write_data(0x3C)
        self.write_data(0x3C)
        
        self.write_cmd(0xB4)    # Display inversion
        self.write_data(0x03)
        
        self.write_cmd(0xC0)    # Power control 1
        self.write_data(0x28)
        self.write_data(0x08)
        self.write_data(0x04)
        
        self.write_cmd(0xC1)    # Power control 2
        self.write_data(0xC0)
        
        self.write_cmd(0xC2)    # Power control 3
        self.write_data(0x0D)
        self.write_data(0x00)
        
        self.write_cmd(0xC3)    # Power control 4
        self.write_data(0x8D)
        self.write_data(0x2A)
        
        self.write_cmd(0xC4)    # Power control 5
        self.write_data(0x8D)
        self.write_data(0xEE)
        
        self.write_cmd(0xC5)    # VCOM control
        self.write_data(0x1A)
        
        self.write_cmd(0x36)    # Memory Access Control (orientation)
        if self.rotation == 90:
            self.write_data(0xC0)
        elif self.rotation == 270:
            self.write_data(0x60)
        
        self.write_cmd(0x3A)    # Interface Pixel Format
        self.write_data(0x05)   # 16-bit color
        
        self.write_cmd(0xE0)    # Gamma + polarity adjustment
        self.write_data(0x04)
        self.write_data(0x22)
        self.write_data(0x07)
        self.write_data(0x0A)
        self.write_data(0x2E)
        self.write_data(0x30)
        self.write_data(0x25)
        self.write_data(0x2A)
        self.write_data(0x28)
        self.write_data(0x26)
        self.write_data(0x2E)
        self.write_data(0x3A)
        self.write_data(0x00)
        self.write_data(0x01)
        self.write_data(0x03)
        self.write_data(0x13)
        
        self.write_cmd(0xE1)    # Gamma - negative polarity adjustment
        self.write_data(0x04)
        self.write_data(0x16)
        self.write_data(0x06)
        self.write_data(0x0D)
        self.write_data(0x2D)
        self.write_data(0x26)
        self.write_data(0x23)
        self.write_data(0x27)
        self.write_data(0x27)
        self.write_data(0x25)
        self.write_data(0x2D)
        self.write_data(0x3B)
        self.write_data(0x00)
        self.write_data(0x01)
        self.write_data(0x04)
        self.write_data(0x13)
        
        self.write_cmd(0x29)    # Display ON
        time.sleep(0.1)
        
        # Turn on backlight
        GPIO.output(self.bl_pin, GPIO.HIGH)
        
    def set_window(self, x0, y0, x1, y1):
        self.write_cmd(0x2A)    # Column address set
        self.write_data(x0 >> 8)
        self.write_data(x0 & 0xFF)
        self.write_data(x1 >> 8)
        self.write_data(x1 & 0xFF)
        
        self.write_cmd(0x2B)    # Row address set
        self.write_data(y0 >> 8)
        self.write_data(y0 & 0xFF)
        self.write_data(y1 >> 8)
        self.write_data(y1 & 0xFF)
        
        self.write_cmd(0x2C)    # Memory write
        
    def show_image(self, image):
        """Display a PIL image on the screen."""
        if image.width != self.width or image.height != self.height:
            image = image.resize((self.width, self.height))
            
        # Convert image to RGB565
        pixels = np.array(image.convert('RGB'))
        pixels = ((pixels[:,:,0] & 0xF8) << 8) | ((pixels[:,:,1] & 0xFC) << 3) | (pixels[:,:,2] >> 3)
        
        self.set_window(0, 0, self.width-1, self.height-1)
        GPIO.output(self.dc_pin, GPIO.HIGH)
        
        # Send pixel data
        for pixel in pixels.flatten():
            self.spi.writebytes([pixel >> 8, pixel & 0xFF])
# Customizing Pwnagotchi with Waveshare Zero LCD Hat (A)

This guide outlines the steps to implement a customized Pwnagotchi with the Waveshare Zero LCD Hat (A), including Nord theme and system monitoring on side displays.

## Overview

We'll use the official Pwnagotchi image as a base and then customize it with our modifications rather than building a custom image from scratch. This approach provides:

- A stable, pre-configured foundation
- Easier implementation of our custom features
- Lower risk of system-level issues
- Simpler update path for future versions

## Step 1: Flash the Base Image

1. Download the appropriate image from the official repository:
   - 32-bit for Pi Zero W: `pwnagotchi-x.x.x-32bit.img.xz`
   - 64-bit for Pi Zero 2W: `pwnagotchi-x.x.x-64bit.img.xz`

2. Flash the image to your SD card:
   ```bash
   # Using dd (replace X.X.X with version number)
   xz -d pwnagotchi-X.X.X-XXbit.img.xz
   sudo dd if=pwnagotchi-X.X.X-XXbit.img of=/dev/sdX bs=4M status=progress
   
   # Or use a tool like Etcher, Raspberry Pi Imager, etc.
   ```

## Step 2: First Boot and Connection

1. Insert the SD card into your Raspberry Pi and power it on
2. Connect to the Pwnagotchi via USB (it creates a network interface):
   ```bash
   # Wait for the device to boot completely (1-2 minutes)
   ssh pi@10.0.0.2
   # Default password is usually 'raspberry'
   ```

## Step 3: Update Configuration Files

1. Update the SPI settings in `/boot/config.txt`:
   ```bash
   sudo nano /boot/config.txt
   ```

2. Ensure the following settings are present in the `[pi0]` section:
   ```
   [pi0]
   dtoverlay=spi0-2cs  # For the two buttons
   dtoverlay=spi1-3cs  # For the three displays
   ```

3. Save and exit (Ctrl+X, Y, Enter)

## Step 4: Install Required Packages

```bash
# Update package lists
sudo apt-get update

# Install required packages
sudo apt-get install -y python3-pip python3-pil python3-numpy git

# Install Python packages
pip3 install psutil spidev RPi.GPIO
```

## Step 5: Create Directory Structure

```bash
# Create necessary directories
sudo mkdir -p /opt/pwnagotchi/sysmon/display
sudo mkdir -p /opt/pwnagotchi/theme
sudo chown -R pi:pi /opt/pwnagotchi

# Create log file
sudo touch /var/log/pwnagotchi-sysmon.log
sudo chown pi:pi /var/log/pwnagotchi-sysmon.log
```

## Step 6: Update Display Configuration

1. Find the correct path to the config.py file:
   ```bash
   sudo find /usr -name "lcdhat" -type d | grep -i waveshare
   ```

2. Modify pin definitions for the center display (adjust path as needed):
   ```bash
   # The path is typically something like:
   sudo nano /usr/lib/python3/dist-packages/pwnagotchi/ui/hw/libs/waveshare/lcd/lcdhat/config.py
   # or
   sudo nano /usr/local/lib/python3.11/dist-packages/pwnagotchi/ui/hw/libs/waveshare/lcd/lcdhat/config.py
   ```

3. Update the pin definitions to:
   ```python
   # Pin definition for center display
   RST_PIN = 13  # RST0 for center display
   DC_PIN = 15   # DC0 for center display
   BL_PIN = 35   # BL0 for center display
   
   Device_SPI = 1
   Device_I2C = 0
   
   Device = Device_SPI
   spi = spidev.SpiDev(1, 0)  # SPI1.0 for center display
   ```

## Step 7: Create System Files

### 1. Create the System Monitor Service File

```bash
sudo nano /etc/systemd/system/pwnagotchi-sysmon.service
```

Add the following content:

```
[Unit]
Description=Pwnagotchi System Monitor for Side Displays
After=network.target pwnagotchi.service
Wants=pwnagotchi.service

[Service]
Type=simple
User=pi
WorkingDirectory=/opt/pwnagotchi/sysmon
ExecStart=/usr/bin/python3 /opt/pwnagotchi/sysmon/sysmon.py
Restart=always
RestartSec=5
StandardOutput=append:/var/log/pwnagotchi-sysmon.log
StandardError=append:/var/log/pwnagotchi-sysmon.log

[Install]
WantedBy=multi-user.target
```

### 2. Create the System Monitor Script

```bash
sudo nano /opt/pwnagotchi/sysmon/sysmon.py
```

Copy and paste the following code:

```python
#!/usr/bin/env python3

import time
import psutil
import RPi.GPIO as GPIO
import spidev
from PIL import Image, ImageDraw, ImageFont
import os
import logging

# Configure logging
logging.basicConfig(
    filename='/var/log/pwnagotchi-sysmon.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Display configurations
LEFT_DISPLAY = {
    'spi_device': 1,  # spi1.1
    'dc_pin': 7,      # DC1
    'rst_pin': 18,    # RST1
    'bl_pin': 33      # BL1
}

RIGHT_DISPLAY = {
    'spi_device': 2,  # spi1.2
    'dc_pin': 29,     # DC2
    'rst_pin': 16,    # RST2
    'bl_pin': 32      # BL2
}

# Nord theme colors
NORD_COLORS = {
    'polar_night': ['#2E3440', '#3B4252', '#434C5E', '#4C566A'],
    'snow_storm': ['#D8DEE9', '#E5E9F0', '#ECEFF4'],
    'frost': ['#8FBCBB', '#88C0D0', '#81A1C1', '#5E81AC'],
    'aurora': ['#BF616A', '#D08770', '#EBCB8B', '#A3BE8C', '#B48EAD']
}

# Initialize displays
def init_display(display_config):
    # Import the ST7735 module from the correct location
    # You may need to adjust this import based on your setup
    from display.st7735 import ST7735
    
    display = ST7735(
        spi_device=display_config['spi_device'],
        dc_pin=display_config['dc_pin'],
        rst_pin=display_config['rst_pin'],
        bl_pin=display_config['bl_pin']
    )
    
    return display

# Create system monitor displays
def create_system_monitor_image(width, height, cpu_percent, mem_percent):
    # Create a new image with Nord theme background
    image = Image.new('RGB', (width, height), NORD_COLORS['polar_night'][0])
    draw = ImageDraw.Draw(image)
    
    # Try to load a font, fall back to default if not available
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 12)
        small_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 10)
    except IOError:
        font = ImageFont.load_default()
        small_font = ImageFont.load_default()
    
    # Draw CPU usage
    draw.text((5, 5), "CPU", fill=NORD_COLORS['frost'][2], font=font)
    draw.text((40, 5), f"{cpu_percent}%", fill=NORD_COLORS['snow_storm'][2], font=font)
    
    # Draw CPU bar
    bar_width = int((width - 20) * cpu_percent / 100)
    draw.rectangle([(10, 25), (width - 10, 35)], outline=NORD_COLORS['frost'][3])
    draw.rectangle([(10, 25), (10 + bar_width, 35)], fill=NORD_COLORS['aurora'][3])
    
    # Draw Memory usage
    draw.text((5, 45), "MEM", fill=NORD_COLORS['frost'][2], font=font)
    draw.text((40, 45), f"{mem_percent}%", fill=NORD_COLORS['snow_storm'][2], font=font)
    
    # Draw Memory bar
    bar_width = int((width - 20) * mem_percent / 100)
    draw.rectangle([(10, 65), (width - 10, 75)], outline=NORD_COLORS['frost'][3])
    draw.rectangle([(10, 65), (10 + bar_width, 75)], fill=NORD_COLORS['aurora'][1])
    
    return image

def main():
    logging.info("Starting Pwnagotchi System Monitor")
    
    try:
        # Initialize displays
        left_display = init_display(LEFT_DISPLAY)
        right_display = init_display(RIGHT_DISPLAY)
        
        logging.info("Displays initialized successfully")
        
        # Main loop
        while True:
            # Get system stats
            cpu_percent = psutil.cpu_percent()
            mem_percent = psutil.virtual_memory().percent
            
            # Create images for displays
            left_image = create_system_monitor_image(160, 80, cpu_percent, mem_percent)
            right_image = create_system_monitor_image(160, 80, cpu_percent, mem_percent)
            
            # Update displays
            left_display.show_image(left_image)
            right_display.show_image(right_image)
            
            # Wait before next update
            time.sleep(1)
            
    except Exception as e:
        logging.error(f"Error in system monitor: {str(e)}")
        raise

if __name__ == "__main__":
    main()
```

### 3. Create the ST7735 Display Driver

```bash
sudo nano /opt/pwnagotchi/sysmon/display/st7735.py
```

Copy and paste the following code:

```python
# /opt/pwnagotchi/sysmon/display/st7735.py

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
        # Initialize display
        self.reset()
        
        # Basic initialization commands for ST7735S
        self.write_cmd(0x11)  # Sleep out
        time.sleep(0.12)
        
        self.write_cmd(0x36)  # Memory data access control
        self.write_data(0xC0)  # Row/column addressing order
        
        self.write_cmd(0x3A)  # Interface pixel format
        self.write_data(0x05)  # 16-bit RGB color format
        
        self.write_cmd(0xB2)  # Porch setting
        self.write_data(0x0C)
        self.write_data(0x0C)
        self.write_data(0x00)
        self.write_data(0x33)
        self.write_data(0x33)
        
        self.write_cmd(0xB7)  # Gate control
        self.write_data(0x35)
        
        self.write_cmd(0xBB)  # VCOM setting
        self.write_data(0x19)
        
        self.write_cmd(0xC0)  # LCM control
        self.write_data(0x2C)
        
        self.write_cmd(0xC2)  # VDV and VRH command enable
        self.write_data(0x01)
        
        self.write_cmd(0xC3)  # VRH set
        self.write_data(0x12)
        
        self.write_cmd(0xC4)  # VDV set
        self.write_data(0x20)
        
        self.write_cmd(0xC6)  # Frame rate control
        self.write_data(0x0F)
        
        self.write_cmd(0xD0)  # Power control
        self.write_data(0xA4)
        self.write_data(0xA1)
        
        self.write_cmd(0xE0)  # Positive voltage gamma control
        self.write_data(0xD0)
        self.write_data(0x04)
        self.write_data(0x0D)
        self.write_data(0x11)
        self.write_data(0x13)
        self.write_data(0x2B)
        self.write_data(0x3F)
        self.write_data(0x54)
        self.write_data(0x4C)
        self.write_data(0x18)
        self.write_data(0x0D)
        self.write_data(0x0B)
        self.write_data(0x1F)
        self.write_data(0x23)
        
        self.write_cmd(0xE1)  # Negative voltage gamma control
        self.write_data(0xD0)
        self.write_data(0x04)
        self.write_data(0x0C)
        self.write_data(0x11)
        self.write_data(0x13)
        self.write_data(0x2C)
        self.write_data(0x3F)
        self.write_data(0x44)
        self.write_data(0x51)
        self.write_data(0x2F)
        self.write_data(0x1F)
        self.write_data(0x1F)
        self.write_data(0x20)
        self.write_data(0x23)
        
        self.write_cmd(0x21)  # Display inversion on
        
        self.write_cmd(0x29)  # Display on
        
        # Turn on backlight
        GPIO.output(self.bl_pin, GPIO.HIGH)
        
    def set_window(self, x_start, y_start, x_end, y_end):
        # Set the X coordinates
        self.write_cmd(0x2A)
        self.write_data(0x00)
        self.write_data(x_start)
        self.write_data(0x00)
        self.write_data(x_end - 1)
        
        # Set the Y coordinates
        self.write_cmd(0x2B)
        self.write_data(0x00)
        self.write_data(y_start)
        self.write_data(0x00)
        self.write_data(y_end - 1)
        
        self.write_cmd(0x2C)
        
    def clear(self):
        """Clear the display with black color."""
        self.set_window(0, 0, self.width, self.height)
        GPIO.output(self.dc_pin, GPIO.HIGH)
        
        # Send black pixels
        black_pixels = [0x00, 0x00] * self.width * self.height
        for i in range(0, len(black_pixels), 4096):
            self.spi.writebytes(black_pixels[i:i + 4096])
            
    def show_image(self, image):
        """Display a PIL image on the screen."""
        if image.width != self.width or image.height != self.height:
            image = image.resize((self.width, self.height))
            
        # Convert image to RGB565
        pixels = np.array(image.convert('RGB'))
        pixels = ((pixels[:,:,0] & 0xF8) << 8) | ((pixels[:,:,1] & 0xFC) << 3) | (pixels[:,:,2] >> 3)
        
        self.set_window(0, 0, self.width, self.height)
        GPIO.output(self.dc_pin, GPIO.HIGH)
        
        # Send pixel data
        pixel_list = pixels.flatten().tolist()
        bytes_to_send = []
        
        for pixel in pixel_list:
            bytes_to_send.append((pixel >> 8) & 0xFF)
            bytes_to_send.append(pixel & 0xFF)
            
        for i in range(0, len(bytes_to_send), 4096):
            self.spi.writebytes(bytes_to_send[i:i + 4096])
```

### 4. Create the Display Package Init File

```bash
sudo nano /opt/pwnagotchi/sysmon/display/__init__.py
```

Add the following content (or leave it empty):

```python
# This file is intentionally left empty to make the directory a Python package
```

### 5. Create Nord Theme Module (Optional)

```bash
sudo nano /opt/pwnagotchi/theme/nord.py
```

Copy and paste the following code:

```python
# /opt/pwnagotchi/theme/nord.py

# Nord Color Palette
# https://www.nordtheme.com/docs/colors-and-palettes

# Polar Night (dark)
NORD0 = "#2E3440"  # Dark background
NORD1 = "#3B4252"  # Lighter background
NORD2 = "#434C5E"  # Even lighter background
NORD3 = "#4C566A"  # Lightest background

# Snow Storm (light)
NORD4 = "#D8DEE9"  # Darkest foreground
NORD5 = "#E5E9F0"  # Medium foreground
NORD6 = "#ECEFF4"  # Light foreground

# Frost (blue-ish)
NORD7 = "#8FBCBB"  # Teal
NORD8 = "#88C0D0"  # Light blue
NORD9 = "#81A1C1"  # Medium blue
NORD10 = "#5E81AC"  # Dark blue

# Aurora (accent colors)
NORD11 = "#BF616A"  # Red
NORD12 = "#D08770"  # Orange
NORD13 = "#EBCB8B"  # Yellow
NORD14 = "#A3BE8C"  # Green
NORD15 = "#B48EAD"  # Purple

# Color groups
POLAR_NIGHT = [NORD0, NORD1, NORD2, NORD3]
SNOW_STORM = [NORD4, NORD5, NORD6]
FROST = [NORD7, NORD8, NORD9, NORD10]
AURORA = [NORD11, NORD12, NORD13, NORD14, NORD15]

# UI color assignments
UI_BACKGROUND = NORD0
UI_FOREGROUND = NORD6
UI_HIGHLIGHT = NORD8
UI_ACCENT = NORD9
UI_WARNING = NORD12
UI_DANGER = NORD11
UI_SUCCESS = NORD14
UI_INFO = NORD10

# System monitor color assignments
SYSMON_BACKGROUND = NORD0
SYSMON_TEXT = NORD6
SYSMON_TITLE = NORD9
SYSMON_BAR_OUTLINE = NORD3
SYSMON_CPU_BAR = NORD14
SYSMON_MEM_BAR = NORD12
SYSMON_NET_BAR = NORD13
SYSMON_TEMP_BAR = NORD11

# Pwnagotchi UI color assignments
PWNGRID_DOT = NORD8
FRIEND_DOT = NORD14
FRIEND_NAME = NORD13
STATUS_TEXT = NORD6
NAME_TEXT = NORD8
FACE_BACKGROUND = NORD1
```

### 6. Create Theme Package Init File (Optional)

```bash
sudo nano /opt/pwnagotchi/theme/__init__.py
```

Copy and paste the following code:

```python
# /opt/pwnagotchi/theme/__init__.py

from . import nord

# Set the active theme
active_theme = nord

# Export theme colors
COLORS = {
    'background': active_theme.UI_BACKGROUND,
    'foreground': active_theme.UI_FOREGROUND,
    'highlight': active_theme.UI_HIGHLIGHT,
    'accent': active_theme.UI_ACCENT,
    'warning': active_theme.UI_WARNING,
    'danger': active_theme.UI_DANGER,
    'success': active_theme.UI_SUCCESS,
    'info': active_theme.UI_INFO
}

# Export system monitor colors
SYSMON = {
    'background': active_theme.SYSMON_BACKGROUND,
    'text': active_theme.SYSMON_TEXT,
    'title': active_theme.SYSMON_TITLE,
    'bar_outline': active_theme.SYSMON_BAR_OUTLINE,
    'cpu_bar': active_theme.SYSMON_CPU_BAR,
    'mem_bar': active_theme.SYSMON_MEM_BAR,
    'net_bar': active_theme.SYSMON_NET_BAR,
    'temp_bar': active_theme.SYSMON_TEMP_BAR
}

# Export Pwnagotchi UI colors
PWNAGOTCHI = {
    'pwngrid_dot': active_theme.PWNGRID_DOT,
    'friend_dot': active_theme.FRIEND_DOT,
    'friend_name': active_theme.FRIEND_NAME,
    'status_text': active_theme.STATUS_TEXT,
    'name_text': active_theme.NAME_TEXT,
    'face_background': active_theme.FACE_BACKGROUND
}
```

## Step 8: Finalize Setup

1. Make the scripts executable:
   ```bash
   sudo chmod +x /opt/pwnagotchi/sysmon/sysmon.py
   ```

2. Enable and start the system monitor service:
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable pwnagotchi-sysmon.service
   sudo systemctl start pwnagotchi-sysmon.service
   ```

## Step 9: Test and Debug

1. Restart the Pwnagotchi service:
   ```bash
   sudo systemctl restart pwnagotchi
   ```

2. Check the logs for any issues:
   ```bash
   # Pwnagotchi main logs
   tail -f /var/log/pwnagotchi.log
   
   # System monitor logs
   tail -f /var/log/pwnagotchi-sysmon.log
   ```

3. Verify the displays are working correctly:
   - Center display should show the Pwnagotchi UI
   - Side displays should show system monitoring information

## Step 10: Create a Backup (Optional)

Once everything is working correctly, create a backup of your configuration:

```bash
# Using the built-in backup script
cd /path/to/scripts
./BR.sh backup -o my-custom-pwnagotchi-backup.tgz
```

## Troubleshooting

### Display Issues
- Check SPI device availability: `ls -l /dev/spidev*`
- Verify pin connections according to the pin mapping reference
- Check for errors in the logs

### System Monitor Issues
- Verify the service is running: `systemctl status pwnagotchi-sysmon.service`
- Check permissions on directories and files
- Look for Python errors in the logs

### Connection Issues
- Verify the USB network interface is up: `ifconfig`
- Try connecting via serial if SSH is not working

## Pin Mapping Reference

```
VCC     3.3V
GND     GND
MOSI0   38
MOSI1   19
SCLK0   40
SCLK1   23
CS0     12      # Center display
CS1     24      # Left side display
CS2     26      # Right side display
DC0     15      # Center display
DC1     7       # Left side display
DC2     29      # Right side display
RST0    13      # Center display
RST1    18      # Left side display
RST2    16      # Right side display
BL0     35      # Center display
BL1     33      # Left side display
BL2     32      # Right side display
KEY1    22      # Left button
KEY2    37      # Right button
``` 
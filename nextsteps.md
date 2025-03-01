# Pwnagotchi with Waveshare Zero LCD Hat (A) - Next Steps

## What We've Done

### 1. Display Configuration
- Updated `config.txt` with proper SPI settings:
  ```
  [pi0]
  dtoverlay=spi0-2cs  # For the two buttons
  dtoverlay=spi1-3cs  # For the three displays
  ```
- Modified pin definitions in `pwnagotchi/ui/hw/libs/waveshare/lcd/lcdhat/config.py`:
  ```python
  # Pin definition for center display
  RST_PIN = 13  # RST0 for center display
  DC_PIN = 15   # DC0 for center display
  BL_PIN = 35   # BL0 for center display
  
  Device = Device_SPI
  spi = spidev.SpiDev(1, 0)  # SPI1.0 for center display
  ```

### 2. Nord Theme Implementation
- Created global theme system at `/opt/pwnagotchi/theme/`:
  - `__init__.py` - Module initialization
  - `nord.py` - Nord color palette definitions
- Implemented color schemes for different components:
  - Base Nord colors (Polar Night, Snow Storm, Frost, Aurora)
  - UI color assignments
  - System monitor color assignments
  - Pwnagotchi UI color assignments

### 3. System Monitor for Side Displays
- Created system monitor at `/opt/pwnagotchi/sysmon/`:
  - `display/st7735.py` - Driver for ST7735S displays
  - `sysmon.py` - Main monitoring code
- Implemented features:
  - CPU and memory monitoring
  - Vertical bar graphs with Nord theme colors
  - Historical data graphs
  - 60-second update interval
- Created systemd service at `/etc/systemd/system/pwnagotchi-sysmon.service`

## Next Steps

### 1. Connection and Testing
- Establish connection to the Pi Zero W (SSH or serial)
- Test the center display configuration:
  ```bash
  # Check if SPI devices are available
  ls -l /dev/spidev*
  
  # Verify the Pwnagotchi UI is displaying on center screen
  systemctl status pwnagotchi
  ```

### 2. Side Display Setup
- Install required packages:
  ```bash
  sudo apt-get update
  sudo apt-get install python3-pip python3-pil python3-numpy
  pip3 install psutil spidev RPi.GPIO
  ```
- Create necessary directories:
  ```bash
  sudo mkdir -p /opt/pwnagotchi/sysmon/display
  sudo mkdir -p /opt/pwnagotchi/theme
  sudo chown -R pi:pi /opt/pwnagotchi
  ```
- Copy our code to the Pi
- Set up logging:
  ```bash
  sudo touch /var/log/pwnagotchi-sysmon.log
  sudo chown pi:pi /var/log/pwnagotchi-sysmon.log
  ```
- Enable and start the service:
  ```bash
  sudo systemctl daemon-reload
  sudo systemctl enable pwnagotchi-sysmon.service
  sudo systemctl start pwnagotchi-sysmon.service
  ```

### 3. Debugging and Refinement
- Check system monitor logs:
  ```bash
  tail -f /var/log/pwnagotchi-sysmon.log
  ```
- Verify SPI device assignments:
  ```bash
  # For center display
  spi = spidev.SpiDev(1, 0)
  
  # For left side display
  LEFT_DISPLAY = {
      'spi_device': 1,  # spi1.1
      'dc_pin': 7,      # DC1
      'rst_pin': 18,    # RST1
      'bl_pin': 33      # BL1
  }
  
  # For right side display
  RIGHT_DISPLAY = {
      'spi_device': 2,  # spi1.2
      'dc_pin': 29,     # DC2
      'rst_pin': 16,    # RST2
      'bl_pin': 32      # BL2
  }
  ```
- Adjust display layout and colors as needed

### 4. Future Enhancements
- Add button functionality (KEY1 and KEY2)
- Implement additional metrics for side displays:
  - Temperature
  - Network activity
  - Battery status (if applicable)
- Apply Nord theme to main Pwnagotchi UI
- Create custom faces or animations for the Pwnagotchi

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
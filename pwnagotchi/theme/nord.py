#!/usr/bin/env python3

"""
Nord Theme Color Definitions
https://www.nordtheme.com/

This module provides color definitions for use across the pwnagotchi project.
Colors are provided in RGB format for PIL compatibility.
"""

# Base Nord Colors
POLAR_NIGHT = {
    'nord0': (46, 52, 64),     # Base background
    'nord1': (59, 66, 82),     # Lighter background
    'nord2': (67, 76, 94),     # Subtle borders
    'nord3': (76, 86, 106)     # Bright borders
}

SNOW_STORM = {
    'nord4': (216, 222, 233),  # Darkest text
    'nord5': (229, 233, 240),  # Medium text
    'nord6': (236, 239, 244)   # Brightest text
}

FROST = {
    'nord7': (143, 188, 187),  # Mint frost
    'nord8': (136, 192, 208),  # Ice blue
    'nord9': (129, 161, 193),  # Medium blue
    'nord10': (94, 129, 172)   # Dark blue
}

AURORA = {
    'nord11': (191, 97, 106),   # Red (critical/error)
    'nord12': (208, 135, 112),  # Orange (warning)
    'nord13': (235, 203, 139),  # Yellow (caution)
    'nord14': (163, 190, 140),  # Green (success)
    'nord15': (180, 142, 173)   # Purple (special)
}

# Semantic Color Assignments
UI_COLORS = {
    'background': POLAR_NIGHT['nord0'],
    'text': {
        'primary': SNOW_STORM['nord6'],
        'secondary': SNOW_STORM['nord4'],
        'disabled': POLAR_NIGHT['nord3']
    },
    'borders': {
        'subtle': POLAR_NIGHT['nord2'],
        'bright': POLAR_NIGHT['nord3']
    },
    'status': {
        'success': AURORA['nord14'],
        'warning': AURORA['nord13'],
        'error': AURORA['nord11'],
        'special': AURORA['nord15']
    },
    'accent': {
        'primary': FROST['nord8'],
        'secondary': FROST['nord9'],
        'tertiary': FROST['nord10']
    }
}

# System Monitor Specific Colors
SYSMON_COLORS = {
    'cpu': {
        'normal': FROST['nord10'],
        'warning': AURORA['nord13'],
        'critical': AURORA['nord11']
    },
    'memory': {
        'normal': FROST['nord9'],
        'warning': AURORA['nord13'],
        'critical': AURORA['nord11']
    },
    'text': {
        'title': SNOW_STORM['nord6'],
        'value': FROST['nord8'],
        'label': SNOW_STORM['nord4']
    },
    'graph': {
        'background': POLAR_NIGHT['nord1'],
        'line': FROST['nord8'],
        'grid': POLAR_NIGHT['nord2']
    }
}

# Pwnagotchi UI Specific Colors
PWNGRID_COLORS = {
    'face': FROST['nord8'],
    'name': SNOW_STORM['nord6'],
    'status': SNOW_STORM['nord4'],
    'wifi': {
        'connected': AURORA['nord14'],
        'disconnected': AURORA['nord11'],
        'handshake': AURORA['nord13']
    },
    'stats': {
        'text': SNOW_STORM['nord5'],
        'value': FROST['nord7']
    }
}
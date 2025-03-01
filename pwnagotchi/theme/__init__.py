"""
Pwnagotchi Theme Module

This module provides theming capabilities for the pwnagotchi project.
Currently implements the Nord theme (https://www.nordtheme.com/).
"""

from .nord import (
    # Base color palettes
    POLAR_NIGHT,
    SNOW_STORM,
    FROST,
    AURORA,
    
    # Semantic color groupings
    UI_COLORS,
    SYSMON_COLORS,
    PWNGRID_COLORS
)

__all__ = [
    'POLAR_NIGHT',
    'SNOW_STORM',
    'FROST',
    'AURORA',
    'UI_COLORS',
    'SYSMON_COLORS',
    'PWNGRID_COLORS'
]
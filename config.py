import os

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "empresa.db")

# Window Configuration
APP_TITLE = "PyStock_Manager"
WINDOW_WIDTH = 1100
WINDOW_HEIGHT = 700

# Theme settings
# Using custom HSL-tailored colors in HEX for modern dark styling (similar to Catppuccin Mocha)
COLORS = {
    "bg_dark": "#181825",       # Deep dark background for sidebar
    "bg_medium": "#1e1e2e",     # Medium dark for main container background
    "bg_light": "#252538",      # Lighter dark for cards and frames
    "accent": "#89b4fa",        # Blue primary accent
    "accent_hover": "#b4befe",  # Soft lavender for hover states
    "text_primary": "#cdd6f4",  # High contrast text color
    "text_secondary": "#a6adc8",# Subdued text color
    "success": "#a6e3a1",       # Pastel green for success logs/buttons
    "warning": "#f9e2af",       # Soft yellow for stock alerts
    "danger": "#f38ba8",        # Pastel red for critical/delete actions
    "border": "#313244",        # Border/Separator color
}

# Theme settings for CustomTkinter
CTK_THEME = "dark"              # default theme mode
CTK_COLOR_THEME = "blue"        # custom base color theme

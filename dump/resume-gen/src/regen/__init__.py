import os

CURRENT_PATH = os.path.dirname(os.path.abspath(__file__))
PROFILE_PATH = os.path.join(CURRENT_PATH, "profiles")
PRESET_PATH = os.path.join(CURRENT_PATH, "presets")

PRESETS = [x[:-3] for x in os.listdir(PRESET_PATH) if x.endswith(".py") and not x.startswith("__")]
PROFILES = [x for x in os.listdir(PROFILE_PATH) if os.path.isdir(os.path.join(PROFILE_PATH, x))]

EXAMPLE_TOML = os.path.join(CURRENT_PATH, "example.toml")

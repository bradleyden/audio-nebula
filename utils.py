import yaml

# This file handles all utils related to fetching and saving user defined settings.

# Default settings, which can be overwritten by values defined in settings.yml
settings = {
    'intensity_color': 'red',
    'mic_sensitivity': .035,
    'width': 1920,
    'height': 1080
}

# Save whatever data is defined in the settings variable to settings.yml
def save_settings():
    global settings
    if validate_settings(settings):
        with open("settings.yml", 'w') as f:
            yaml.dump(settings, f, default_flow_style=False)
    else:
        print("Current settings are invalid and cannot be saved.")


# Validate a settings object to ensure values are safe to load or save
def validate_settings(settings_data):
    return(
        isinstance(settings_data['mic_sensitivity'], float) and \
        isinstance(settings_data['width'], int) and \
        isinstance(settings_data['height'], int) and \
        (settings_data['intensity_color'] == 'red' or settings_data['intensity_color'] == 'green')
    )

# Load settings from settings.yml to memory
def read_settings():
    global settings

    try:
        with open("settings.yml", 'r') as f:
            try:
                settings_data = yaml.safe_load(f)

                if validate_settings(settings_data):
                    settings = settings_data
                else:
                    print("Invalid settings file, restoring defaults")
                    save_settings()
            except yaml.YAMLError as exc:
                print(exc)
    except FileNotFoundError:
        print("No Settings file found, generating defaults")
        save_settings()


# Get a specified setting value from memory
def get_setting(key):
    global settings
    return settings[key]


# Set a specified setting to a given value in memory, then save it
def set_setting(key, value):
    global settings
    settings[key] = value
    save_settings()


# Utility function to clamp a numeric value based on a max and min value
def clamp(n, minn, maxn):
    if n < minn:
        return minn
    if n > maxn:
        return maxn
    return n


# Utility function to return the opposite of whichever color is passed in
# to avoid repetative conditional logic.
def toggle_color(current_color):
    if current_color == 'red':
        return 'green'
    else:
        return 'red'
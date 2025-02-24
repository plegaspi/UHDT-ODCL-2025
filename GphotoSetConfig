import subprocess
import sys

# Define a dictionary of presets.
# Each preset is a dictionary where the keys are the configuration names
# (which remain constant) and the values are the values to be set.
PRESETS = {
    "default": {
        "exposurecompensation": "15",
        "d170": "0",
        "iso": "2"
    }
}

def set_config_value(name, value):
    """
    Set a camera configuration by calling:
      gphoto2 --set-config <name>=<value>
    """
    config_arg = f"{name}={value}"
    command = ["gphoto2", "--set-config", config_arg]
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        print(f"Successfully set {name} to {value}.")
        if result.stdout:
            print(result.stdout.strip())
    except subprocess.CalledProcessError as e:
        print(f"Error setting {name} to {value}: {e.stderr}", file=sys.stderr)
        sys.exit(1)

def apply_preset(preset):
    """
    Apply a preset by iterating over its key/value pairs and setting each value.
    """
    for name, value in preset.items():
        set_config_value(name, value)

if __name__ == "__main__":
    # Choose the preset based on a command-line argument.
    # If no preset is provided, the "default" preset is used.
    preset_name = sys.argv[1] if len(sys.argv) > 1 else "default"
    if preset_name not in PRESETS:
        print(f"Preset '{preset_name}' not found. Available presets:", file=sys.stderr)
        for key in PRESETS.keys():
            print(f"  - {key}", file=sys.stderr)
        sys.exit(1)

    print(f"Applying preset '{preset_name}'...")
    apply_preset(PRESETS[preset_name])


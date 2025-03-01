#!/usr/bin/env python3
import subprocess
import sys
import json
import csv
from datetime import datetime

# -------------------------------
# Kill Process Functionality
# -------------------------------
def get_gphot_processes():
    """
    Retrieve a list of PIDs for processes whose command line contains 'gphot'.
    Excludes any lines that include 'grep'.
    """
    try:
        output = subprocess.check_output(["ps", "aux"], text=True)
    except subprocess.CalledProcessError as e:
        print("Error running ps aux:", e, file=sys.stderr)
        sys.exit(1)
    
    pids = []
    for line in output.splitlines():
        if "gphot" in line and "grep" not in line:
            parts = line.split()
            if len(parts) > 1:
                pid = parts[1]
                pids.append(pid)
    return pids

def kill_process(pid):
    """
    Kill a process given its PID using the kill command.
    """
    try:
        subprocess.run(["kill", "-9", pid], check=True)
        print(f"Killed process with PID {pid}")
    except subprocess.CalledProcessError as e:
        print(f"Error killing process {pid}: {e}", file=sys.stderr)

def kill_gphot_processes():
    """
    Find and kill up to two processes matching 'gphot'.
    """
    pids = get_gphot_processes()
    if not pids:
        print("No matching 'gphot' processes found.")
        return

    # Kill the first 2 matching processes (or fewer if less than 2 exist)
    for pid in pids[:2]:
        kill_process(pid)

# -------------------------------
# Configuration Setting & Getting
# -------------------------------
# Define a dictionary of presets.
# Each preset maps configuration names to the values to be set.
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

def get_config_value(name):
    """
    Retrieve a camera configuration by calling:
      gphoto2 --get-config <name>
    """
    command = ["gphoto2", "--get-config", name]
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        print(f"Configuration for '{name}':")
        print(result.stdout.strip())
    except subprocess.CalledProcessError as e:
        print(f"Error getting configuration for {name}: {e.stderr}", file=sys.stderr)
        sys.exit(1)

# -------------------------------
# Get All Configurations and Export
# -------------------------------
def clean_line(line):
    """
    Clean a line by stripping whitespace, removing any trailing commas,
    and stripping surrounding quotes.
    """
    line = line.strip()
    if line.endswith(','):
        line = line[:-1].strip()
    if line.startswith('"') and line.endswith('"'):
        line = line[1:-1].strip()
    return line

def get_all_config_details():
    """
    Run gphoto2 --list-all-config and parse the output into a list of dictionaries.
    Each dictionary has keys: "key", "label", and "current".
    """
    try:
        result = subprocess.run(
            ["gphoto2", "--list-all-config"],
            capture_output=True,
            text=True,
            check=True
        )
    except subprocess.CalledProcessError as e:
        print("Error running gphoto2 --list-all-config:", e.stderr, file=sys.stderr)
        sys.exit(1)
    
    all_configs = []
    current_block = []
    for raw_line in result.stdout.splitlines():
        line = clean_line(raw_line)
        if not line:
            continue
        
        if line == "END":
            if current_block:
                config_key = current_block[0]
                label = None
                current_val = None
                for block_line in current_block[1:]:
                    if block_line.startswith("Label:"):
                        label = block_line[len("Label:"):].strip()
                    elif block_line.startswith("Current:"):
                        current_val = block_line[len("Current:"):].strip()
                all_configs.append({
                    "key": config_key,
                    "label": label,
                    "current": current_val
                })
                current_block = []
        else:
            current_block.append(line)
    
    # Process any remaining block if it wasn't terminated with "END"
    if current_block:
        config_key = current_block[0]
        label = None
        current_val = None
        for block_line in current_block[1:]:
            if block_line.startswith("Label:"):
                label = block_line[len("Label:"):].strip()
            elif block_line.startswith("Current:"):
                current_val = block_line[len("Current:"):].strip()
        all_configs.append({
            "key": config_key,
            "label": label,
            "current": current_val
        })
    
    return all_configs

def export_configs_as_json(config_list, filename="gphoto2_config.json"):
    try:
        with open(filename, "w") as f:
            json.dump(config_list, f, indent=4)
        print(f"Configuration details successfully written to {filename}")
    except IOError as e:
        print("Error writing to file:", e, file=sys.stderr)
        sys.exit(1)

def export_configs_as_csv(config_list, filename="all_config.csv"):
    fieldnames = ["key", "label", "current"]
    try:
        with open(filename, "w", newline="") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for config in config_list:
                writer.writerow(config)
        print(f"Configuration details successfully written to {filename}")
    except IOError as e:
        print("Error writing CSV to file:", e, file=sys.stderr)
        sys.exit(1)

# -------------------------------
# Main Execution Flow
# -------------------------------
def main():
    # First, kill any existing gphot processes.
    kill_gphot_processes()

    # Choose the preset based on a command-line argument.
    # If no preset is provided, use the "default" preset.
    preset_name = sys.argv[1] if len(sys.argv) > 1 else "default"
    if preset_name not in PRESETS:
        print(f"Preset '{preset_name}' not found. Available presets:", file=sys.stderr)
        for key in PRESETS.keys():
            print(f"  - {key}", file=sys.stderr)
        sys.exit(1)

    print(f"Applying preset '{preset_name}'...")
    apply_preset(PRESETS[preset_name])

    print("\nRetrieving updated configuration values for the preset:")
    for name in PRESETS[preset_name]:
        get_config_value(name)

    # -------------------------------
    # Run --list-all-config and export outputs
    # -------------------------------
    print("\nRunning '--list-all-config' to retrieve all configuration values...")
    config_list = get_all_config_details()
    
    # Generate timestamped filenames.
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    json_filename = f"all_config_{timestamp}.json"
    csv_filename = f"all_config_{timestamp}.csv"

    print("Exporting configuration as JSON and CSV...")
    export_configs_as_json(config_list, json_filename)
    export_configs_as_csv(config_list, csv_filename)

if __name__ == "__main__":
    main()


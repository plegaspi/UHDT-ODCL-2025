#!/usr/bin/env python3
import subprocess
import sys
import json
import csv
import os
from datetime import datetime

''' Template
"<name>":  {"iso"                 : <value>,
            "whitebalance"        : <value>,
            "exposurecompensation": <value>,
            "f-number"            : <value>,
            "shutterspeed"        : <value>,
            "d01c"                : <value>, # Noise Reduction
            "d170"                : <value>  # Lens Zoom
            }
'''

PRESETS = {
    "default": {"exposurecompensation": "15", 
                "d170": "0", 
                "iso": "2"
                },
    "preset2": {"exposurecompensation": "10", 
                "d170": "1", 
                "iso": "4"
                }
}

# Retrieve a list of PIDs for processes whose command line contains 'gphot', excluding 'grep'.
def get_gphoto_processes():
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
                pids.append(parts[1])
    return pids

# Kill a process given its PID using the kill command.
def kill_process(pid):
    try:
        subprocess.run(["kill", "-9", pid], check=True)
        print(f"Killed process with PID {pid}")
    except subprocess.CalledProcessError as e:
        print(f"Error killing process {pid}: {e}", file=sys.stderr)

# Find and kill processes matching 'gphot'.
def kill_gphoto_processes():

    pids = get_gphoto_processes()
    if not pids:
        print("No matching 'gphot' processes found.")
        return
    for pid in pids[:2]:
        kill_process(pid)

# Set a camera configuration using 'gphoto2 --set-config <name>=<value>'.
def set_config_value(name, value):
    
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


#Apply a preset by setting each configuration value.
def apply_preset(preset):
    
    for name, value in preset.items():
        set_config_value(name, value)

# Clean a line by stripping whitespace, removing trailing commas, and stripping surrounding quotes. (used for exporting the json/csv file)
def clean_line(line):
    line = line.strip()
    if line.endswith(','):
        line = line[:-1].strip()
    if line.startswith('"') and line.endswith('"'):
        line = line[1:-1].strip()
    return line

# Parse output from 'gphoto2 --list-all-config' into a list of dictionaries with keys 'key', 'label', and 'current'.
def get_all_config_details():
    try:
        result = subprocess.run(["gphoto2", "--list-all-config"], capture_output=True, text=True, check=True)
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
                all_configs.append({"key": config_key, "label": label, "current": current_val})
                current_block = []
        else:
            current_block.append(line)
    if current_block:
        config_key = current_block[0]
        label = None
        current_val = None
        for block_line in current_block[1:]:
            if block_line.startswith("Label:"):
                label = block_line[len("Label:"):].strip()
            elif block_line.startswith("Current:"):
                current_val = block_line[len("Current:"):].strip()
        all_configs.append({"key": config_key, "label": label, "current": current_val})
    return all_configs


# Export configuration details as a JSON file to the specified filepath.
def export_configs_as_json(config_list, filepath):
    try:
        with open(filepath, "w") as f:
            json.dump(config_list, f, indent=4)
        #print(f"Configuration details successfully written to {filepath}")
    except IOError as e:
        print("Error writing to file:", e, file=sys.stderr)
        sys.exit(1)

# Export configuration details as a CSV file to the specified filepath.
def export_configs_as_csv(config_list, filepath):
    fieldnames = ["key", "label", "current"]
    try:
        with open(filepath, "w", newline="") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for config in config_list:
                writer.writerow(config)
        #print(f"Configuration details successfully written to {filepath}")
    except IOError as e:
        print("Error writing CSV to file:", e, file=sys.stderr)
        sys.exit(1)

# Capture an image using gphoto2 and download it to the specified folder.
def trigger(file_name):
    command = ["gphoto2", "--capture-image-and-download", "--filename", file_name]
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        #print(f"Image captured and saved as {image_filepath}")
        if result.stdout:
            print(result.stdout.strip())
    except subprocess.CalledProcessError as e:
        print(f"Error capturing image: {e.stderr}", file=sys.stderr)
        sys.exit(1)

def flight_testing(presets, images_per_preset):
    for preset_name, preset_values in PRESETS.items():
        apply_preset(preset_values)
        config_list = get_all_config_details()
        if not os.path.exists(preset_name):
            try:
                os.makedirs(preset_name)
            except OSError as e:
                print(f"Error creating folder '{preset_name}': {e}", file=sys.stderr)
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        json_filepath = os.path.join(preset_name, f"all_config_{timestamp}.json")
        csv_filepath = os.path.join(preset_name, f"all_config_{timestamp}.csv")
        
        export_configs_as_json(config_list, json_filepath)
        export_configs_as_csv(config_list, csv_filepath)
        for i in range(images_per_preset):
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            image_filepath = os.path.join(preset_name, f"captured_{timestamp}.jpg")
            trigger(image_filepath)

def initialize(preset):
    kill_gphoto_processes()
    result = subprocess.run("gphoto2", "--auto-detect")
    print("Camera connected")
    apply_preset(preset)

def main():
    kill_gphoto_processes()
    for preset_name, preset_values in PRESETS.items():
        #print(f"\n=== Applying preset '{preset_name}' ===")
        apply_preset(preset_values)
        #print(f"\nRetrieving configuration values for preset '{preset_name}':")
        #for name in preset_values:
            #get_config_value(name)
        config_list = get_all_config_details()
        if not os.path.exists(preset_name):
            try:
                os.makedirs(preset_name)
                #print(f"Folder '{preset_name}' created.")
            except OSError as e:
                print(f"Error creating folder '{preset_name}': {e}", file=sys.stderr)
                sys.exit(1)
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        json_filepath = os.path.join(preset_name, f"all_config_{timestamp}.json")
        csv_filepath = os.path.join(preset_name, f"all_config_{timestamp}.csv")
        
        export_configs_as_json(config_list, json_filepath)
        export_configs_as_csv(config_list, csv_filepath)
        #print("Capturing image...")
        for i in range(10):
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            image_filepath = os.path.join(preset_name, f"captured_{timestamp}.jpg")
            trigger(image_filepath)
            


if __name__ == "__main__":
    main()

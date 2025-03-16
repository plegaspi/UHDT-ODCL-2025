import os
import datetime
import sys
import Camera


def main(images_per_preset):
    PRESETS = Camera.PRESETS
    for preset_name, preset_values in PRESETS.items():
        Camera.apply_preset(preset_values)
        config_list = Camera.get_all_config_details()
        if not os.path.exists(preset_name):
            try:
                os.makedirs(preset_name)
            except OSError as e:
                print(f"Error creating folder '{preset_name}': {e}", file=sys.stderr)
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        json_filepath = os.path.join(preset_name, f"all_config_{timestamp}.json")
        csv_filepath = os.path.join(preset_name, f"all_config_{timestamp}.csv")
        
        Camera.export_configs_as_json(config_list, json_filepath)
        Camera.export_configs_as_csv(config_list, csv_filepath)
        #print("Capturing image...")
        for i in range(images_per_preset):
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            image_filepath = os.path.join(preset_name, f"captured_{timestamp}.jpg")
            Camera.trigger(image_filepath)
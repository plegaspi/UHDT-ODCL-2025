import yaml

class Config():
    def __init__(self, config_file_path):
        self.file_path = config_file_path
        self.params = self.read_configuration_file()
        self.targets = self.parse_targets()
        self.is_logging_enabled = self.parse_logging()
        self.default_drop_zones = self.parse_default_dropzones()
        self.watch_dir_path = self.params["watch_directory"]
    
    def read_configuration_file(self):
        with open(self.file_path) as file_path:
            params = yaml.safe_load(file_path)
            return params

    
    def parse_targets(self):
        targets = self.params["targets"]
        number_of_targets =  self.params["number_of_targets"]
        assert(len(targets) == number_of_targets), f"Found {len(targets)} targets in configuration file. You must enter exactly 4 targets."
        return targets
    
    def parse_logging(self):
        is_logging_enabled = self.params["logging"]
        return is_logging_enabled
    
    def parse_default_dropzones(self):
        mode = self.params["mode"]
        drop_zones = self.params["airdrop_mode"][mode]
        assert(len(drop_zones) == 4), f"Found {len(drop_zones)} drop zones in configuration file for mode {mode}. You must enter exactly 4 drop zones."
        return drop_zones

import argparse
import json

default_config = {
    "REPORT_SIZE": 1000,
    "REPORT_DIR": "./reports",
    "LOG_DIR": "./log"
}

def read_config(config_file):
    try:
        with open(config_file) as f:
            config_from_file = json.load(f)
    except FileNotFoundError:
        print(f"Config file '{config_file}' not found")
        exit(1)
    except json.JSONDecodeError:
        print(f"Error parsing config file '{config_file}'")
        exit(1)
    return config_from_file

def merge_configs(default_config, file_config):
    merged_config = default_config.copy()
    merged_config.update(file_config)
    return merged_config

def main(config_file):
    default_config = {
        "REPORT_SIZE": 1000,
        "REPORT_DIR": "./reports",
        "LOG_DIR": "./log"
    }

    file_config = read_config(config_file)
    config = merge_configs(default_config, file_config)

    # Используйте полученную конфигурацию для выполнения остальной части скрипта

    print(config)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="config.json", help="Path to configuration file")
    args = parser.parse_args()
    main(args.config)
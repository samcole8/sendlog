from plugin import Log, Rule, Transformation
from utils.config_handler import ConfigHandler


CONFIG_PATH = "sendlog.yml"

def main():
    config = ConfigHandler(CONFIG_PATH)

if __name__ == "__main__":
    main()
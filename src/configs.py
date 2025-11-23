from attr import dataclass
from datetime import datetime
import yaml

CONFIG_FILE = "config.yaml"

@dataclass
class ScraperConfig:
    BASE_URL:str = 'https://www.hltv.org'
    LOG_FILE:str = 'logs/' + datetime.now().strftime("%Y-%m-%d")
    chrome_driver_path:str|None = None

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)


@dataclass
class PlayerConfig:
    pass

@dataclass
class MatchConfig:
    pass

@dataclass
class Filter:
    start_date:datetime
    end_date:datetime

def get_scraper_config(config_file = CONFIG_FILE) -> ScraperConfig:
    with open(config_file, 'r') as file:
        config = yaml.safe_load(file)
        return ScraperConfig(**config['scraper'])
    
def get_player_config(config_file = CONFIG_FILE) -> PlayerConfig:
    with open(config_file, 'r') as file:
        config = yaml.safe_load(file)
        return PlayerConfig(**config['player'])
    
def get_match_config(config_file = CONFIG_FILE) -> MatchConfig:
    with open(config_file, 'r') as file:
        config = yaml.safe_load(file)
        return MatchConfig(**config['match'])
from attr import dataclass
import yaml

@dataclass
class ScraperConfig:
    BASE_URL = 'https://www.hltv.org'
    chrome_driver_path = None

def get_scraper_config() -> ScraperConfig:
    pass
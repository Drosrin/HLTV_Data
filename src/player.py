"""
    Author: Dr_osrin <https://github.com/Drosrin>
    Description: 
        Scrape HLTV player stats
        - get players' stats by player name
        - Filter data according to HLTV filters
        - get formatted data
"""

from datetime import datetime

from attr import dataclass
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService

from src.configs import get_scraper_config

@dataclass
class Filter:
    start_date:datetime
    end_date:datetime


class HLTV_Player_Stat_Scraper:
    def __init__(self, player_name:str|None = None):
        self.matches = []
        self._config = get_scraper_config()
        self._driver = self._get_driver()
        self.player_name = player_name

    def _get_driver(self):
        service = ChromeService(executable_path=self._config.chrome_driver_path)
        options = webdriver.ChromeOptions()
        driver = webdriver.Chrome(service=service, options=options)
        return driver
    
    def search_player(self, player_name:str) -> str | None:
        self._driver.get(self._config.BASE_URL + '')

    def parse_player_website(self) -> None:
        pass
    
    def get_basic_stats(self) -> dict[str, str]:
        pass
    def get_matches(self, match_filter:Filter) -> list[Match]:
        pass



def main():
    # search certain player
    scraper = HLTV_Player_Stat_Scraper()
    player_name = 'NiKo'
    scraper.search_player(player_name)
    # parse player's website -> matches
    scraper.parse_player_website()
    # return all matches
    matches = scraper.get_matches(
        match_filter = Filter(
            start_date=datetime(2025, 1, 1), 
            end_date=datetime(2025, 12, 31)
        )
    )


if __name__ == '__main__':
    main()
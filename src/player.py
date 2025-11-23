"""
    Author: Dr_osrin <https://github.com/Drosrin>
    Description: 
        Scrape HLTV player stats
        - get players' stats by player name
        - Filter data according to HLTV filters
        - get formatted data
"""

from datetime import datetime

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By

from src.configs import get_scraper_config, Filter
from src.match import Match
from src.logger import get_logger


class HLTV_Player_Stat_Scraper:
    def __init__(self, player_name:str|None = None):
        self.matches = []
        self._config = get_scraper_config()
        self.logger = get_logger(__name__, self._config.LOG_FILE)
        self._driver = self._get_driver()
        self.player_name = player_name

        self.logger.info("HLTV_Player_Stat_Scraper initialized")

    def _get_driver(self):
        driver = webdriver.Chrome()
        self.logger.info("Driver initialized")
        return driver
    
    def search_player(self, player_name:str|None) -> str | None:
        """
        This function will search for a player by name. This function DOES NOT ensure that you can get the exact player you want: 
        e.g. you can search 'niko', but this function will return `Nikola 'NiKo' Kovač` instead of Nikolaj 'niko' Kristensen.
        It follows the ranking on HLTV.

        Parameters
        -------
        player_name: str
            The name of the player you want to search for. This parameter will be overwritten by `self.player_name` if it is not None.

        Returns
        -------
        str | None:
            A Part of the URL of the player's page, in format of `/player/<ID>/<PLAYER_NAME>`.
            e.g. `/player/3741/niko`
        """
        # HLTV search be like:
        # https://www.hltv.org/search?query=NiKo
        # so directly visit it.
        player_name = player_name if self.player_name is None else self.player_name
        search_page = f"{self._config.BASE_URL}/search?query={player_name}"
        self._driver.get(search_page)
        search_dst = 'body > div.bgPadding > div.widthControl > div:nth-child(2) > div.contentCol > div.search > table:nth-child(4) > tbody > tr:nth-child(2) > td > a'
        list_of_players = self._driver.find_element(By.CSS_SELECTOR, search_dst)
        player_url = list_of_players.get_attribute('href')
        if player_url is None:
            self.logger.error(f"Player {player_name} not found")
            return None
        self.logger.info(f"Found player: {player_url}")
        return player_url

    def parse_player_website(self, player_url:str) -> None:
        """
        This function will parse the player's website URL and store it into the scraper.

        Parameters
        -------
        player_url: str
            The URL of the player's page.

        Returns
        -------
        None
        """
        self.logger.info(f"Parsing player: {player_url}")
        player_url = player_url.lstrip(self._config.BASE_URL + '/player/')
        player_id, player_name = player_url.split('/')
        self.player_id = player_id
        self.player_name = player_name
        self.logger.info(f"Player ID: {self.player_id}, Player Name: {self.player_name}")

    
    def get_basic_stats(self, stats_filter:Filter) -> dict[str, str]:
        src_url = f"{self._config.BASE_URL}/stats/players/{self.player_id}/{self.player_name}?{stats_filter.to_query()}"
        
        t_side_rt_selector_path = 'body > div.bgPadding > div.widthControl > div:nth-child(2) > div.contentCol > div.stats-section.stats-player.stats-player-overview > div.player-summary-stat-box.compact > div.player-summary-stat-box-right > div.player-summary-stat-box-right-middle > div.player-summary-stat-box-side-rating.t-rating > div > div.player-summary-stat-box-side-rating-background'
        round_swing_selector_path = 'body > div.bgPadding > div.widthControl > div:nth-child(2) > div.contentCol > div.stats-section.stats-player.stats-player-overview > div.player-summary-stat-box.compact > div.player-summary-stat-box-right > div.player-summary-stat-box-right-bottom > div:nth-child(1) > div.player-summary-stat-box-data'
    def get_matches(self, match_filter:Filter) -> list[Match]:
        pass



def main():
    # search certain player
    scraper = HLTV_Player_Stat_Scraper()
    player_name = 'NiKo'
    player_url = scraper.search_player(player_name)
    # parse player's website -> matches
    if player_url is None:
        print("Player not found")
        return
    scraper.parse_player_website(player_url)
    # return all matches
    matches = scraper.get_matches(
        match_filter = Filter(
            start_date=datetime(2025, 1, 1), 
            end_date=datetime(2025, 12, 31)
        )
    )


if __name__ == '__main__':
    main()
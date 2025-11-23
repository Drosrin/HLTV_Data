"""
    Author: Dr_osrin <https://github.com/Drosrin>
    Description: 
        Scrape HLTV player stats
        - get players' stats by player name
        - Filter data according to HLTV filters
        - get formatted data
"""

import selenium.common.exceptions
from selenium.webdriver.common.by import By
import undetected_chromedriver as uc
from selenium.webdriver.chrome.options import Options

from src.configs import get_scraper_config, Filter # This is in ./src! Not ./config !
from src.logger import get_logger
from src.views.visualize import visualize_player_stats
from src.utils.exponential_backoff import exponential_backoff

class HLTV_Player_Stat_Scraper:
    """
    A scraper class for retrieving player statistics from HLTV.org.
    
    This class provides methods to search for players, retrieve their basic statistics,
    and get lists of their match URLs. It uses Selenium with undetected Chrome driver
    to scrape data from the HLTV website.
    """
    def __init__(self, player_name:str|None = None, player_id:int|None = None):
        """
        Initialize the HLTV player stat scraper.
        
        Parameters
        ----------
        player_name : str or None, optional
            The name of the player to scrape stats for
        player_id : int or None, optional
            The HLTV ID of the player
            
        Attributes
        ----------
        matches : list
            List to store match data
        _config : object
            Configuration settings for the scraper
        logger : Logger
            Logger instance for logging events
        _driver : WebDriver
            Selenium WebDriver instance
        player_name : str or None
            Name of the player being scraped. You may forcely set this parameter, for some players which may not be searched.
        player_id : int or None
            ID of the player being scraped. You may forcely set this parameter, for some players which may not be searched.
        """
        self.matches = []
        self._config = get_scraper_config()
        self.logger = get_logger(__name__, self._config.LOG_FILE)
        self._driver = self._get_driver()
        self.player_name = player_name
        self.player_id = player_id

        self.logger.info("HLTV_Player_Stat_Scraper initialized")

    def _get_driver(self):
        """
        Initialize and configure the Chrome WebDriver.
        
        Returns
        -------
        WebDriver
            Configured Chrome WebDriver instance
        """
        options = Options()
        options.page_load_strategy = self._config.page_load_strategy
        if self._config.headless:
            options.add_argument("--headless")
        driver = uc.Chrome(options=options)
        self.logger.info("Driver initialized")
        return driver
    
    @exponential_backoff(logger_getter=lambda self: self.logger, max_retries=5, exponential_wait_time=5.5)
    def search_player(self, player_name:str|None) -> str | None:
        """
        This function will search for a player by name. This function DOES NOT ensure that you can get the exact player you want: 
        e.g. you can search 'niko', but this function will return `Nikola 'NiKo' Kovač` instead of Nikolaj 'niko' Kristensen.
        It follows the ranking on HLTV.

        Parameters
        -------
        player_name: str | None
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
        self._driver.get(search_page) # It seems that this page is not protected by Cloudflare?
        search_selector_path = 'body > div.bgPadding > div.widthControl > div:nth-child(2) > div.contentCol > div.search > table:nth-child(4) > tbody > tr:nth-child(2) > td > a'
        player_url = self._driver.find_element(By.CSS_SELECTOR, search_selector_path).get_attribute('href')
        if player_url is None:
            self.logger.error(f"Player {player_name} not found")
            return None
        self.logger.info(f"Found player: {player_url}")
        self.parse_player_website(player_url)
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
        None.
        """
        self.logger.info(f"Parsing player: {player_url}")
        player_url = player_url.lstrip(self._config.BASE_URL + '/player/')
        player_id, player_name = player_url.split('/')
        self.player_id = player_id
        self.player_name = player_name
        self.logger.info(f"Player ID: {self.player_id}, Player Name: {self.player_name}")

    @exponential_backoff(logger_getter=lambda self: self.logger, max_retries=5, exponential_wait_time=5.5)
    def get_basic_stats(self, stats_filter:Filter) -> dict[str, str]:
        """
        Retrieve basic statistics for the player based on specified filters.
        
        This method scrapes various player statistics including rating, side ratings,
        DPR (Deaths Per Round), KAST, multi-kills, ADR (Average Damage per Round),
        and KPR (Kills Per Round).
        
        Parameters
        ----------
        stats_filter : Filter
            Filter object containing query parameters for HLTV stats filtering
            
        Returns
        -------
        dict[str, str]
            Dictionary containing player statistics with keys:
            - 'rt': Overall rating
            - 't_side_rt': Terrorist side rating
            - 'ct_side_rt': Counter-Terrorist side rating
            - 'round_swing': Round swing percentage
            - 'dpr': Deaths per round
            - 'kast': KAST percentage
            - 'multi_kill': Multi-kill rounds
            - 'adr': Average damage per round
            - 'kpr': Kills per round
        """
        src_url = f"{self._config.BASE_URL}/stats/players/{self.player_id}/{self.player_name}?{str(stats_filter)}"
        self._driver.get(src_url)
        self.logger.info(f"Getting basic stats for player: {self.player_name}")
        selector_paths = {
            'rt':'body > div.bgPadding > div.widthControl > div:nth-child(2) > div.contentCol > div.stats-section.stats-player.stats-player-overview > div.player-summary-stat-box.compact > div.player-summary-stat-box-right > div.player-summary-stat-box-right-middle > div.player-summary-stat-box-rating-wrapper.average > div.player-summary-stat-box-rating-data-text',
            't_side_rt':'body > div.bgPadding > div.widthControl > div:nth-child(2) > div.contentCol > div.stats-section.stats-player.stats-player-overview > div.player-summary-stat-box.compact > div.player-summary-stat-box-right > div.player-summary-stat-box-right-middle > div.player-summary-stat-box-side-rating.t-rating > div',
            'ct_side_rt':'body > div.bgPadding > div.widthControl > div:nth-child(2) > div.contentCol > div.stats-section.stats-player.stats-player-overview > div.player-summary-stat-box.compact > div.player-summary-stat-box-right > div.player-summary-stat-box-right-middle > div.player-summary-stat-box-side-rating.ct-rating > div',
            'round_swing':'body > div.bgPadding > div.widthControl > div:nth-child(2) > div.contentCol > div.stats-section.stats-player.stats-player-overview > div.player-summary-stat-box.compact > div.player-summary-stat-box-right > div.player-summary-stat-box-right-bottom > div:nth-child(1) > div.player-summary-stat-box-data',
            'dpr':'body > div.bgPadding > div.widthControl > div:nth-child(2) > div.contentCol > div.stats-section.stats-player.stats-player-overview > div.player-summary-stat-box.compact > div.player-summary-stat-box-right > div.player-summary-stat-box-right-bottom > div:nth-child(2) > div.player-summary-stat-box-data.traditionalData',
            'kast':'body > div.bgPadding > div.widthControl > div:nth-child(2) > div.contentCol > div.stats-section.stats-player.stats-player-overview > div.player-summary-stat-box.compact > div.player-summary-stat-box-right > div.player-summary-stat-box-right-bottom > div:nth-child(3) > div.player-summary-stat-box-data.traditionalData',
            'multi_kill':'body > div.bgPadding > div.widthControl > div:nth-child(2) > div.contentCol > div.stats-section.stats-player.stats-player-overview > div.player-summary-stat-box.compact > div.player-summary-stat-box-right > div.player-summary-stat-box-right-bottom > div:nth-child(4) > div.player-summary-stat-box-data.traditionalData',
            'adr':'body > div.bgPadding > div.widthControl > div:nth-child(2) > div.contentCol > div.stats-section.stats-player.stats-player-overview > div.player-summary-stat-box.compact > div.player-summary-stat-box-right > div.player-summary-stat-box-right-bottom > div:nth-child(5) > div.player-summary-stat-box-data.traditionalData',
            'kpr':'body > div.bgPadding > div.widthControl > div:nth-child(2) > div.contentCol > div.stats-section.stats-player.stats-player-overview > div.player-summary-stat-box.compact > div.player-summary-stat-box-right > div.player-summary-stat-box-right-bottom > div:nth-child(6) > div.player-summary-stat-box-data.traditionalData',
        }
        stats = {key:self._driver.find_element(By.CSS_SELECTOR, value).text.split("\n")[0] for key, value in selector_paths.items()}
        self.logger.info(f"Basic stats of {self.player_name} has been retrieved: {visualize_player_stats(stats)}")
        return stats


    def get_match_urls(self, match_filter:Filter) -> list[str]:
        """
        Retrieve URLs for all matches played by the player based on specified filters.
        
        This method paginates through the match history and collects URLs for individual
        match pages. It handles pagination automatically by incrementing the offset
        parameter until all matches are collected.
        
        Parameters
        ----------
        match_filter : Filter
            Filter object containing query parameters for HLTV match filtering
            
        Returns
        -------
        list[str]
            List of URLs for individual match pages
        """
        match_table_selector_path = 'body > div.bgPadding > div.widthControl > div:nth-child(2) > div.contentCol > div.stats-section.stats-player.stats-player-matches > table > tbody'
        offset = 0
        matches = []
        self.logger.info(f"Getting matches of {self.player_name}")
        @exponential_backoff(logger_getter=lambda scraper_instance: scraper_instance.logger, max_retries=5, exponential_wait_time=5.5)
        def get_matches_from_url(scraper_instance, offset: int = 0):
            if offset == 0:
                src_url = f"{self._config.BASE_URL}/stats/players/matches/{self.player_id}/{self.player_name}?{str(match_filter)}"
            else:
                src_url = f"{self._config.BASE_URL}/stats/players/matches/{self.player_id}/{self.player_name}?offset={offset}&{str(match_filter)}"
            self._driver.get(src_url)
            self._driver.find_element(By.CSS_SELECTOR, match_table_selector_path)
            # And by now we ensure that the page is loaded
            this_page_matches = []
            for i in range(1, 101): # HLTV match page is ranging from 1 to 100
                try:
                    match_url = self._driver.find_element(By.CSS_SELECTOR, f"{match_table_selector_path} > tr:nth-child({i}) > td:nth-child(1) > a").get_attribute('href')
                    this_page_matches.append(match_url)
                except selenium.common.exceptions.NoSuchElementException:
                    break
            self.logger.info(f"Matches in sub-pages of {self.player_name} with offset = {offset} has been retrieved: {len(this_page_matches)}")
            return this_page_matches
        while (result := get_matches_from_url(self, offset)) != []:
            matches.extend(result)
            if len(result) < 100: # If there is less than 100 matches in the page, we know that we have reached the end of the page
                break
            offset += 100
        self.logger.info(f"Total matches of {self.player_name} has been retrieved: {len(matches)}")
        return matches

def main():
    """
    Main function demonstrating usage of the HLTV_Player_Stat_Scraper class.
    
    This function shows how to:
    1. Create a scraper instance
    2. Search for a player by name
    3. Parse player information from URL
    4. Retrieve player statistics with filters
    5. Get list of match URLs with filters
    
    Example
    -------
    >>> # Results can be used with match.py to get detailed match information
    """
    # search certain player
    scraper = HLTV_Player_Stat_Scraper()
    player_name = 'NiKo'
    player_url = scraper.search_player(player_name)
    # parse player's website -> matches
    if player_url is None:
        print("Player not found")
        return
    scraper.parse_player_website(player_url) # This has been merged into search_player procedure, but you can do it manually.
    stat = scraper.get_basic_stats(
        stats_filter = Filter(
            quick_time_filter='Last Month',
            ranking='Top5'            
        )
    )
    matches = scraper.get_match_urls(
        match_filter = Filter(
            ranking='Top5'        
        )
    )
    # These matches could be further passed to `match.py` to get more details.


if __name__ == '__main__':
    main()
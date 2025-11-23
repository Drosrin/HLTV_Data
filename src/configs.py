from typing import Set, Literal
from attr import dataclass
from datetime import datetime, timedelta
import yaml

CONFIG_FILE = "config/config.yaml"

@dataclass
class ScraperConfig:
    chrome_driver_path:str
    page_load_strategy:str
    headless: bool
    
    BASE_URL:str = 'https://www.hltv.org'
    LOG_FILE:str = 'logs/' + datetime.now().strftime("%Y-%m-%d")

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)


@dataclass
class PlayerConfig:
    pass

@dataclass
class MatchConfig:
    pass

class Filter:
    map_names = Literal["All", "de_ancient", "de_dust2", "de_inferno", "de_mirage", "de_nuke", "de_overpass", "de_train", "de_anubis", "de_vertigo", "de_cache", "de_cobblestone"]
    quick_time_filter:Literal["All", "Last Month", "Last 3 Months", "Last 6 Months", "Last 12 Months"]
    start_date:datetime
    end_date:datetime
    match_type:str # Majors, BigEvents, Lan, Online
    cs_version:str # CSGO, CS2
    maps:Set[map_names] # de_[map_name]
    ranking:str    # Top5, Top10, Top20, Top30, Top50

    def __init__(self, 
                 quick_time_filter:Literal["All", "Last Month", "Last 3 Months", "Last 6 Months", "Last 12 Months"] = "All", 
                 start_date:datetime = datetime.min, 
                 end_date:datetime = datetime.max, 
                 match_type:Literal["All", "Majors", "BigEvents", "Lan", "Online"] = "All", 
                 cs_version:Literal["All", "CSGO", "CS2"] = "All", 
                 maps:Set[map_names] = {"All"},
                 ranking:Literal["All", "Top5", "Top10", "Top20", "Top30", "Top50"] = "All"):
        """
        Filter for match search, player stat search, etc.

        Parameters
        ----------
        quick_time_filter : str
            Easy for user to select time range. Including Last Month, Last 3 Months, Last 6 Months, Last 12 Months. Will override start_date and end_date.
            If quick_time_filter is None, start_date and end_date will be used.
        All other parameters below can be seen on HLTV, refer to www.hltv.org/stats/players/matches/21266/1eer as an example.
        - start_date : datetime
        - end_date : datetime
        - match_type : str
        - cs_version : str
        - maps : Set[str]
        - ranking : str

        Returns
        -------
        None
        """
        self.quick_time_filter = quick_time_filter
        if quick_time_filter is not None:
            match quick_time_filter:
                case "All":
                    self.start_date = datetime.min
                    self.end_date = datetime.now()
                case "Last Month":
                    self.start_date = datetime.now() - timedelta(days=30)
                    self.end_date = datetime.now()
                case "Last 3 Months":
                    self.start_date = datetime.now() - timedelta(days=90)
                    self.end_date = datetime.now()
                case "Last 6 Months":
                    self.start_date = datetime.now() - timedelta(days=180)
                    self.end_date = datetime.now()
                case "Last 12 Months":
                    self.start_date = datetime.now() - timedelta(days=365)
                    self.end_date = datetime.now()
        else:
            self.start_date = start_date
            self.end_date = end_date
        self.match_type = match_type
        self.cs_version = cs_version
        self.maps = maps
        self.ranking = ranking


    def __str__(self):
        query = {}
        if self.quick_time_filter != 'All':
            query["startDate"] = self.start_date.strftime("%Y-%m-%d")
            query["endDate"] = self.end_date.strftime("%Y-%m-%d")
        if self.match_type != 'All':
            query["matchType"] = self.match_type
        if self.cs_version != 'All':
            query["csVersion"] = self.cs_version
        if "All" not in self.maps:
            query["maps"] = "&".join([ n_map for n_map in self.maps ])
        if self.ranking != 'All':
            query["rankingFilter"] = self.ranking
        query_string = "&".join([f"{key}={value}" for key, value in query.items()])
        return query_string

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
import unittest
from Scrapers.afl_web_scraper import AFLWebScraper

class TESTAFLWEBSCRAPER(unittest.TestCase):



    def test_scrape_team_ratings(self):
        afl = AFLWebScraper()
        afl.scrape_team_ratings(afl.AFL_2021_URL_NUMBER, afl.AFL_2021_TEAM_STATS_CSV_NAME)

    def test_scrape_win_lose(self):
        afl = AFLWebScraper()
        afl.scrape_afl_season_win_lose_stats('34', afl.AFL_2021_FIXTURE_CSV_NAME)


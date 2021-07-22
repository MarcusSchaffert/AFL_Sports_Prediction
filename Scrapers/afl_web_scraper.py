from Scrapers.web_scraper import WebScraper


class AFLWebScraper(WebScraper):
    'https://www.afl.com.au/fixture?Competition=1&CompSeason=20&MatchTimezone=MY_TIME&Regions=2&ShowBettingOdds=1&GameWeeks=18&Teams=1&Venues=13#byround'
    AFL_2021_URL_NUMBER = '34'
    AFL_2020_URL_NUMBER = '20'
    AFL_SEASON_FIRST_BIT = 'https://www.afl.com.au/fixture?Competition=1&CompSeason='
    AFL_SEASON_SECOND_BIT = '&MatchTimezone=MY_TIME&Regions=2&ShowBettingOdds=1&GameWeeks='
    AFL_SEASON_THIRD_BIT = '&Teams=1&Venues=13#byround'
    AFL2020SEASONURLFIRSTHALF = 'https://www.afl.com.au/fixture?Competition=1&CompSeason=20&MatchTimezone=MY_TIME&Regions=2&ShowBettingOdds=1&GameWeeks='
    AFL2020SEASONURLSECONDHALF = '&Teams=1&Venues=13#byround'
    FIRSTROUND = '1'
    AFLTEAMRATINGSFIRSTHALF = 'https://www.afl.com.au/stats/team-rankings?CompSeason='
    AFLTEAMRATINGSSECONDHALF = '&GameWeeks=-1'

    TEAM_NAME_ELEMENT_CLASS = 'match-team__name'
    TOTAL_POINTS_ELEMNT_CLASS = 'match-scoreboard__score-total'
    TEAM_STATS_TEAM_ELEMEMT_CLASS_NAME = 'u-hide-tablet'
    TEAM_STATS_STAT_ELEMENT_CLASS_NAME = 'team-rankings__inner-data-value'
    TEAM_STATS_DATE_ELEMENT_CLASS_NAME = 'match-list__group-date'

    TEAM_STATS_HEADERS = ['Team', 'Kicks', 'Handballs', 'Disposals', 'Marks', 'Hit_outs', 'Frees_For', 'Frees_Against',
                          'Goals', 'Behinds', 'AFL_Fantasy']

    LAST_ROUND_OF_SEASON_2020 = 18
    LAST_ROUND_NORMAL_SEASON = 23

    AFL_2020_TEAM_STATS_CSV_NAME = 'AFL_2020_Team_Stats.csv'
    AFL_2021_TEAM_STATS_CSV_NAME = 'AFL_2021_Team_Stats.csv'

    AFL_2020_FIXTURE_CSV_NAME = 'AFL_2020_Fixture_Results.csv'
    AFL_2021_FIXTURE_CSV_NAME = 'AFL_2021_Fixture_Results.csv'

    CURRENT_ROUND = '14'

    round_counter = None
    team_name = None
    scores = None
    dates = None

    def __init__(self):
        url = self.AFL2020SEASONURLFIRSTHALF + self.FIRSTROUND + self.AFL2020SEASONURLSECONDHALF
        super(AFLWebScraper, self).__init__(url)
        self.round_counter = 1
        self.team_name = []
        self.scores = []
        self.dates = []

    def scrape_afl_season_win_lose_stats(self, afl_season_url_number, csv_name):
        # need to know season number because that number determines the url associated with the fixture results of
        # a particular season
        # for example: https://www.afl.com.au/fixture?Competition=1&CompSeason=20&MatchTimezone=MY_TIME&Regions=2&ShowBettingOdds=1&GameWeeks=2&Teams=1&Venues=13#byround
        # where it says CompSeason=20, 20 is the unique identifier. In this instance it refers to the 2020 season.
        assert isinstance(afl_season_url_number, str)
        for i in range(1, self.LAST_ROUND_NORMAL_SEASON + 1):
            url = self.AFL_SEASON_FIRST_BIT + afl_season_url_number + self.AFL_SEASON_SECOND_BIT\
                  + str(i) + self.AFL_SEASON_THIRD_BIT
            self.set_url_to_scrape(url)

            for div in self.soup.find(self.DIV_ELEMENT, {self.ELEMENT_CLASS: self.TEAM_STATS_DATE_ELEMENT_CLASS_NAME}):
                self.dates.append(div.getText())


            for div in self.soup.findAll(self.DIV_ELEMENT, {self.ELEMENT_CLASS: self.TEAM_NAME_ELEMENT_CLASS}):
                self.team_name.append(div.getText())

            for span in self.soup.findAll(self.SPAN_ELEMENT, {self.ELEMENT_CLASS : self.TOTAL_POINTS_ELEMNT_CLASS}):
                self.scores.append(span.getText())

            # have to update constant CURRENT_ROUND to reflect the current round
            if str(i) == self.CURRENT_ROUND:
                break

        self.headers = ['Date', 'Home_Team', 'Home_Team_Score', 'Away_Team', 'Away_Team_Score']

        # organise the scraped data
        for index, value in enumerate(self.scores):
            self.rows_data.append(self.dates[index])
            self.rows_data.append(self.team_name[index])
            self.rows_data.append(value)

        self.create_dataframe_from_scraped_table_data(self.rows_data, self.headers)
        self.save_dataframe(csv_name)
        self.rows_data = []
        self.reset_variables()

    def scrape_team_ratings(self, afl_season_url_number, csv_name):
        # if you wanted to scrape data from the 2020 AFL season then you would use a url like the one
        # constructed below
        #url = self.AFLTEAMRATINGSFIRSTHALF + '20' + self.AFLTEAMRATINGSSECONDHALF
        # year does not necessarily correlate with url, as seen below: '34'
        assert isinstance(afl_season_url_number, str)
        url = self.AFLTEAMRATINGSFIRSTHALF + afl_season_url_number + self.AFLTEAMRATINGSSECONDHALF
        self.set_url_to_scrape(url)
        team_names_list = []
        scores_list = []
        for span in self.soup.findAll(self.SPAN_ELEMENT, {self.ELEMENT_CLASS: self.TEAM_STATS_TEAM_ELEMEMT_CLASS_NAME}):
            # skip every second element because dont need that text value
            team_names_list.append(span.getText())
        for span in self.soup.findAll(self.SPAN_ELEMENT, {self.ELEMENT_CLASS: self.TEAM_STATS_STAT_ELEMENT_CLASS_NAME}):
            scores_list.append(span.getText())

        final_scores_list = []
        for index, score in enumerate(scores_list):
            if index % 2 == 0:
                final_scores_list.append(score)

        team_list_counter = 0
        for index, score in enumerate(final_scores_list):
            if team_list_counter == 0:
                self.rows_data.append(team_names_list[index])
                team_list_counter += 1
            elif index % 10 == 0:
                self.rows_data.append(team_names_list[team_list_counter])
                team_list_counter += 1
            self.rows_data.append(score)

        self.create_dataframe_from_scraped_table_data(self.rows_data, self.TEAM_STATS_HEADERS)
        self.save_dataframe(csv_name)
        self.reset_variables()








if __name__ == '__main__':
    afls = AFLWebScraper()
    afls.scrape_afl_season_win_lose_stats(afls.AFL_2021_URL_NUMBER, afls.AFL_2021_FIXTURE_CSV_NAME)



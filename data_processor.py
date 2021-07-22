import pandas as pd
from Scrapers.afl_web_scraper import AFLWebScraper


class DataProcessor:
    AFL_2020_FIXTURE_CSV = 'AFL_2020_Fixture_Results.csv'
    AFL_2020_TEAM_STATS_CSV = 'AFL_2020_Team_Stats.csv'

    df_afl_2020_fixture = None
    df_afl_2020_team_stats = None

    df_final_team_stats = None
    df_final_fixture = None

    afl_web_scraper = None

    TEAM_COLUMN_STATS = 'Team'
    HOME_TEAM_COLUMN = 'Home_Team'
    AWAY_TEAM_COLUMN = 'Away_Team'
    HOME_TEAM_SCORE = 'Home_Team_Score'
    AWAY_TEAM_SCORE = 'Away_Team_Score'
    HOME = 'home'
    AWAY = 'away'

    FINAL_CSV_NAME = "2021_2020_afl_season_and_stats.csv"

    df_team_stats_combine = None
    df_fixture_combine = None

    def __init__(self):
        self.df_afl_2020_fixture = pd.read_csv(self.AFL_2020_FIXTURE_CSV)
        self.df_afl_2020_team_stats = pd.read_csv(self.AFL_2020_TEAM_STATS_CSV)
        self.afl_web_scraper = AFLWebScraper()

    # may have to change the type to be able to add dataframes together
    def combine_team_stats(self):
        self.afl_web_scraper.scrape_team_ratings(self.afl_web_scraper.AFL_2021_URL_NUMBER,
                                                 self.afl_web_scraper.AFL_2021_TEAM_STATS_CSV_NAME)
        df_2021_team_ratings = self.afl_web_scraper.df
        team_column = self.df_afl_2020_team_stats[self.TEAM_COLUMN_STATS]
        self.df_team_stats_combine = df_2021_team_ratings.copy()
        for column in df_2021_team_ratings.columns:
            # skip team names column
            if column == self.TEAM_COLUMN_STATS:
                continue
            self.df_team_stats_combine[column] = self.df_team_stats_combine[column].astype(float)
            self.df_team_stats_combine[column] += self.df_afl_2020_team_stats[column].astype(float)
            self.df_team_stats_combine[column] = self.df_team_stats_combine[column] / 2
        self.df_team_stats_combine[self.TEAM_COLUMN_STATS] = \
            self.df_team_stats_combine[self.TEAM_COLUMN_STATS].str.strip()

    def normalise_combined_team_stats(self):
        assert isinstance(self.df_team_stats_combine, pd.DataFrame)
        for column in self.df_team_stats_combine.columns:
            # skip team names column
            if column == self.TEAM_COLUMN_STATS:
                continue
            self.df_team_stats_combine[column] = (self.df_team_stats_combine[column] - self.df_team_stats_combine[
                column].min()) / \
                                                 (self.df_team_stats_combine[column].max() - self.df_team_stats_combine[
                                                     column].min())

    def combine_season_fixtures(self):
        self.afl_web_scraper.scrape_afl_season_win_lose_stats(self.afl_web_scraper.AFL_2021_URL_NUMBER,
                                                              self.afl_web_scraper.AFL_2021_FIXTURE_CSV_NAME)
        df_afl_2021_fixture = self.afl_web_scraper.df.copy()
        self.df_fixture_combine = self.df_afl_2020_fixture.append(df_afl_2021_fixture)
        self.df_fixture_combine[self.HOME_TEAM_COLUMN] = self.df_fixture_combine[self.HOME_TEAM_COLUMN].str.strip()
        self.df_fixture_combine[self.AWAY_TEAM_COLUMN] = self.df_fixture_combine[self.AWAY_TEAM_COLUMN].str.strip()
        self.df_fixture_combine.reset_index(inplace=True)

    def combine_fixture_and_stats(self):
        assert isinstance(self.df_fixture_combine, pd.DataFrame)
        assert isinstance(self.df_team_stats_combine, pd.DataFrame)
        for index, row in self.df_team_stats_combine.iterrows():
            mask_home = self.df_fixture_combine[self.HOME_TEAM_COLUMN] == row[self.TEAM_COLUMN_STATS]
            mask_away = self.df_fixture_combine[self.AWAY_TEAM_COLUMN] == row[self.TEAM_COLUMN_STATS]
            for column in self.df_team_stats_combine.columns:
                if (column == self.HOME_TEAM_COLUMN) | (column == self.AWAY_TEAM_COLUMN):
                    continue
                self.df_fixture_combine.loc[mask_home, self.HOME + '_' + column] = row[column]
                self.df_fixture_combine.loc[mask_away, self.AWAY + '_' + column] = row[column]


    def create_target(self):
        mask_home_win = self.df_fixture_combine[self.HOME_TEAM_SCORE] > self.df_fixture_combine[self.AWAY_TEAM_SCORE]
        self.df_fixture_combine.loc[mask_home_win, 'home_win_lose'] = 1
        self.df_fixture_combine.loc[mask_home_win, 'away_win_lose'] = 0
        mask_away_win = self.df_fixture_combine[self.HOME_TEAM_SCORE] < self.df_fixture_combine[self.AWAY_TEAM_SCORE]
        self.df_fixture_combine.loc[mask_away_win, 'away_win_lose'] = 1
        self.df_fixture_combine.loc[mask_away_win, 'home_win_lose'] = 0
        mask_draw = self.df_fixture_combine[self.HOME_TEAM_SCORE] == self.df_fixture_combine[self.AWAY_TEAM_SCORE]
        self.df_fixture_combine.loc[mask_draw, 'away_win_lose'] = 0
        self.df_fixture_combine.loc[mask_draw, 'home_win_lose'] = 0

    def save_processed_dataframe(self, csv_name):
        self.df_fixture_combine.to_csv(csv_name, index=False)


if __name__ == '__main__':
    dp = DataProcessor()
    dp.combine_team_stats()
    dp.normalise_combined_team_stats()
    dp.combine_season_fixtures()
    dp.combine_fixture_and_stats()
    dp.create_target()
    dp.save_processed_dataframe(dp.FINAL_CSV_NAME)
    dp.afl_web_scraper.end_scraper()

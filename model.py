import pandas as pd
import numpy as np


class Model:

    # constant for the test user login info
    TEST_USERNAME = 'admin'
    TEST_PASSWORD = '123'

    # column name constants
    ANIME_ID = 'anime_id'
    NAME = 'name'
    GENRE = 'genre'
    TYPE = 'type'
    RATING = 'rating'
    A_RATING = 'a_rating'
    P_RATING = 'p_rating'
    USER_ID = 'user_id'
    C_SCORE = 'c_score'
    R_SCORE = 'r_score'
    COMBINED_SCORE = 'combined_score'
    EPISODES = 'episodes'
    MEMBERS = 'members'
    VIEW_COUNT = 'view_count'

    # dataframe datatype constants
    ANIME_DTYPES = {ANIME_ID: int, NAME: str, GENRE: str, TYPE: str, RATING: float}
    RATING_DTYPES = {ANIME_ID: int, USER_ID: int, RATING: int}
    P_RATING_DTYPES = {ANIME_ID: int, P_RATING: float}
    GENRE_DTYPES = {GENRE: str, VIEW_COUNT: int}

    # csv path constants
    ANIME_PATH = "Data/clean_anime.csv"
    RATING_PATH = "Data/clean_rating.csv"
    CONTENT_CORR_PATH = "Data/content_correlation.csv"
    RATING_CORR_PATH = "Data/rating_correlation.csv"
    P_RATING_PATH = "Data/predicted_ratings.csv"
    GENRE_VIEWS_PATH = "Data/genre_views.csv"

    # catalog info constants
    ORIGINAL_CATALOG_ANIME_IDS = [127, 135, 191, 246, 345, 759, 809, 817, 2376]
    ANIFLIX_A_RATINGS = [8.34, 8.30, 8.14, 5.05, 4.91, 2.7, 2.47, 7.87, 5.42]

    # similarity score weights -- used when computing the combined similarity score
    C_SCORE_WEIGHT = 0.22
    R_SCORE_WEIGHT = 0.78

    def __init__(self):
        # declare class variables
        self.anime_df = None
        self.rating_df = None
        self.content_corr_df = None
        self.rating_corr_df = None
        self.p_rating_df = None
        self.genre_views_df = None

        # initialize Aniflix catalog average rating dataframe
        self.a_rating_df = pd.DataFrame({Model.ANIME_ID: Model.ORIGINAL_CATALOG_ANIME_IDS, Model.A_RATING: Model.ANIFLIX_A_RATINGS})
        self.new_catalog_ids = []

    # reads all CSVs needed for the application
    def load_data(self):
        self.anime_df = pd.read_csv(Model.ANIME_PATH, dtype=Model.ANIME_DTYPES, low_memory=False)
        self.rating_df = pd.read_csv(Model.RATING_PATH, dtype=Model.RATING_DTYPES, low_memory=False)
        self.content_corr_df = pd.read_csv(Model.CONTENT_CORR_PATH, header=0)
        self.rating_corr_df = pd.read_csv(Model.RATING_CORR_PATH)
        self.p_rating_df = pd.read_csv(Model.P_RATING_PATH, dtype=Model.P_RATING_DTYPES)
        self.genre_views_df = pd.read_csv(Model.GENRE_VIEWS_PATH, dtype=Model.GENRE_DTYPES)

    # gets the most viewed genres as a dataframe
    def get_top_genre_views(self, head=5):
        genre_views_df = self.genre_views_df.sort_values([Model.VIEW_COUNT], ascending=False)
        return genre_views_df.head(head)

    # checks login info against TEST_USERNAME and TEST_PASSWORD
    @staticmethod
    def validate_login_info(login_info):
        if login_info[0] == Model.TEST_USERNAME and login_info[1] == Model.TEST_PASSWORD:
            return True
        else:
            return False

    # adds a new id the to new_catalog_ids list
    def add_animes_to_catalog(self, anime_ids):
        for anime_id in anime_ids:
            if anime_id not in self.new_catalog_ids:
                self.new_catalog_ids.append(anime_id)

    # removes an id from the new_catalog_ids list -- does not allow removal of original catalog anime ids
    def remove_animes_from_catalog(self, anime_ids):
        for anime_id in anime_ids:
            if anime_id in Model.ORIGINAL_CATALOG_ANIME_IDS:
                print("cannot remove original catalog items")
            else:
                try:
                    self.new_catalog_ids.remove(anime_id)
                except Exception as e:
                    print("Failed to remove anime_id=", anime_id, " from catalog")

    # empties the new_catalog_ids list
    def reset_catalog(self):
        self.new_catalog_ids = []

    # creates a dict showing the number of MyAnimeList members that view the original anime, new anime, or both
    def calc_shared_users(self):
        users_df = self.rating_df[[Model.ANIME_ID, Model.USER_ID]]
        current_users_df = users_df.loc[users_df[Model.ANIME_ID].isin(self.ORIGINAL_CATALOG_ANIME_IDS)]
        current_users_df = current_users_df[Model.USER_ID]

        new_users_df = users_df.loc[users_df[Model.ANIME_ID].isin(self.new_catalog_ids)]
        new_users_df = new_users_df[Model.USER_ID]

        shared_users = current_users_df.loc[current_users_df.isin(new_users_df)]
        current_users = current_users_df.loc[~current_users_df.isin(new_users_df)]
        new_users = new_users_df.loc[~new_users_df.isin(current_users_df)]

        return {'original': current_users.size, 'shared': shared_users.size, 'new': new_users.size}

    # creates the similarity dataframe -- this dataframe combines all of the information available on anime that can be added to catalog
    # this includes rating similarity scores, content similarity scores, calculates combined similarity scores, and shows predicted ratings
    def create_sim_df(self, anime_ids=None, sort_by=None, ascending=False):
        if sort_by is None:
            sort_by = Model.C_SCORE
        if anime_ids is None:
            anime_ids = Model.ORIGINAL_CATALOG_ANIME_IDS

        # find content similarity and rating similarity scores, then calculate the combined similarity score
        c_score_s = self.content_corr_df.iloc[:, anime_ids].sum(axis=1)
        r_score_s = self.rating_corr_df.iloc[:, anime_ids].sum(axis=1)
        combined_score_s = c_score_s * Model.C_SCORE_WEIGHT + r_score_s * Model.R_SCORE_WEIGHT

        # merge sim scores and anime_df data
        score_df = pd.DataFrame(
            {Model.C_SCORE: c_score_s, Model.R_SCORE: r_score_s, Model.COMBINED_SCORE: combined_score_s})
        score_df.index.name = Model.ANIME_ID
        score_df.reset_index(inplace=True)

        print(score_df)

        temp_df = pd.merge(score_df, self.p_rating_df, on=Model.ANIME_ID)
        sim_df = pd.merge(temp_df, self.anime_df, on=Model.ANIME_ID)

        sim_df.sort_values([sort_by], ascending=ascending, inplace=True)

        # remove anime that are already in the catalog
        sim_df = sim_df.loc[~sim_df[Model.ANIME_ID].isin(Model.ORIGINAL_CATALOG_ANIME_IDS + self.new_catalog_ids)]

        # round scores and ratings
        sim_df[Model.C_SCORE] = sim_df[Model.C_SCORE].round(2)
        sim_df[Model.R_SCORE] = sim_df[Model.R_SCORE].round(2)
        sim_df[Model.COMBINED_SCORE] = sim_df[Model.COMBINED_SCORE].round(2)
        sim_df[Model.P_RATING] = sim_df[Model.P_RATING].round(2)

        return sim_df[[
            Model.ANIME_ID,
            Model.NAME,
            Model.GENRE,
            Model.TYPE,
            Model.EPISODES,
            Model.MEMBERS,
            Model.RATING,
            Model.C_SCORE,
            Model.R_SCORE,
            Model.COMBINED_SCORE,
            Model.P_RATING
        ]]

    # creates the catalog df using the ORIGINAL_CATALOG_ANIME_IDS and new_catalog_anime_ids lists
    def create_catalog_df(self, sort_by=None, ascending=False, separate=True):
        if sort_by is None:
            sort_by = Model.ANIME_ID
            ascending = True

        original_catalog_df = self._create_original_catalog_df()
        new_catalog_df = self._create_new_catalog_df()
        catalog_df = None

        # sort the original and new anime separately
        if separate:
            original_catalog_df.sort_values([sort_by], ascending=ascending, inplace=True)
            new_catalog_df.sort_values([sort_by], ascending=ascending, inplace=True)

            catalog_df = pd.concat([original_catalog_df, new_catalog_df], ignore_index=True)
        # sort the original and new anime together
        else:
            catalog_df = pd.concat([original_catalog_df, new_catalog_df], ignore_index=True)
            catalog_df.sort_values([sort_by], ascending=ascending, inplace=True)

        return catalog_df[[
            Model.ANIME_ID,
            Model.NAME,
            Model.GENRE,
            Model.TYPE,
            Model.EPISODES,
            Model.P_RATING,
            Model.A_RATING
        ]]

    # create dataframe using the ORIGINAL_CATALOG_ANIME_IDS list
    def _create_original_catalog_df(self):
        original_catalog_df = pd.merge(self.a_rating_df, self.anime_df, on=Model.ANIME_ID)
        original_catalog_df = original_catalog_df.reindex(columns=original_catalog_df.columns.tolist() + [Model.P_RATING])

        return original_catalog_df

    # create dataframe using the new_catalog_anime_ids list
    def _create_new_catalog_df(self):
        new_catalog_df = self.anime_df.loc[(self.anime_df[Model.ANIME_ID].isin(self.new_catalog_ids))]
        new_catalog_df = pd.merge(new_catalog_df, self.p_rating_df, on=Model.ANIME_ID)
        new_catalog_df = new_catalog_df.reindex(columns=new_catalog_df.columns.tolist() + [Model.A_RATING])

        new_catalog_df[Model.P_RATING] = new_catalog_df[Model.P_RATING].round(2)

        return new_catalog_df

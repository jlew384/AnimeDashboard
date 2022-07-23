from model import Model
from view import View
import logging


class Controller:

    def __init__(self):
        # setup the logging tool
        logging.basicConfig(filename='Data/app.log', level=logging.INFO, filemode='a', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        try:
            self.model = Model()

            # declare class variables
            self.current_catalog_df = None
            self.current_sim_df = None
            self.shared_users = None
            self.genre_views_df = None

            # initialize default sort settings for the catalog and similarity treeviews
            self.current_catalog_sort = {"sort_by": Model.ANIME_ID, "ascending": True}
            self.current_sim_sort = {"sort_by": Model.P_RATING, "ascending": False}
            self.last_selection = Model.ORIGINAL_CATALOG_ANIME_IDS

            # create the view, display the login form, and begin the main loop
            self.view = View(self)
            self.view.show_login_frame()
            self.view.mainloop()
        except Exception as e:
            logging.error("Exception occurred", exc_info=True)

    # adds the anime selected in the similarity treeview to the catalog dataframe then updates the catalog treeview
    def on_add_button_clicked(self):
        try:
            selection = self.view.get_tv_selection(self.view.sim_tv)
            self.model.add_animes_to_catalog(selection)
            self._on_catalog_changed()
        except Exception as e:
            logging.error("Exception occurred", exc_info=True)

    # removes the anime selected in the catalog treeview from the catalog dataframe then updates the catalog treeview
    def on_remove_button_clicked(self):
        try:
            selection = self.view.get_tv_selection(self.view.catalog_tv)
            self.model.remove_animes_from_catalog(selection)
            self._on_catalog_changed()
        except Exception as e:
            logging.error("Exception occurred", exc_info=True)

    # resets the catalog dataframe to the original anime and update the catalog treeview
    def on_reset_button_clicked(self):
        try:
            self.model.reset_catalog()
            self._on_catalog_changed()
        except Exception as e:
            logging.error("Exception occurred", exc_info=True)

    # creates the new catalog dataframe and updates the catalog treeview
    def _on_catalog_changed(self):
        try:
            sorted_catalog_df = self.model.create_catalog_df(sort_by=self.current_catalog_sort['sort_by'], ascending=self.current_catalog_sort['ascending'])
            self.view.update_tv_rows(self.view.catalog_tv, sorted_catalog_df)
            self.view.create_user_pie_graph(self.model.calc_shared_users())

            self.current_catalog_df = sorted_catalog_df
        except Exception as e:
            logging.error("Exception occurred", exc_info=True)

    # finds new similarity scores based on the selected anime in the catalog treeview then it updates the similarity treeview
    def on_sim_button_clicked(self):
        try:
            selection = self.view.get_tv_selection(self.view.catalog_tv)
            if len(selection) == 0:
                selection = None
            sorted_sim_df = self.model.create_sim_df(selection, sort_by=self.current_sim_sort["sort_by"], ascending=self.current_sim_sort["ascending"])
            self.view.update_tv_rows(self.view.sim_tv, sorted_sim_df)
            self.last_selection = selection
        except Exception as e:
            logging.error("Exception occurred", exc_info=True)

    # sorts the similarity dataframe based on the heading selected, then it updates the similarity treeview rows
    def on_sim_tv_heading_clicked(self, heading):
        try:
            ascending = True
            if self.current_sim_sort['sort_by'] == heading:
                if self.current_sim_sort['ascending'] is True:
                    ascending = False
                else:
                    ascending = True
            self.current_sim_df.sort_values([heading], ascending=ascending, inplace=True)
            self.current_sim_sort['sort_by'] = heading
            self.current_sim_sort['ascending'] = ascending
            self.view.update_tv_rows(self.view.sim_tv, self.current_sim_df)
        except Exception as e:
            logging.error("Exception occurred", exc_info=True)

    # sorts the catalog dataframe based on the heading selected, then it updates the catalog treeview rows
    def on_catalog_tv_heading_clicked(self, heading):
        try:
            ascending = True
            if self.current_catalog_sort['sort_by'] == heading:
                if self.current_catalog_sort['ascending'] is True:
                    ascending = False
                else:
                    ascending = True
            sorted_catalog_df = self.model.create_catalog_df(sort_by=heading, ascending=ascending)
            self.current_catalog_sort['sort_by'] = heading
            self.current_catalog_sort['ascending'] = ascending
            self.view.update_tv_rows(self.view.catalog_tv, sorted_catalog_df)
        except Exception as e:
            logging.error("Exception occurred", exc_info=True)

    # validates the user login information and displays the main application view
    def on_login_button_clicked(self):
        try:
            # check login info
            login_info = self.view.get_login_info()
            if self.model.validate_login_info(login_info):
                # log the login
                logging.info(login_info[0] + " has logged in.")
                # load application data
                self._load_main_frame_data()

                # show main application GUI
                self.view.destroy_login_frame()
                self.view.show_main_frame(self.current_catalog_df, self.current_sim_df, self.shared_users, self.genre_views_df)
            else:
                self.view.show_incorrect_login_message()
        except Exception as e:
            logging.error("Exception occured", exc_info=True)

    # loads all data for the main application
    def _load_main_frame_data(self):
        try:
            self.model.load_data()

            self.current_catalog_df = self.model.create_catalog_df(sort_by=Model.ANIME_ID, ascending=True)
            self.current_sim_df = self.model.create_sim_df(Model.ORIGINAL_CATALOG_ANIME_IDS, sort_by=Model.COMBINED_SCORE,
                                                           ascending=False)

            self.current_catalog_sort = {"sort_by": Model.ANIME_ID, "ascending": True}
            self.current_sim_sort = {"sort_by": Model.COMBINED_SCORE, "ascending": False}
            self.last_selection = Model.ORIGINAL_CATALOG_ANIME_IDS

            self.shared_users = self.model.calc_shared_users()
            self.genre_views_df = self.model.get_top_genre_views()
        except Exception as e:
            logging.error("Exception occured", exc_info=True)


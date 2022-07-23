import tkinter as tk
from tkinter import ttk

from model import Model

import pandas as pd

import matplotlib
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

matplotlib.use("TkAgg")


class View(tk.Tk):

    # constants used to fill large text fields
    DASHBOARD_DESC = ""

    CATALOG_DESC = "The catalog shows the original Aniflix anime(highlighted) and new anime added to the catalog. It also shows the average rating(a_rating) by Aniflix users and the predicted rating(p_rating) for Aniflix users. New anime can be added by selecting one from the Similar Anime list and clicking 'Add to Catalog'"

    USER_PIE_DESC = "This pie graph shows the number of MyAnimeList.net members that view the original anime, new anime, or both in the catalog. This updates as you add anime to the catalog."

    GENRE_BAR_DESC = "This bar graph compares the viewership of the most viewed genres on MyAnimeList.net."

    SIMILARITY_DESC = "The similarity view shows the rating similarity score(r_score), content similarity score(c_score), and the combined similarity score(combined_score) of anime that can be added to the catalog. It also shows the predicted rating(p_rating) for Aniflix users. Click 'Find Similar Anime' to generate new scores based on the selected anime in the catalog."

    # constants for formatting
    STD_FONT = 'TkDefaultFont 9'
    LABEL_FONT = 'TkDefaultFont 12 bold'
    TITLE_FONT = 'TkDefaultFont 18 bold'

    DARK_GREEN = "#094214"
    GREEN = "#19772a"
    BLUE_GREEN = "#113e6d"
    BLUE = "#2f60d8"
    DARK_BLUE = "#112b6d"
    RED = "#7f270c"
    DARK_GREY = "#1c1c1c"

    ENTRY_PAD = 5
    FRAME_PADDING = 10
    BUTTON_PAD = 10
    PIE_PAD = 10

    COLUMN_WIDTHS = {
        Model.ANIME_ID: 60,
        Model.NAME: 200,
        Model.GENRE: 150,
        Model.TYPE: 60,
        Model.RATING: 60,
        Model.USER_ID: 60,
        Model.C_SCORE: 60,
        Model.R_SCORE: 60,
        Model.COMBINED_SCORE: 70,
        Model.A_RATING: 60,
        Model.P_RATING: 70,
        Model.EPISODES: 60,
        Model.MEMBERS: 60
    }

    def __init__(self, controller):
        super().__init__()
        self.controller = controller

        # configure application style
        self.state('zoomed')
        self.pack_propagate(True)
        self.title('Aniflix Dashboard')

        self.tk.call("source", "Sun-Valley-ttk-theme/sun-valley.tcl")
        self.tk.call("set_theme", "dark")
        ttk.Style().map('Treeview', background=[('selected', self.GREEN)])
        ttk.Style().configure('Treeview', rowheight=22)

        # declare class variables
        self.last_tv_clicked = None

        self.login_frame = None
        self.warning_label = None
        self.username_entry = None
        self.password_entry = None

        self.catalog_tv = None
        self.sim_tv = None
        self.user_pie_parent = None
        self.genre_bar_parent = None

    # creates and shows all the widgets for the login screen
    def show_login_frame(self):
        self.login_frame = ttk.Frame(self)
        self.login_frame.place(relx=0.5, rely=0.5, anchor='center')

        heading_label = ttk.Label(self.login_frame, text="Aniflix Dashboard Login", font=View.LABEL_FONT)
        heading_label.grid(row=0, column=0, columnspan=2, padx=View.FRAME_PADDING, pady=View.FRAME_PADDING)

        username_label = ttk.Label(self.login_frame, text="Username:")
        username_label.grid(row=1, column=0)

        self.username_entry = ttk.Entry(self.login_frame)
        self.username_entry.grid(row=1, column=1, padx=View.ENTRY_PAD, pady=View.ENTRY_PAD)

        password_label = ttk.Label(self.login_frame, text="Password:")
        password_label.grid(row=2, column=0)

        self.password_entry = ttk.Entry(self.login_frame)
        self.password_entry.grid(row=2, column=1, padx=View.ENTRY_PAD, pady=View.ENTRY_PAD)

        self.warning_label = ttk.Label(self.login_frame)
        self.warning_label.grid(row=3, column=0, columnspan=2)

        login_button = ttk.Button(self.login_frame, text="Login", width=35, command=self.controller.on_login_button_clicked)
        login_button.grid(row=4, column=0, columnspan=2, padx=View.BUTTON_PAD, pady=View.BUTTON_PAD)

    # allows the controller to retrieve the login info
    def get_login_info(self):
        return [self.username_entry.get(), self.password_entry.get()]

    # shows warning message for when incorrect login info is entered
    def show_incorrect_login_message(self):
        self.warning_label.config(text='Incorrect username and password.')

    # destroys the widget containing the login form -- this is meant to be done after correctly logging in and before showing the main frame widget
    def destroy_login_frame(self):
        self.login_frame.destroy()

    # shows the main frame that contains the main UI for the application
    def show_main_frame(self, catalog_df, similarity_df, user_counts, genre_views_df):

        # create frames for organization
        main_frame = ttk.Frame(self)
        main_frame.pack(padx=self.FRAME_PADDING, pady=self.FRAME_PADDING)

        title_frame = ttk.Frame(main_frame)
        title_frame.grid(sticky="S", row=0, column=0)

        top_frame = ttk.Frame(main_frame)
        top_frame.grid(sticky="W", row=1, column=0)

        control_frame = ttk.Frame(main_frame)
        control_frame.grid(sticky="W", row=2, column=0)

        bottom_frame = ttk.Frame(main_frame)
        bottom_frame.grid(sticky="W", row=3, column=0)

        # create dashboard title label
        title_label = ttk.Label(title_frame, text="Aniflix Recommender Dashboard", font=View.TITLE_FONT)
        title_label.grid(sticky="S", row=0, column=0)

        dashboard_desc = tk.Label(title_frame, text=View.DASHBOARD_DESC, wraplength=1000, font=View.STD_FONT)
        dashboard_desc.grid(row=1, column=0)

        # create catalog label, description, and treeview
        catalog_tv_label = ttk.Label(top_frame, text="Catalog", font=View.LABEL_FONT)
        catalog_tv_label.grid(sticky='s', row=0, column=0)

        catalog_tv_desc = tk.Label(top_frame, text=View.CATALOG_DESC, wraplength=700, font=View.STD_FONT)
        catalog_tv_desc.grid(row=1, column=0)

        self.catalog_tv = self._create_tv(top_frame, catalog_df, left_click_command=self._on_tv_clicked)
        self.catalog_tv.grid(sticky=['w', 's'], row=2, column=0)

        # configure catalog treeview scrollbar
        catalog_scroll = ttk.Scrollbar(top_frame)
        catalog_scroll.configure(command=self.catalog_tv.yview)
        self.catalog_tv.configure(yscrollcommand=catalog_scroll.set)
        catalog_scroll.grid(sticky=['w', 's', 'n'], row=2, column=1)

        # create similarity label, description, and treeview
        sim_tv_label = ttk.Label(bottom_frame, text="Similar Anime", font=View.LABEL_FONT)
        sim_tv_label.grid(sticky='s', row=0, column=0)

        sim_tv_desc = tk.Label(bottom_frame, text=View.SIMILARITY_DESC, wraplength=900, font=View.STD_FONT)
        sim_tv_desc.grid(row=1, column=0)

        self.sim_tv = self._create_tv(parent=bottom_frame, dataframe=similarity_df,
                                      left_click_command=self._on_tv_clicked)
        self.sim_tv.grid(sticky="w", row=2, column=0)

        # configure similarity treeview scrollbar
        sim_scroll = ttk.Scrollbar(bottom_frame)
        sim_scroll.configure(command=self.sim_tv.yview)
        self.sim_tv.configure(yscrollcommand=sim_scroll.set)
        sim_scroll.grid(sticky=['w', 's', 'n'], row=2, column=1)

        # create buttons for adding, removing and resetting anime in the catalog -- also includes button for generating new similarity scores
        add_button = ttk.Button(control_frame, text="Add Anime to Catalog",
                                command=self.controller.on_add_button_clicked)
        add_button.grid(sticky="W", row=0, column=0, padx=View.BUTTON_PAD, pady=View.BUTTON_PAD)

        remove_button = ttk.Button(control_frame, text="Remove Anime from Catalog",
                                   command=self.controller.on_remove_button_clicked)
        remove_button.grid(sticky="W", row=0, column=2, padx=View.BUTTON_PAD, pady=View.BUTTON_PAD)

        reset_button = ttk.Button(control_frame, text="Reset Catalog", command=self.controller.on_reset_button_clicked)
        reset_button.grid(sticky="W", row=0, column=3, padx=View.BUTTON_PAD, pady=View.BUTTON_PAD)

        sim_button = ttk.Button(control_frame, text="Find Similar Anime",
                                command=self.controller.on_sim_button_clicked)
        sim_button.grid(sticky="W", row=0, column=4, padx=View.BUTTON_PAD, pady=View.BUTTON_PAD)

        # create shared user pie graph, label, and description
        user_pie_label = ttk.Label(bottom_frame, text="Shared Users", font=View.LABEL_FONT)
        user_pie_label.grid(sticky='s', row=0, column=2)

        user_pie_desc = tk.Label(bottom_frame, text=View.USER_PIE_DESC, wraplength=350, font=View.STD_FONT)
        user_pie_desc.grid(row=1, column=2)

        self.user_pie_parent = bottom_frame
        self.create_user_pie_graph(user_counts)

        # create genre bar graph, label, description
        genre_bar_label = ttk.Label(top_frame, text="Viewers Per Genre", font=View.LABEL_FONT)
        genre_bar_label.grid(sticky='s', row=0, column=2)

        genre_bar_desc = tk.Label(top_frame, text=View.GENRE_BAR_DESC, wraplength=350, font=View.STD_FONT)
        genre_bar_desc.grid(row=1, column=2)

        self.genre_bar_parent = top_frame
        self.create_genre_bar_graph(genre_views_df)

    # creates the shared user pie graph and displays it in the user_pie_parent widget
    def create_user_pie_graph(self, user_counts):
        fig = plt.Figure(figsize=(4.5, 3), dpi=100, facecolor=self.DARK_GREY)
        plot = fig.add_subplot(111)
        names = list()
        values = list()
        colors = list()

        # fills the names, values and colors lists based on the user_counts input -- some counts may not exist every time this is called
        for key in user_counts.keys():
            if user_counts[key] != 0:
                names.append(key + "=" + str(user_counts[key]))
                values.append(user_counts[key])
                if key == 'original':
                    colors.append(View.DARK_GREEN)
                elif key == 'shared':
                    colors.append(View.BLUE_GREEN)
                elif key == 'new':
                    colors.append(View.BLUE)

        fig.patch.set_facecolor(self.DARK_GREY)
        plt.rcParams['text.color'] = 'white'
        plot.pie(values, labels=names, wedgeprops={'linewidth': 2, 'edgecolor': self.DARK_GREY}, colors=colors)
        canvas = FigureCanvasTkAgg(fig, self.user_pie_parent)
        canvas.get_tk_widget().grid(sticky="E", row=2, column=2, padx=self.PIE_PAD)

    # creates the genre view count bar graph and displays it in the genre_bar_parent widget
    def create_genre_bar_graph(self, genre_views_df):
        fig = plt.Figure(figsize=(8, 6), dpi=50)
        ax = fig.add_subplot(111)

        view_counts = genre_views_df[Model.VIEW_COUNT].values
        genres = genre_views_df[Model.GENRE].values

        ax.bar(genres, view_counts)
        ax.set_ylabel("VIEWERS")
        ax.set_xlabel("TOP GENRES")
        ax.ticklabel_format(axis='y', style='plain')
        canvas = FigureCanvasTkAgg(fig, self.genre_bar_parent)
        canvas.get_tk_widget().grid(sticky="E", row=2, column=2, padx=self.PIE_PAD)

    # called when a treeview is clicked
    def _on_tv_clicked(self, event):
        tv = event.widget

        # check if different treeview was clicked
        if self.last_tv_clicked is not None and self.last_tv_clicked is not tv:
            for item in self.last_tv_clicked.selection():
                self.last_tv_clicked.selection_remove(item)

        # check if a heading  region was clicked
        region = tv.identify_region(event.x, event.y)
        if region == "heading":
            column = tv.identify_column(event.x)
            column_name = tv.column(column, option='id')
            if tv is self.sim_tv:
                self.controller.on_sim_tv_heading_clicked(column_name)
            elif tv is self.catalog_tv:
                self.controller.on_catalog_tv_heading_clicked(column_name)

        # save clicked tv so that it can be checked on the next tv click event
        self.last_tv_clicked = tv

    # creates a treeview based on a dataframe, sets a click event, and attaches it to a parent widget
    @staticmethod
    def _create_tv(parent, dataframe, left_click_command):
        tv = ttk.Treeview(parent, height=10)
        tv.bind("<Button-1>", left_click_command)
        tv['columns'] = list(dataframe.columns)
        tv["show"] = "headings"

        for column in tv["columns"]:
            tv.heading(column, text=column)

        View._set_tv_column_sizes(tv)
        View.update_tv_rows(tv, dataframe)
        return tv

    # updates a treeview's rows by deleting all previous rows and refilling the treeview
    @staticmethod
    def update_tv_rows(tv, df):
        # delete old rows
        for row in tv.get_children():
            tv.delete(row)

        # insert new rows
        df_rows = df.to_numpy().tolist()
        for row in df_rows:
            if row[0] in Model.ORIGINAL_CATALOG_ANIME_IDS:
                tv.insert("", "end", values=row, tags=("old", "f"))
            else:
                tv.insert("", "end", values=row, tags=("new", "f"))

        # configure row style
        tv.tag_configure("old", background=View.DARK_GREEN)
        tv.tag_configure("f", font=View.STD_FONT)

    # get the selected row in a treeview
    @staticmethod
    def get_tv_selection(tv):
        selection = tv.selection()
        value_list = list()
        for item in selection:
            item_dict = tv.item(item)
            value_list.append(item_dict['values'][0])
        return value_list

    # sets all the columns sizes based on the COLUMN_WIDTHS dictionary constant
    @staticmethod
    def _set_tv_column_sizes(tv):
        for name in tv['columns']:
            try:
                tv.column(name, width=View.COLUMN_WIDTHS.get(name))
            except:
                pass

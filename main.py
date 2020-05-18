from imports import *


class QHLine(QFrame):
    def __init__(self):
        super(QHLine, self).__init__()
        self.setFrameShape(QFrame.HLine)
        self.setFrameShadow(QFrame.Sunken)


class About(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("About")
        self.setWindowIcon(QIcon(":imgs/icon.png"))
        self.setFixedSize(210, 120)

        layout = QGridLayout()
        title = QLabel("UniGet")
        title.setStyleSheet("font:14px bold;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title, 0, 1)
        icon = QLabel()
        icon.setPixmap(QPixmap(":imgs/icon.png").scaledToWidth(20, Qt.SmoothTransformation))
        layout.addWidget(icon, 0, 0)
        info = QLabel("UniGet is a tool built in Python used to search and fetch records from the UniProt database.")
        info.setWordWrap(True)
        layout.addWidget(QHLine(), 1, 1)
        layout.addWidget(info, 2, 1)
        self.setLayout(layout)


class UniProtGet(QMainWindow):
    def __init__(self):
        super().__init__()
        folders = ["data/imported", "downloaded"]
        for folder in folders:
            if not os.path.exists(folder):
                os.makedirs(folder)

        self.initUI()

    def initUI(self):
        self.statusBar().setStyleSheet("background-color:#d6d6d6;")
        self.statusBar().showMessage("Ready")

        self.progressbar = QProgressBar(self)
        self.progressbar.setFixedWidth(200)
        self.progressbar.setValue(0)
        self.progressbar.setStyleSheet("{border:1px solid white;background-color:#707070;text-align:center;};")
        self.statusBar().addPermanentWidget(self.progressbar)
        self.progressbar.hide()

        self.statusbar_record_count = QLabel("No records")
        self.statusBar().addPermanentWidget(self.statusbar_record_count)

        self.statusbar_fetch = QPushButton()
        self.statusbar_fetch.setToolTip("Fetch the selected records")
        self.statusbar_fetch.setIcon(QIcon(":imgs/checkmark.png"))
        self.statusbar_fetch.setStyleSheet(":hover{border:2px solid green;border-style:inset};")
        self.statusbar_fetch.clicked.connect(self.fetch_gb)
        self.statusbar_fetch.setEnabled(False)
        self.statusBar().addPermanentWidget(self.statusbar_fetch)

        self.input = QLineEdit()
        self.input.returnPressed.connect(self.get_query)
        self.search_button = QPushButton("Search")
        self.search_button.clicked.connect(self.get_query)

        self.toolbutton = QToolButton()
        self.toolbutton.setArrowType(Qt.DownArrow)
        self.toolbutton.setPopupMode(QToolButton.InstantPopup)
        self.toolbutton.setAutoRaise(True)
        self.toolbutton.setStyleSheet("::menu-indicator{image:none;};")
        self.set_extra_menu()

        self.loading_label = QLabel()
        self.loading_label.hide()
        self.table = QTableView()
        self.table.hide()

        self.layout = QGridLayout()

        self.search_groupbox = QGroupBox("Input")
        self.search_groupbox.setFixedSize(280, 55)
        layout = QGridLayout()
        layout.addWidget(self.input, 0, 0)
        layout.addWidget(self.search_button, 0, 1)
        layout.addWidget(self.toolbutton, 0, 2)
        layout.addWidget(self.loading_label, 0, 3)
        self.search_groupbox.setLayout(layout)

        self.layout.addWidget(self.search_groupbox, 0, 0)
        self.groupbox_base_filters = self.get_base_filters_groupbox()
        self.layout.addWidget(self.groupbox_base_filters, 1, 0)
        self.groupbox_experimental_filters = self.get_experimental_filters_groupbox()
        self.layout.addWidget(self.groupbox_experimental_filters, 2, 0)
        self.groupbox_gene_filters = self.get_gene_filters_groupbox()
        self.layout.addWidget(self.groupbox_gene_filters, 3, 0)
        self.layout.addWidget(self.table, 0, 4, 4, 1)
        frame = QFrame()
        # TODO
        frame.setFrameStyle(1)
        # frame.setStyleSheet("border:1px solid black")
        frame.setLayout(self.layout)
        self.setCentralWidget(frame)

        self.centre()
        self.setWindowTitle("UniGet")
        self.setWindowIcon(QIcon(":imgs/icon.png"))
        self.setMinimumSize(self.sizeHint())
        self.show()

        self.get_data()

    def get_data(self):
        # Refresh GUI
        app.processEvents()

        # Save update times for each database
        try:
            self.update_times = [None] * 5
            with open("data/imported/db_last_update.txt", "r") as file:
                lines = file.readlines()
                for _, line in enumerate(lines):
                    self.update_times[_] = line
        except:
            self.update_times = [None] * 5

        # Databases
        self.path_db_df = "data/imported/db_df.pkl"
        if not os.path.exists(self.path_db_df):
            self.get_db_filters = GetDBFilters()
            self.get_db_filters.progress.connect(self.get_db_progress)
            self.get_db_filters.done.connect(self.get_db_done)
            self.get_db_filters.start()

            self.update_times[0] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S\n")
        else:
            self.db_df = pickle.load(open(self.path_db_df, "rb"))
            self.get_db_combo()

        # Species
        self.path_spec_df = "data/imported/spec_df.pkl"
        if not os.path.exists(self.path_spec_df):
            self.get_species_filters = GetSpeciesFilters()
            self.get_species_filters.progress.connect(self.get_species_progress)
            self.get_species_filters.done.connect(self.get_species_done)
            self.get_species_filters.start()

            self.update_times[1] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S\n")
        else:
            self.spec_df = pickle.load(open(self.path_spec_df, "rb"))
            self.get_spec_combo()

        # Families
        self.path_family_dict = "data/imported/family_dict.pkl"
        if not os.path.exists(self.path_family_dict):
            self.get_families_filters = GetFamiliesFilters()
            self.get_families_filters.progress.connect(self.get_families_progress)
            self.get_families_filters.done.connect(self.get_families_done)
            self.get_families_filters.start()

            self.update_times[2] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S\n")
        else:
            self.family_dict = pickle.load(open(self.path_family_dict, "rb"))
            self.get_family_combo()

        # Pathways
        self.path_pathway_dict = "data/imported/pathway_dict.pkl"
        if not os.path.exists(self.path_pathway_dict):
            self.get_pathways_filters = GetPathwaysFilters()
            self.get_pathways_filters.progress.connect(self.get_pathways_progress)
            self.get_pathways_filters.done.connect(self.get_pathways_done)
            self.get_pathways_filters.start()

            self.update_times[3] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S\n")
        else:
            self.pathway_dict = pickle.load(open(self.path_pathway_dict, "rb"))
            self.get_pathways_combo()

        # Subcellular locations
        self.path_subcell_dict = "data/imported/subcell_dict.pkl"
        if not os.path.exists(self.path_subcell_dict):
            self.get_subcell_filters = GetSubcellFilters()
            self.get_subcell_filters.progress.connect(self.get_subcell_progress)
            self.get_subcell_filters.done.connect(self.get_subcell_done)
            self.get_subcell_filters.start()

            self.update_times[4] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S\n")
        else:
            self.subcell_dict = pickle.load(open(self.path_subcell_dict, "rb"))
            self.get_subcell_combo()

        with open("data/imported/db_last_update.txt", "w") as file:
            file.writelines(self.update_times)

    def get_db_progress(self, progress):
        self.db_progressbar.setValue(progress)

    def get_db_done(self, data):
        with open(self.path_db_df, "wb") as file:
            pickle.dump(data, file)
        self.db_df = data
        self.get_db_combo()

    def get_db_combo(self):
        self.groupbox_base_filters.layout().removeWidget(self.db_progressbar)
        self.db_progressbar.hide()
        self.db_combo = QComboBox()
        self.db_combo.setSizeAdjustPolicy(self.db_combo.AdjustToMinimumContentsLengthWithIcon)
        self.db_combo.addItems(self.db_df["Abbrev"])
        self.groupbox_base_filters.layout().addWidget(self.db_combo, 1, 1)

    def get_species_progress(self, progress):
        self.spec_progressbar.setValue(progress)

    def get_species_done(self, data):
        with open(self.path_spec_df, "wb") as file:
            pickle.dump(data, file)
        self.spec_df = data
        self.get_spec_combo()

    def get_spec_combo(self):
        self.groupbox_base_filters.layout().removeWidget(self.spec_progressbar)
        self.spec_progressbar.hide()
        self.spec_combo = QComboBox()
        self.spec_combo.setSizeAdjustPolicy(self.spec_combo.AdjustToMinimumContentsLengthWithIcon)
        self.spec_combo.addItems(list(self.spec_df.index))
        self.groupbox_base_filters.layout().addWidget(self.spec_combo, 2, 1)

    def get_families_progress(self, progress):
        self.family_progressbar.setValue(progress)

    def get_families_done(self, data):
        with open(self.path_family_dict, "wb") as file:
            pickle.dump(data, file)
        self.family_dict = data
        self.get_family_combo()

    def get_family_combo(self):
        self.groupbox_gene_filters.layout().removeWidget(self.family_progressbar)
        self.family_progressbar.hide()
        self.family_combo = QComboBox()
        self.family_combo.setSizeAdjustPolicy(self.family_combo.AdjustToMinimumContentsLengthWithIcon)
        self.family_combo.addItems(list(self.family_dict.keys()))
        self.groupbox_gene_filters.layout().addWidget(self.family_combo, 1, 1)

    def get_pathways_progress(self, progress):
        self.pathway_progressbar.setValue(progress)

    def get_pathways_done(self, data):
        with open(self.path_pathway_dict, "wb") as file:
            pickle.dump(data, file)
        self.pathway_dict = data
        self.get_pathways_combo()

    def get_pathways_combo(self):
        self.groupbox_gene_filters.layout().removeWidget(self.pathway_progressbar)
        self.pathway_progressbar.hide()
        self.pathway_combo = QComboBox()
        self.pathway_combo.setSizeAdjustPolicy(self.pathway_combo.AdjustToMinimumContentsLengthWithIcon)
        self.pathway_combo.addItems(list(self.pathway_dict.keys()))
        self.groupbox_gene_filters.layout().addWidget(self.pathway_combo, 5, 1)

    def get_subcell_progress(self, progress):
        self.subcell_progressbar.setValue(progress)

    def get_subcell_done(self, data):
        with open(self.path_subcell_dict, "wb") as file:
            pickle.dump(data, file)
        self.subcell_dict = data
        self.get_subcell_combo()

    def get_subcell_combo(self):
        self.groupbox_gene_filters.layout().removeWidget(self.subcell_progressbar)
        self.subcell_progressbar.hide()
        self.subcell_combo = QComboBox()
        self.subcell_combo.setSizeAdjustPolicy(self.subcell_combo.AdjustToMinimumContentsLengthWithIcon)
        keys = sorted(list(self.subcell_dict.keys()))
        self.subcell_combo.addItems(keys)
        self.groupbox_gene_filters.layout().addWidget(self.subcell_combo, 7, 1)

    def centre(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def set_extra_menu(self):
        menu = QMenu(self)

        self.open_action = QAction("Open", self)
        self.save_action = QAction("Save", self)

        edit_menu = QMenu("Edit", self)
        self.select_all_action = QAction("Select all", self)
        edit_menu.addAction(self.select_all_action)
        self.open_downloads_action = QAction("Open downloads folder", self)
        edit_menu.addAction(self.open_downloads_action)

        self.filters_action = QAction("Filters", self)
        self.about_action = QAction("About", self)

        settings_menu = QMenu("Settings", self)
        self.update_db_action = QAction("Update databases", self)
        settings_menu.addAction(self.update_db_action)
        self.update_db_action.setShortcut("Ctrl+U")
        self.update_db_action.triggered.connect(self.toolbutton_click)

        menu.addAction(self.open_action)
        menu.addAction(self.save_action)
        menu.addMenu(edit_menu)
        menu.addAction(self.filters_action)
        menu.addMenu(settings_menu)
        menu.addSeparator()
        menu.addAction(self.about_action)

        self.open_action.triggered.connect(self.toolbutton_click)
        self.open_action.setShortcut("Ctrl+O")
        self.save_action.triggered.connect(self.toolbutton_click)
        self.save_action.setShortcut("Ctrl+S")
        self.select_all_action.triggered.connect(self.toolbutton_click)
        self.select_all_action.setShortcut("Ctrl+A")
        self.open_downloads_action.triggered.connect(self.toolbutton_click)
        self.open_downloads_action.setShortcut("Ctrl+D")
        self.filters_action.triggered.connect(self.toolbutton_click)
        self.filters_action.setShortcut("Ctrl+F")
        self.about_action.triggered.connect(self.toolbutton_click)
        self.about_action.setShortcut("Alt+A")

        self.toolbutton.setMenu(menu)

    def toolbutton_click(self):
        if self.sender() is self.open_action:
            try:
                name = QFileDialog.getOpenFileName(self, "Open file", filter="csv(*.csv)")
                self.df = pd.read_csv(name[0], index_col=0)
                row_count = self.df.shape[0]
                self.update_table((self.df, row_count))
                QMessageBox.information(self, "Info", "File successfully imported!")
            except:
                QMessageBox.warning(self, "Warning", "Unable to import data!")

        if self.sender() is self.save_action:
            try:
                self.df
                name = QFileDialog.getSaveFileName(self, "Save file", filter="csv(*.csv)")
                self.df.to_csv(name[0])
                QMessageBox.information(self, "Info", "Filed successfully saved!")
            except:
                QMessageBox.warning(self, "Warning", "Unable to save data!")

        if self.sender() is self.select_all_action:
            for row in range(self.row_count):
                index = self.table.model().index(row, 0)
                self.table.model().setData(index, Qt.Checked, Qt.CheckStateRole)

        if self.sender() is self.open_downloads_action:
            path = os.getcwd() + "/downloaded"
            path = os.path.realpath(path)
            os.startfile(path)

        if self.sender() is self.filters_action:
            if self.groupbox_base_filters.isVisible():
                self.groupbox_base_filters.hide()
            if self.groupbox_experimental_filters.isVisible():
                self.groupbox_experimental_filters.hide()
            if self.groupbox_gene_filters.isVisible():
                self.groupbox_gene_filters.hide()
            else:
                self.groupbox_base_filters.show()
                self.groupbox_experimental_filters.show()
                self.groupbox_gene_filters.show()
                # TODO: resize properly
                # self.resize(self.sizeHint() + QSize(40, 20))

        if self.sender() is self.update_db_action:
            self.force_db_update()

        if self.sender() is self.about_action:
            self.about_widget = About()
            self.about_widget.setWindowModality(Qt.ApplicationModal)
            self.about_widget.show()

    def get_base_filters_groupbox(self):
        groupbox = QGroupBox("Base Filters")
        groupbox.setFixedSize(280, 110)
        layout = QGridLayout()

        self.db_label = QLabel("Databases:")
        self.db_progressbar = QProgressBar()
        self.db_progressbar.setStyleSheet("border:0px;text-align:center;background:#707070;color:white")
        layout.addWidget(self.db_label, 1, 0)
        layout.addWidget(self.db_progressbar, 1, 1)

        self.button_db = QPushButton("+")
        self.button_db.setFixedSize(20, 20)
        self.button_db.setStyleSheet("border:0px;color:green;font:22px bold;")
        self.button_db.clicked.connect(lambda: self.get_db_table(self.db_df))
        layout.addWidget(self.button_db, 1, 2)

        self.spec_label = QLabel("Species:")
        self.spec_progressbar = QProgressBar()
        self.spec_progressbar.setStyleSheet("border:0px;text-align:center;background:#707070;color:white")

        layout.addWidget(self.spec_label, 2, 0)
        layout.addWidget(self.spec_progressbar, 2, 1)

        self.button_spec = QPushButton("+")
        self.button_spec.setFixedSize(20, 20)
        self.button_spec.setStyleSheet("border:0px;color:green;font:22px bold;")
        self.button_spec.clicked.connect(lambda: self.get_spec_table(self.spec_df))
        layout.addWidget(self.button_spec, 2, 2)

        self.review_label = QLabel("Review status:")
        self.review_check = QCheckBox("Unspecified")
        self.review_check.setTristate(True)
        self.review_check.setCheckState(Qt.Unchecked)
        self.review_check.stateChanged.connect(self.set_review_status)
        layout.addWidget(self.review_label, 3, 0)
        layout.addWidget(self.review_check, 3, 1)

        groupbox.setLayout(layout)

        return groupbox

    def get_experimental_filters_groupbox(self):
        groupbox = QGroupBox("Experimental Filters")
        groupbox.setFixedSize(280, 110)
        layout = QGridLayout()

        self.methods_label = QLabel("Methods:")
        methods = ["em", "fiber", "ir",
                   "model", "nmr", "neutron", "x-ray"]
        methods_labels = ["Electron microscopy", "Fiber diffraction", "Infrared spectroscopy",
                          "Model", "NMR", "Neutron diffraction", "X-ray"]
        self.methods_combo = QComboBox()
        self.methods_combo.addItems(methods_labels)
        layout.addWidget(self.methods_label, 1, 0)
        layout.addWidget(self.methods_combo, 1, 1)

        self.mass_label = QLabel("Mass:")
        self.mass_spinbox = QSpinBox()
        self.mass_label_unit = QLabel("Da")
        layout.addWidget(self.mass_label, 2, 0)
        layout.addWidget(self.mass_spinbox, 2, 1)
        layout.addWidget(self.mass_label_unit, 2, 2)

        self.length_label = QLabel("Length:")
        self.length_spinbox = QSpinBox()
        self.length_label_unit = QLabel("residues")
        layout.addWidget(self.length_label, 3, 0)
        layout.addWidget(self.length_spinbox, 3, 1)
        layout.addWidget(self.length_label_unit, 3, 2)

        groupbox.setLayout(layout)

        return groupbox

    def get_gene_filters_groupbox(self):
        groupbox = QGroupBox("Genetic Filters")
        groupbox.setFixedSize(280, 180)
        layout = QGridLayout()

        self.family_label = QLabel("Family:")
        self.family_progressbar = QProgressBar()
        self.family_progressbar.setStyleSheet("border:0px;text-align:center;background:#707070;color:white")

        layout.addWidget(self.family_label, 1, 0)
        layout.addWidget(self.family_progressbar, 1, 1)

        self.button_family = QPushButton("+")
        self.button_family.setFixedSize(20, 20)
        self.button_family.setStyleSheet("border:0px;color:green;font:22px bold;")
        # TODO
        # self.button_family.clicked.connect(lambda: self.get_family_listview(self.db_df))
        layout.addWidget(self.button_family, 1, 2)

        self.gene_label = QLabel("Gene:")
        self.gene_input = QLineEdit()
        self.gene_exact_label = QLabel("Gene exact:")
        self.gene_exact_input = QLineEdit()
        layout.addWidget(self.gene_label, 2, 0)
        layout.addWidget(self.gene_input, 2, 1)
        layout.addWidget(self.gene_exact_label, 3, 0)
        layout.addWidget(self.gene_exact_input, 3, 1)

        layout.addWidget(QHLine(), 4, 0, 1, 3)

        self.pathway_label = QLabel("Pathway:")
        self.pathway_progressbar = QProgressBar()
        self.pathway_progressbar.setStyleSheet("border:0px;text-align:center;background:#707070;color:white")

        layout.addWidget(self.pathway_label, 5, 0)
        layout.addWidget(self.pathway_progressbar, 5, 1)

        self.button_pathway = QPushButton("+")
        self.button_pathway.setFixedSize(20, 20)
        self.button_pathway.setStyleSheet("border:0px;color:green;font:22px bold;")
        # TODO
        # self.button_family.clicked.connect(lambda: self.get_pathway_listview(self.db_df))
        layout.addWidget(self.button_pathway, 5, 2)

        layout.addWidget(QHLine(), 6, 0, 1, 3)

        self.subcell_label = QLabel("Subcellular location:")
        self.subcell_progressbar = QProgressBar()
        self.subcell_progressbar.setStyleSheet("border:0px;text-align:center;background:#707070;color:white")

        layout.addWidget(self.subcell_label, 7, 0)
        layout.addWidget(self.subcell_progressbar, 7, 1)

        self.button_subcell = QPushButton("+")
        self.button_subcell.setFixedSize(20, 20)
        self.button_subcell.setStyleSheet("border:0px;color:green;font:22px bold;")
        # TODO
        # self.button_family.clicked.connect(lambda: self.get_subcell_listview(self.db_df))
        layout.addWidget(self.button_subcell, 7, 2)

        groupbox.setLayout(layout)

        return groupbox

    def set_review_status(self):
        status, colors = ["Unspecified", "Unreviewed", "Reviewed"], \
                         ["black", "red", "green"]
        current_state = self.review_check.checkState()
        self.review_check.setText(status[current_state])
        self.review_check.setStyleSheet("color:{}".format(colors[current_state]))

        # Set filtering based on review status
        # ^/&: start/end delimiters
        self.proxy.setFilterRegExp(QRegExp(
            "" if status[current_state] is "Unspecified" else "^" + status[current_state] + "$", Qt.CaseInsensitive))
        self.statusbar_record_count.setText("{} records".format(self.table.model().rowCount()))

    def get_db_table(self, df):
        self.db_table = QTableView()
        model = PandasModel(df)
        self.db_table.setModel(model)
        self.db_table.show()

    def get_spec_table(self, df):
        self.spec_table = QTableView()
        model = PandasModel(df)
        self.spec_table.setModel(model)
        self.spec_table.show()

    def get_query(self):
        query = self.input.text()
        try:
            assert len(query) > 0
        except AssertionError:
            error = QErrorMessage(self)
            error.setWindowTitle("Warning")
            error.showMessage("Query cannot be empty!")
            return

        self.search_button.setEnabled(False)
        self.input.setEnabled(False)
        self.groupbox_base_filters.setEnabled(False)
        self.groupbox_experimental_filters.setEnabled(False)
        self.groupbox_gene_filters.setEnabled(False)

        self.statusBar().setStyleSheet("background-color:#d6d6d6;")
        self.statusBar().showMessage("Searching: {}...".format(query))
        query_formatted = query.replace(" ", "%20")

        self.loading_gif = QMovie(":imgs/loading.gif")
        self.loading_gif.setScaledSize(QSize(20, 20))
        self.loading_label.setMovie(self.loading_gif)
        self.loading_label.show()
        self.loading_gif.start()

        self.gen_table = GetData(query_formatted)
        self.gen_table.done.connect(self.update_table)
        self.gen_table.error.connect(self.error_table)
        self.gen_table.start()

    def update_table(self, data):
        self.statusBar().clearMessage()
        self.df, self.row_count = data
        self.statusbar_record_count.setText("{} records".format(self.row_count))

        model = PandasModel(self.df)
        self.proxy = QSortFilterProxyModel(self)
        self.proxy.setSourceModel(model)
        # Filter review status of record
        self.proxy.setFilterKeyColumn(2)
        self.table.setModel(self.proxy)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.show()

        self.reset_gui()

        self.resize(1100, 550)
        self.centre()

        self.statusbar_fetch.setEnabled(True)

    def error_table(self, error):
        self.statusBar().clearMessage()
        self.statusBar().setStyleSheet("color:#ff4242;background-color:#d6d6d6;")
        self.statusBar().showMessage(error, 3000)
        self.reset_gui()

    def reset_gui(self):
        self.search_button.setEnabled(True)
        self.input.setEnabled(True)
        self.groupbox_base_filters.setEnabled(True)
        self.groupbox_experimental_filters.setEnabled(True)
        self.groupbox_gene_filters.setEnabled(True)
        try:
            # When importing from file, this should not be calledF
            self.loading_gif.stop()
            self.loading_label.hide()
        except:
            pass

        app.processEvents()
        time.sleep(1)
        self.statusBar().setStyleSheet("color:black")
        self.statusBar().showMessage("Ready")

    def fetch_gb(self):
        self.statusBar().removeWidget(self.statusbar_fetch)
        self.statusbar_fetch.deleteLater()
        self.statusbar_fetch_loading = QLabel()
        self.statusbar_fetch_loading.setMovie(self.loading_gif)
        self.loading_gif.start()
        self.statusBar().addPermanentWidget(self.statusbar_fetch_loading)

        to_fetch = []
        for row in range(self.row_count):
            if self.table.model().index(row, 0).data(Qt.CheckStateRole) == Qt.Checked:
                to_fetch.append(self.table.model().index(row, 0).data())

        assert to_fetch
        self.progressbar.show()

        self.uniprot_get = GetUniProt(ids=to_fetch, format="fasta")
        self.uniprot_get.progress.connect(self.get_uniprot_progress)
        self.uniprot_get.done.connect(self.get_uniprot_done)
        self.uniprot_get.start()

    def get_uniprot_progress(self, value):
        progress_id, progress_value = value
        self.progressbar.setValue(progress_value)
        self.statusBar().showMessage("Downloading record {}\t|\t{}".format(
            progress_id, self.table.model().rowCount()))

    def get_uniprot_done(self):
        self.statusBar().removeWidget(self.statusbar_fetch_loading)
        self.statusbar_fetch_loading.deleteLater()
        self.statusbar_fetch = QPushButton()
        self.statusbar_fetch.setToolTip("Fetch the selected records")
        self.statusbar_fetch.setIcon(QIcon(":imgs/checkmark.png"))
        self.statusbar_fetch.setStyleSheet(":hover{border:2px solid green;border-style:inset};")
        self.statusbar_fetch.clicked.connect(self.fetch_gb)
        self.statusBar().addPermanentWidget(self.statusbar_fetch)

        self.progressbar.hide()
        self.progressbar.setValue(0)
        self.statusBar().showMessage("Ready")

    def force_db_update(self):
        # TODO: this function crashes when called before self.get_data finished
        self.statusBar().showMessage("Updating databases", 5000)

        try:
            self.combos = [self.db_combo, self.spec_combo, self.family_combo, self.pathway_combo, self.subcell_combo]
            self.progressbars = [self.db_progressbar, self.spec_progressbar, self.family_progressbar,
                                 self.pathway_progressbar, self.subcell_progressbar]
        except:
            QMessageBox.warning(self, "Warning", "Databases are still loading.\nWait for completion.")
            return

        msg_info = ["Databases", "Species", "Families", "Pathways", "Subcellular locations"]
        msg = QMessageBox.question(self, "Update databases",
                                   "<b>Last update</b>:<br><br>{}".format(
                                       "<br>".join(
                                           [msg_info[_] + ":\t" + self.update_times[_] for _ in range(len(msg_info))])),
                                   QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if msg == QMessageBox.Yes:
            folders = ["data/imported", "downloaded"]
            for folder in folders:
                for file in os.listdir(folder):
                    os.remove(os.path.join(folder, file))

            # Clear and hide combobox
            for combo in self.combos:
                combo.clear()
                combo.hide()
            # Reset and show progressbar
            for progress in self.progressbars:
                progress.setValue(0)
                progress.show()

            self.get_data()

        else:
            return


if __name__ == "__main__":
    app = QApplication(sys.argv)
    upg = UniProtGet()
    sys.exit(app.exec_())

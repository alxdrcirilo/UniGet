import data.imgs
from data.get_data import GetData
from data.get_db import GetDBFilters
from data.get_species import GetSpeciesFilters
from data.get_file import GetUniProt
from data.get_families import GetFamiliesFilters
from data.get_pathways import GetPathwaysFilters
from data.get_subcell import GetSubcellFilters
from data.pandas_model import PandasModel

from PyQt5.QtCore import QRegExp, QSize, QSortFilterProxyModel, Qt
from PyQt5.QtGui import QIcon, QMovie, QPixmap
from PyQt5.QtWidgets import QApplication, QAction, QCheckBox, QComboBox, QDesktopWidget, QErrorMessage, QFrame, \
    QGridLayout, QGroupBox, QHeaderView, QLabel, QLineEdit, QMainWindow, QMenu, QMessageBox, QPushButton, QProgressBar, QSpinBox, \
    QTableView, QToolButton, QWidget

import datetime
import os
import pickle
import sys
import time
import pandas as pd
from PyQt5.QtCore import pyqtSignal, QThread

class GetData(QThread):
    done = pyqtSignal(tuple)
    error = pyqtSignal(str)

    def __init__(self, query, parent=None):
        QThread.__init__(self, parent)
        self.query = query

    def run(self):
        query_url = "https://www.uniprot.org/uniprot/?query={}&format=tab".format(self.query)
        # Debug
        # query_df = pd.read_csv("uniprot_myoglobin_tab.txt", sep="\t", header=0)
        try:
            query_df = pd.read_csv(query_url, sep="\t", header=0)
            self.done.emit((query_df, query_df.shape[0]))
        except pd.errors.EmptyDataError:
            self.error.emit("No records found!")
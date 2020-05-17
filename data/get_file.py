import os
from PyQt5.QtCore import pyqtSignal, QThread
import urllib.request
from urllib.error import HTTPError


class GetUniProt(QThread):
    progress = pyqtSignal(tuple)
    done = pyqtSignal()

    def __init__(self, ids: list, format: str = "fasta", parent=None):
        QThread.__init__(self, parent)
        self.ids = ids
        self.format = format

    def run(self):
        """
        Downloads the UniProt entries supplied in the ids list.

        :param ids: List of UniProt accession numbers
        :param format: Format of file to be downloaded (args: "txt", "fasta", "xml", "rdf/xml", "gff"
        """
        path = "downloaded/"
        failed = []

        for _, id in enumerate(self.ids):
            file = "{}.{}".format(id, self.format)
            if not os.path.exists(path + file):
                try:
                    url = "https://www.uniprot.org/uniprot/{}.{}".format(id, self.format)
                    out_path = path + file
                    urllib.request.urlretrieve(url, out_path)
                except HTTPError:
                    failed.append(id)
            else:
                pass

            progress = ((_ + 1) / len(self.ids) * 100)

            self.progress.emit((_ + 1, progress))
        self.done.emit()

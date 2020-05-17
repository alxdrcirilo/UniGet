import pandas as pd
from PyQt5.QtCore import pyqtSignal, QThread
import urllib.request


class GetDBFilters(QThread):
    done = pyqtSignal(object)
    progress = pyqtSignal(int)

    def run(self):
        db_url = "http://www.uniprot.org/docs/dbxref.txt"
        db_txt = urllib.request.urlopen(db_url)
        entries = ["AC", "Abbrev", "Name", "Server", "Db_URL", "Cat"]
        db_dict = {key: [] for key in entries}

        counter = 0
        for line in db_txt:
            if b"dbxref.txt" in line:
                continue
            for id in entries:
                if line.startswith(id.encode()):
                    str_line = str(line, "utf-8")
                    index = str_line.index(":")
                    db_dict[id].append(str_line[index + 1:-1])

                    counter += 1
                    # Debug: hardcoded 173!
                    tmp_counter = round(counter / 173 * 100)

                    try:
                        global_counter
                    except NameError:
                        global_counter = tmp_counter

                    if tmp_counter != global_counter:
                        self.progress.emit(tmp_counter)

                    global_counter = tmp_counter

        self.done.emit(pd.DataFrame.from_dict(db_dict))

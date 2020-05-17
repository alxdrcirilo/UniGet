import pandas as pd
from PyQt5.QtCore import pyqtSignal, QThread
import urllib.request


class GetSpeciesFilters(QThread):
    done = pyqtSignal(object)
    progress = pyqtSignal(int)

    def run(self):
        spec_url = "https://www.uniprot.org/docs/speclist.txt"
        spec_txt = urllib.request.urlopen(spec_url)
        entries = ["Taxonomy", "Taxon Node", "Name"]
        spec_dict = {}

        naming = ["N=", "C=", "S="]

        flag = False
        counter = 0
        for line in spec_txt:
            # Header
            if b"speclist.txt" in line:
                continue
            # Start
            if b"_____" in line:
                flag = True
                continue
            # End
            if b"-----" in line:
                flag = False
                continue

            if flag:
                str_line = str(line, "utf-8")

                try:
                    index = str_line.index(":")
                    tmp = str_line[:index].split(" ")
                    tmp = [_ for _ in tmp if _]
                except ValueError:
                    pass

                try:
                    spec_dict[tmp[0]]
                except KeyError:
                    spec_dict[tmp[0]] = {key: [] for key in entries}

                    counter += 1
                    # Debug: hardcoded 26348!
                    tmp_counter = round(counter / 26348 * 100)

                    try:
                        global_counter
                    except NameError:
                        global_counter = tmp_counter

                    if tmp_counter != global_counter:
                        self.progress.emit(tmp_counter)

                spec_dict[tmp[0]]["Taxonomy"] = tmp[1]
                spec_dict[tmp[0]]["Taxon Node"] = tmp[2]

                for name in naming:
                    try:
                        index = str_line.index(name)

                        spec_dict[tmp[0]]["Name"].append(str_line[index:-1])
                    except ValueError:
                        continue

        self.done.emit(pd.DataFrame.from_dict(spec_dict).T)

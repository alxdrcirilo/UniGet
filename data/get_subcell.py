from copy import copy
from PyQt5.QtCore import pyqtSignal, QThread
import urllib.request


class GetSubcellFilters(QThread):
    done = pyqtSignal(object)
    progress = pyqtSignal(int)

    def run(self):
        subcell_url = "https://www.uniprot.org/docs/subcell.txt"
        subcell_txt = urllib.request.urlopen(subcell_url)
        subcell_dict = {}
        default_subdict = {"ID": [], "IT": [], "IO": [], "AC": [], "DE": [], "SY": [], "SL": [],
                           "HI": [], "HP": [], "KW": [], "GO": [], "AN": [], "RX": [], "WW": []}

        flag = False
        counter = 0
        for line in subcell_txt:
            str_line = str(line, "utf-8")

            if "____" in str_line:
                flag = True
                continue

            if flag:
                # Cleanup all identifiers for one given entry
                if "//" in str_line:
                    for key in default_subdict.keys():
                        subcell_dict[AC][key] = " ".join(subcell_dict[AC][key])
                    continue

                if str_line.startswith("ID"):
                    ID = str_line[5:-1]
                    continue

                if str_line.startswith("IT"):
                    IT = str_line[5:-1]
                    continue

                if str_line.startswith("IO"):
                    IO = str_line[5:-1]
                    continue

                # Create entry in subcell_dict
                if str_line.startswith("AC"):
                    AC = str_line[5:-1]
                    subcell_dict[AC] = copy(default_subdict)

                    try:
                        subcell_dict[AC]["ID"] = ID
                    except:
                        pass
                    try:
                        subcell_dict[AC]["IT"] = IT
                    except:
                        pass
                    try:
                        subcell_dict[AC]["IO"] = IO
                    except:
                        pass

                    counter += 1
                    # Debug: hardcoded 545!
                    tmp_counter = round(counter / 545 * 100)
                    try:
                        global_counter
                    except NameError:
                        global_counter = tmp_counter
                    if tmp_counter != global_counter:
                        self.progress.emit(tmp_counter)
                    global_counter = tmp_counter

                    continue

                # Fill entry children in default_subdict
                if str_line.startswith(tuple(default_subdict.keys())):
                    identifier = str_line[:2]
                    subcell_dict[AC][identifier].append(str_line[5:-1])

        self.done.emit(subcell_dict)

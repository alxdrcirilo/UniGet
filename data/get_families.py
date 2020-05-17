from PyQt5.QtCore import pyqtSignal, QThread
import urllib.request


class GetFamiliesFilters(QThread):
    done = pyqtSignal(object)
    progress = pyqtSignal(int)

    def run(self):
        family_url = "https://www.uniprot.org/docs/similar.txt"
        family_txt = urllib.request.urlopen(family_url)
        family_dict = {}

        flag = False
        counter = 0
        for line in family_txt:
            str_line = str(line, "utf-8")

            # End
            if line == b"\n":
                flag = False

            # Children
            if flag:
                formatted_line = [_ for _ in str_line.split(" ") if _][:-1]
                while "," in formatted_line:
                    formatted_line.remove(",")
                child_name, child_key = formatted_line[0::2], formatted_line[1::2]
                formatted_child_key = [_.replace("(", "").replace(")", "") for _ in child_key]

                while child_name and formatted_child_key:
                    family_dict[family_name][child_name.pop()] = formatted_child_key.pop()

            # Start
            if b"family" in line:
                family_name = str(line, "utf-8")[:-1]
                family_dict[family_name] = {}
                flag = True

                counter += 1
                # Debug: hardcoded 11982!
                tmp_counter = round(counter / 11982 * 100)

                try:
                    global_counter
                except NameError:
                    global_counter = tmp_counter

                if tmp_counter != global_counter:
                    self.progress.emit(tmp_counter)

                global_counter = tmp_counter

        self.done.emit(family_dict)

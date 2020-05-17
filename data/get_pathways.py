from PyQt5.QtCore import pyqtSignal, QThread
import urllib.request


class GetPathwaysFilters(QThread):
    done = pyqtSignal(object)
    progress = pyqtSignal(int)

    def format_children(self, data):
        try:
            data.remove(",\n")
        except ValueError:
            try:
                data.remove("\n")
            except ValueError:
                data = [_.replace("\n", "") for _ in data]
        while "," in data:
            data.remove(",")

        return data

    def run(self):
        pathway_url = "https://www.uniprot.org/docs/pathway.txt"
        pathway_txt = urllib.request.urlopen(pathway_url)
        pathway_dict = {}

        flag = False
        counter = 0
        for line in pathway_txt:
            str_line = str(line, "utf-8")

            # Pathway
            if str_line.endswith(".\n"):
                counter += 1
                # Debug: hardcoded 1420!
                tmp_counter = round(counter / 1420 * 100)

                try:
                    global_counter
                except NameError:
                    global_counter = tmp_counter

                if tmp_counter != global_counter:
                    self.progress.emit(tmp_counter)

                global_counter = tmp_counter

                pathway = str_line[:-2]
                pathway_dict[pathway] = {"Entry": [], "Accession": []}
                flag = not flag
                continue

            # Children
            if flag:
                # End
                if "----" in str_line:
                    break
                else:
                    children = [_ for _ in str_line.split(" ") if _]
                    children = self.format_children(data=children)

                    for entry, accession in zip(children[::2], children[1::2]):
                        pathway_dict[pathway]["Entry"].append(entry)
                        pathway_dict[pathway]["Accession"].append(accession.replace("(", "").replace(")", ""))
                        assert len(pathway_dict[pathway]["Entry"]) == len(pathway_dict[pathway]["Accession"])
                    continue

        self.done.emit(pathway_dict)

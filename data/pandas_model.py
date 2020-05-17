import imgs
from PyQt5.QtCore import QAbstractTableModel, Qt
from PyQt5.QtGui import QBrush, QColor, QPixmap


class PandasModel(QAbstractTableModel):
    def __init__(self, data):
        QAbstractTableModel.__init__(self)
        self._data = data
        self._checked = [[False for i in range(self.columnCount())] for j in range(self.rowCount())]

    def rowCount(self, parent=None):
        return self._data.shape[0]

    def columnCount(self, parent=None):
        return self._data.shape[1]

    def data(self, index, role=Qt.DisplayRole):
        data = self._data.iloc[index.row(), index.column()]
        if index.isValid():
            if role == Qt.ForegroundRole and data == "unreviewed":
                return QBrush(QColor("#d62d20"))
            if role == Qt.ForegroundRole and data == "reviewed":
                return QBrush(QColor("#008744"))
            if role == Qt.DisplayRole:
                return str(data)
            if role == Qt.TextAlignmentRole:
                return Qt.AlignCenter
            # Add checkboxes to first column to allow selection of IDs
            if role == Qt.CheckStateRole and index.column() == 0:
                return self._checked[index.row()][index.column()]
        return None

    def flags(self, index):
        if index.isValid():
            if index.column() == 0:
                return Qt.ItemIsUserCheckable | Qt.ItemIsSelectable | Qt.ItemIsEnabled
            else:
                return Qt.ItemIsSelectable | Qt.ItemIsEnabled

    def headerData(self, col, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self._data.columns[col]
        if orientation == Qt.Horizontal and role == Qt.DecorationRole:
            return QPixmap("imgs/table/header_{}.png".format(col))
        return None

    def setData(self, index, value, role):
        if not index.isValid() or role != Qt.CheckStateRole:
            return False
        self._checked[index.row()][index.column()] = value
        self.dataChanged.emit(index, index)
        return True

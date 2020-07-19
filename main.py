import csv

from PyQt5.QtCore import Qt, QSize, QAbstractTableModel, QSortFilterProxyModel, pyqtSlot, QModelIndex
from PyQt5.QtGui import QColor, QKeySequence
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableView, QAction, QWidget, QHeaderView, QHBoxLayout, \
  QSizePolicy, qApp, QFileDialog, QAbstractItemView, QPushButton, QVBoxLayout
# Only needed for access to command line arguments
import sys

class CSVTableModel(QAbstractTableModel):
  def __init__(self, data=None):
    super(CSVTableModel, self).__init__()
    self.load_data(data)

  def load_data(self, data):
    if data is None:
      data = [
        ["Col1", "Col2", "Col3"],
        [4, 9, 2],
        [1, 0, 0],
        [3, 5, 0],
        [3, 3, 2],
        [7, 8, 9],
      ]
    self._headers = data[0]
    self._data = data[1:]

  def data(self, index, role):
    if role == Qt.DisplayRole:
      return self._data[index.row()][index.column()]
    elif role == Qt.TextAlignmentRole:
      return Qt.AlignCenter
    elif role == Qt.EditRole:
      return self._data[index.row()][index.column()]
    # elif role == Qt.BackgroundRole:
    #   return QColor(Qt.white)
    return None

  def setData(self, index, value, role):
    if not index.isValid():
      return False
    if self._data[index.row()][index.column()] == value:
      return False
    self._data[index.row()][index.column()] = value
    return True

  def headerData(self, section, orientation, role):
    if role != Qt.DisplayRole:
      return None
    if orientation == Qt.Horizontal:
      return self._headers[section]
    else:
      return "{}".format(section)

  def flags(self, index):
    return Qt.ItemIsEnabled|Qt.ItemIsEditable|Qt.ItemIsSelectable

  def insertRows(self , position , rows , parent=QModelIndex()):
    # Ignore position. Always append to end of table
    # self.beginInsertRows(QModelIndex(),position,position+rows-1)
    self.beginInsertRows(QModelIndex(),len(self._data),len(self._data)+rows-1)
    columns = len(self._headers)
    for row in range(0, rows):
      self._data.append([None] * columns)
    self.endInsertRows()
    return True

  def removeRows(self , position , rows , parent=QModelIndex()):
    self.beginRemoveRows(QModelIndex(),position,position+rows-1)
    for row in range(0, rows):
      del self._data[position]
    self.endRemoveRows()
    return True

  def rowCount(self, index):
    # The length of the outer list.
    return len(self._data)

  def columnCount(self, index):
    # The following takes the first sub-list, and returns
    # the length (only works if all rows are an equal length)
    return len(self._data[0])

class Widget(QWidget):
  def __init__(self, data):
    QWidget.__init__(self)

    # Creating a QTableView
    self.table_view = QTableView()
    self.table_view.setAlternatingRowColors(True)
    self.table_view.setSortingEnabled(True)
    self.table_view.setSelectionBehavior(QAbstractItemView.SelectRows)
    # QTableView Headers
    self.horizontal_header = self.table_view.horizontalHeader()
    self.vertical_header = self.table_view.verticalHeader()
    self.horizontal_header.setSectionResizeMode(
      QHeaderView.Stretch
    )
    # self.horizontal_header.setStretchLastSection(True)
    self.vertical_header.setSectionResizeMode(
      QHeaderView.ResizeToContents
    )
    self.vertical_header.setVisible(False)

    # QWidget Layout
    self.table_layout = QHBoxLayout()
    size = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
    ## Left layout
    size.setHorizontalStretch(1)
    self.table_view.setSizePolicy(size)
    self.table_layout.addWidget(self.table_view)

    self.btn_layout = QHBoxLayout()
    self.addRowBtn = QPushButton("Add")
    self.addRowBtn.setShortcut(QKeySequence.New)
    self.addRowBtn.setToolTip("Add a new row")
    self.addRowBtn.clicked.connect(self.addRowBtn_clicked)
    self.btn_layout.addWidget(self.addRowBtn)

    self.delRowBtn = QPushButton("Delete")
    self.delRowBtn.setShortcut(QKeySequence.Delete)
    self.delRowBtn.setToolTip("Delete selected row")
    self.delRowBtn.clicked.connect(self.delRowBtn_clicked)
    self.btn_layout.addWidget(self.delRowBtn)

    self.filterBtn = QPushButton("Find")
    self.filterBtn.setShortcut(QKeySequence.Find)
    self.filterBtn.setToolTip("Find a row")
    self.filterBtn.clicked.connect(self.filterBtn_clicked)
    self.btn_layout.addWidget(self.filterBtn)

    self.main_layout = QVBoxLayout()
    self.main_layout.addLayout(self.table_layout)
    self.main_layout.addLayout(self.btn_layout)

    # Set the layout to the QWidget
    self.setLayout(self.main_layout)

    self.set_model(data)

  def set_model(self, data):
    # Getting the Model
    model = CSVTableModel(data)
    proxyModel = QSortFilterProxyModel()
    proxyModel.setSourceModel(model)
    self.model = proxyModel
    self.table_view.setModel(self.model)

  def update_model(self, data):
    self.set_model(data)
    self.table_view.update()

  @pyqtSlot()
  def addRowBtn_clicked(self):
    self.model.insertRows(0, 1)
    self.table_view.scrollToBottom()
    return

  @pyqtSlot()
  def delRowBtn_clicked(self):
    rows = self.table_view.selectionModel().selectedRows()
    if len(rows) == 1:
      if rows[0].isValid():
        self.model.removeRows(rows[0].row(), 1)
    else:
      # TODO show error
      print('ERROR: Multiple rows selected. For your safety, delete one row at a time')
    return

  @pyqtSlot()
  def filterBtn_clicked(self):
    # TODO
    # https://doc.qt.io/qtforpython/PySide2/QtCore/QSortFilterProxyModel.html#filtering
    return

# Subclass QMainWindow to customize your application's main window
class MainWindow(QMainWindow):
  def __init__(self, widget):
    super().__init__()
    self.setWindowTitle("My App")
    self.create_menu_bar()
    self.table_widget = widget
    self.setCentralWidget(self.table_widget)
    geometry = qApp.desktop().availableGeometry(self)
    self.setFixedSize(geometry.width() * 0.8, geometry.height() * 0.7)
    # Status Bar
    self.status = self.statusBar()

  def create_menu_bar(self):
      menu_bar = self.menuBar()
      menu_bar.setNativeMenuBar(False)
      #Menu
      ## Exit QAction
      exit_action = QAction("Exit", self)
      exit_action.setShortcut(QKeySequence.Quit)
      exit_action.setStatusTip("Exit App")
      exit_action.triggered.connect(self.close)

      open_action = QAction("Open", self)
      open_action.setShortcut(QKeySequence.Open)
      open_action.setStatusTip("Open a CSV file")
      open_action.triggered.connect(self.open_file)

      save_action = QAction("Save", self)
      save_action.setShortcut(QKeySequence.Save)
      save_action.setStatusTip("Save to CSV file")
      save_action.triggered.connect(self.save_file)

      file_menu = menu_bar.addMenu("File")
      file_menu.addAction(open_action)
      file_menu.addAction(save_action)
      file_menu.addAction(exit_action)

  def open_file(self):
    file_name, filter = \
      QFileDialog.getOpenFileName(self, "Open file", ".",
                                  "All files (*);;CSV Files (*.csv)")

    with open(file_name) as fin:
      csv_data = [row for row in csv.reader(fin)]
    self.table_widget.update_model(csv_data)
    self.status.showMessage(file_name + " loaded")
    return

  def save_file(self):
    file_name, filter = \
      QFileDialog.getSaveFileName(self, "Open file", ".",
                                  "All files (*);;CSV Files (*.csv)")
    #TODO
    return

if __name__=='__main__':
  # You need one (and only one) QApplication instance per application.
  # Pass in sys.argv to allow command line arguments for your app.
  # If you know you won't use command line arguments QApplication([]) works too.
  app = QApplication(sys.argv)
  # Create a Qt widget, which will be our window.
  widget = Widget(None)
  window = MainWindow(widget)
  window.show()

sys.exit(app.exec_())
# Your application won't reach here until you exit and the event
# loop has stopped.
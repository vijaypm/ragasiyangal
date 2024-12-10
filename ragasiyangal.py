import csv

# Needed for PyQt5
import re
from typing import List

from PyQt6.QtCore import (Qt, QAbstractTableModel,
                          QSortFilterProxyModel, pyqtSlot,
                          QModelIndex, QRegularExpression)
from PyQt6.QtGui import (QColor, QKeySequence, QFont, QAction)
from PyQt6.QtWidgets import (QApplication, QMainWindow, QTableView,
                             QWidget, QHeaderView, QHBoxLayout,
                             QSizePolicy, QFileDialog, QAbstractItemView,
                             QPushButton, QVBoxLayout, QInputDialog,
                             QLineEdit, QMessageBox)
# Only needed for access to command line arguments
import sys

# Needed for crypto
import os
import base64
from datetime import datetime
from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import (
  Cipher, algorithms, modes
)
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

_VERSION_ = "v1.0.5"

class CSVTableModel(QAbstractTableModel):

  def __init__(self, parent=None, data=None):
    super(CSVTableModel, self).__init__(parent)
    self.load_data(data)

  def load_data(self, data):
    if data is None:
      data = [[],[]]
    self._headers = data[0]
    self._data = data[1:]
    self.reset_state()

  def reset_state(self):
    self._state = [{'new': False, 'modified': False, 'deleted': False}] * len(self._data)

  def state(self, row):
    return self._state[row]

  def data(self, index, role):
    if role == Qt.ItemDataRole.DisplayRole:
      return self._data[index.row()][index.column()]
    elif role == Qt.ItemDataRole.FontRole:
      sansFont = QFont("Helvetica", 14)
      if self._state[index.row()]['deleted']:
        sansFont.setStrikeOut(True)
      return sansFont
    elif role == Qt.ItemDataRole.TextAlignmentRole:
      return Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignVCenter
    elif role == Qt.ItemDataRole.EditRole:
      return self._data[index.row()][index.column()]
    elif role == Qt.ItemDataRole.BackgroundRole:
      if self._state[index.row()]['new']:
        return QColor(Qt.GlobalColor.cyan)
      elif self._state[index.row()]['modified']:
          return QColor(Qt.GlobalColor.yellow)
      elif self._state[index.row()]['deleted']:
        return QColor(Qt.GlobalColor.darkGray)
    return None

  def setData(self, index, value, role):
    if not index.isValid():
      return False
    if self._data[index.row()][index.column()] == value:
      #if actual text has not changed, do nothing
      return False
    self._data[index.row()][index.column()] = value
    if not self._state[index.row()]['new']:
      #existing row, mark it as edited
      self._state[index.row()] = {'new': False, 'modified': True, 'deleted': False}
    self.parent().table_view.clearSelection()
    self.parent().table_view.resizeRowsToContents()
    self.parent().parent().set_needs_save()
    return True

  def headerData(self, section, orientation, role):
    if role != Qt.ItemDataRole.DisplayRole:
      return None
    if orientation == Qt.Orientation.Horizontal:
      return self._headers[section]
    else:
      return "{}".format(section)

  def flags(self, index):
    return Qt.ItemFlag.ItemIsEnabled|Qt.ItemFlag.ItemIsEditable|Qt.ItemFlag.ItemIsSelectable

  def insertRows(self , position , rows , parent=QModelIndex()):
    # Ignore position. Always append to end of table
    # self.beginInsertRows(QModelIndex(),position,position+rows-1)
    self.beginInsertRows(QModelIndex(),len(self._data),len(self._data)+rows-1)
    columns = len(self._headers)
    for row in range(0, rows):
      self._data.append([None] * columns)
      self._state.append({'new': True, 'modified': False, 'deleted': False})
    self.endInsertRows()
    return True

  def removeRows(self , position , rows , parent=QModelIndex()):
    if self._state[position]['new']:
      #new row, just remove it from model and view
      self.beginRemoveRows(QModelIndex(),position,position+rows-1)
      for row in range(0, rows):
        del self._data[position]
      self.endRemoveRows()
    else:
      #existing row, mark it for deletion
      self._state[position] = {'new': False, 'modified': False, 'deleted': True}
      print(position, "marked deleted")
      self.dataChanged.emit(parent, parent, [])
    return True

  def rowCount(self, index):
    # The length of the outer list.
    return len(self._data)

  def columnCount(self, index):
    # The following takes the first sub-list, and returns
    # the length (only works if all rows are an equal length)
    return len(self._data[0])

  def row(self, row_num):
    return self._data[row_num]

class CustomSortFilterProxyModel(QSortFilterProxyModel):
  def filterAcceptsRow(self, row_num, parent):
    filterString = self.filterRegularExpression().pattern()
    if not filterString:
      # nothing to filter
      return True
    model = self.sourceModel()
    row = model.row(row_num)
    if not row:
      return False
    tests = [filterString in col for col in filter(None,row)]
    if not tests:
      # brand new row with None in all columns
      return True
    return True in tests

class TableWidget(QWidget):
    def __init__(self, data):
        QWidget.__init__(self)

        # Creating a QTableView
        self.table_view = QTableView()
        self.table_view.setAlternatingRowColors(True)
        self.table_view.setSortingEnabled(True)
        self.table_view.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )
        # QTableView Headers
        self.horizontal_header = self.table_view.horizontalHeader()
        self.vertical_header = self.table_view.verticalHeader()
        self.horizontal_header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        # self.horizontal_header.setStretchLastSection(True)
        self.vertical_header.setSectionResizeMode(
            QHeaderView.ResizeMode.ResizeToContents
        )
        self.vertical_header.setVisible(False)

        # QWidget Layout
        self.table_layout = QHBoxLayout()
        size = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        ## Left layout
        size.setHorizontalStretch(1)
        self.table_view.setSizePolicy(size)
        self.table_layout.addWidget(self.table_view)

        self.btn_layout = QHBoxLayout()
        self.addRowBtn = QPushButton("Add")
        self.addRowBtn.setShortcut(QKeySequence(Qt.Key.Key_Control + Qt.Key.Key_Down))
        self.addRowBtn.setToolTip("Add a new row")
        self.addRowBtn.clicked.connect(self.addRowBtn_clicked)
        self.btn_layout.addWidget(self.addRowBtn)

        self.delRowBtn = QPushButton("Delete")
        self.delRowBtn.setShortcut(QKeySequence.StandardKey.Delete)
        self.delRowBtn.setToolTip("Delete selected row")
        self.delRowBtn.clicked.connect(self.delRowBtn_clicked)
        self.btn_layout.addWidget(self.delRowBtn)

        self.filterBtn = QPushButton("Filter")
        self.filterBtn.setShortcut(QKeySequence.StandardKey.Find)
        self.filterBtn.setToolTip("Filter rows")
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
        model = CSVTableModel(self, data)
        # proxyModel = QSortFilterProxyModel()
        proxyModel = CustomSortFilterProxyModel()
        proxyModel.setSourceModel(model)
        self.model = proxyModel
        self.table_view.setModel(self.model)

    def update_model(self, data):
        self.set_model(data)
        self.table_view.update()

    def reset_model_state(self):
        self.model.sourceModel().reset_state()

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
                self.parent().set_needs_save()
        else:
            QMessageBox.critical(
                self,
                "Multiple Rows Selected!",
                "For your safety, delete one row at a time",
            )
        return

    @pyqtSlot()
    def filterBtn_clicked(self):
        # filterBtn = self.sender()
        # https://doc.qt.io/qtforpython/PySide2/QtCore/QSortFilterProxyModel.html#filtering
        text, okPressed = QInputDialog.getText(
            self, "Find Text", "Text:", QLineEdit.EchoMode.Normal, ""
        )
        if okPressed:
            filterRegexp = QRegularExpression(
                text,
                options= QRegularExpression.PatternOption.CaseInsensitiveOption
                      | QRegularExpression.PatternOption.ExtendedPatternSyntaxOption,
            )
            self.model.setFilterRegularExpression(filterRegexp)
            if text:
                self.filterBtn.setText("Clear Filter: " + text)
                self.filterBtn.setStyleSheet("background-color: red")
                self.table_view.parent().parent().setFilter(True)
            else:
                self.filterBtn.setText("Filter")
                self.filterBtn.setStyleSheet("")
                self.table_view.parent().parent().setFilter(False)
            self.filterBtn.setShortcut(QKeySequence.StandardKey.Find)
            self.filterBtn.setToolTip("Filter rows")
        return

# Subclass QMainWindow to customize your application's main window
class MainWindow(QMainWindow):

  def __init__(self, widget):
    super().__init__()
    self.setWindowTitle("Ragasiyangal - Password Manager")
    self.create_menu_bar()
    widget.setParent(self)
    self.table_widget = widget
    self.setCentralWidget(self.table_widget)
    geometry = QApplication.primaryScreen().availableGeometry()
    self.setMinimumSize(int(geometry.width() * 0.8), int(geometry.height() * 0.7))
    # Status Bar
    self.status = self.statusBar()
    self.needs_save = False
    self.filter_on = False

  def setFilter(self, enabled:bool):
    self.filter_on = enabled

  def is_filter_on(self):
    if self.filter_on:
      QMessageBox.critical(self,
                           "Filter is on!",
                           "Please clear the filter before you attempt any File operations.")
    return self.filter_on

  def create_menu_bar(self):
      menu_bar = self.menuBar()
      menu_bar.setNativeMenuBar(False)
      #Menu
      ## Exit QAction
      exit_action = QAction("Exit", self)
      exit_action.setShortcut(QKeySequence.StandardKey.Quit)
      exit_action.setStatusTip("Exit App")
      exit_action.triggered.connect(self.close)

      open_action = QAction("Open", self)
      open_action.setShortcut(QKeySequence.StandardKey.Open)
      open_action.setStatusTip("Open a CSV file")
      open_action.triggered.connect(self.open_file)

      new_action = QAction("New", self)
      new_action.setShortcut(QKeySequence.StandardKey.New)
      new_action.setStatusTip("Create a New document")
      new_action.triggered.connect(self.new_file)

      save_action = QAction("Save", self)
      save_action.setShortcut(QKeySequence.StandardKey.Save)
      save_action.setStatusTip("Save to CSV file")
      save_action.triggered.connect(self.save_file)

      file_menu = menu_bar.addMenu("File")
      file_menu.addAction(new_action)
      file_menu.addAction(open_action)
      file_menu.addAction(save_action)
      file_menu.addAction(exit_action)

      import_action = QAction("Import", self)
      import_action.setStatusTip("Import an unencrypted CSV file")
      import_action.triggered.connect(self.import_file)

      other_menu = menu_bar.addMenu("Other")
      other_menu.addAction(import_action)

      about_action = QAction("About", self)
      about_action.setStatusTip("About this app")
      about_action.triggered.connect(self.about)

      about_menu = menu_bar.addMenu("About")
      about_menu.addAction(about_action)

  def about(self):
    QMessageBox.about(self, "About Ragasiyangal - " + _VERSION_,
                      "Ragasiyangal - " + _VERSION_ + "\n" + \
                      "This software comes without warranty, liability or support! \n" + \
                      "For more information, check out https://github.com/vijaypm/ragasiyangal")

  def new_file(self):
    if self.is_filter_on():
      return
    csv_data = [['AccountName', 'Username', 'Password', 'Comments'], ['', '', '', '']]
    self.table_widget.update_model(csv_data)
    self.reset_needs_save()

  def import_file(self):
    if self.is_filter_on():
      return
    file_name, filter = \
      QFileDialog.getOpenFileName(self, "Open file", ".",
                                  "CSV Files (*.csv *.txt);;All files (*)")
    if not file_name:
      return
    with open(file_name) as fin:
      csv_data = [row for row in csv.reader(fin)]
    if csv_data:
      self.table_widget.update_model(csv_data)
      self.set_needs_save()
      self.status.showMessage(file_name + " imported. Needs to be saved")
    return

  def open_file(self):
    if self.is_filter_on():
      return
    file_name, filter = \
      QFileDialog.getOpenFileName(self, "Open file", ".",
                                  "CSV Files (*.csv *.txt);;All files (*)")
    if not file_name:
      return
    num_tries = 1
    while num_tries <= 5 :
      password, ok = QInputDialog().getText(self, "Attention",
                                        "Password:",
                                        QLineEdit.EchoMode.Password if num_tries <= 2 else QLineEdit.EchoMode.Normal,
                                        "")
      if ok:
        csv_data = None
        try:
          csv_data = self.__decrypt_file(file_name, password)
        except:
          print(sys.exc_info())
          pass
        if csv_data:
          self.table_widget.update_model(csv_data)
          self.reset_needs_save()
          self.status.showMessage(file_name + " loaded")
          break
        else:
          num_tries = num_tries + 1
          QMessageBox.critical(self,
                            "Wrong Password!",
                            "You entered the wrong password. Please try again.")
      else:
        return
    return

  def save_file(self):
    if self.is_filter_on():
      return
    if not self.needs_save:
      QMessageBox.information(self,
                              "Nothing to Save",
                              "You have not entered any data.")
      return
    file_name, filter = \
      QFileDialog.getSaveFileName(self, "Open file", "." + "/export.csv",
                                  "CSV Files (*.csv *.txt);;All files (*)")
    if not file_name:
      return
    password = self.show_password_create()
    if not password:
      return
    file_saved = self.__encrypt_file(file_name, password)
    if file_saved:
      # reload saved file as a sanity check
      try:
        csv_data = self.__decrypt_file(file_name, password)
        if csv_data:
          self.status.showMessage(file_name + " saved")
          self.table_widget.update_model(csv_data)
          self.reset_needs_save()
      except:
        self.status.showMessage("Error saving file")
        QMessageBox.critical(self,
                             "Error Saving File!",
                             "Please try again! To avoid risk of losing data, " +
                                    "you can copy the content manually or take a screenshot.")

  def __encrypt_file(self, file_name, password):
    # generate a key using password and random salt
    password_bytes = bytes(password, 'utf-8')
    salt_bytes = os.urandom(32)
    key = Crypto.derive_key(password_bytes, salt_bytes)

    # start writing to file
    with open(file_name, "w") as fileOutput:
      # write salt to file as a comment metadata
      # https://www.w3.org/TR/tabular-data-model/#embedded-metadata
      fileOutput.write('# ' + base64.urlsafe_b64encode(salt_bytes).decode('utf-8') + '\n')

      # prepare to write csv table data
      writer = csv.writer(fileOutput)

      # write csv headers
      headers = [self.table_widget.model.headerData(c, Qt.Orientation.Horizontal)
                 for c in range(self.table_widget.model.columnCount())]
      writer.writerow(Crypto.encrypt_row(key, headers))

      #write csv rows
      for row in range(self.table_widget.model.rowCount()):
        if self.table_widget.model.sourceModel().state(row)['deleted']:
          continue
        rowdata = [
          self.table_widget.model.data(
            self.table_widget.model.index(row, column),
            Qt.ItemDataRole.DisplayRole
          )
          for column in range(self.table_widget.model.columnCount())
        ]
        writer.writerow(Crypto.encrypt_row(key, rowdata))
    return True

  def __decrypt_file(self, file_name, password):
    password_bytes = bytes(password, "utf-8")
    with open(file_name) as fin:
      reader = csv.reader(fin)
      salt_bytes = base64.urlsafe_b64decode(bytes(next(reader, None)[0].lstrip('#').strip(), 'utf-8'))
      key = Crypto.derive_key(password_bytes, salt_bytes)
      csv_data = [Crypto.decrypt_row(key, row) for row in csv.reader(fin)]
    return csv_data

  def show_password_create(self):
    password, confirm_password = '', None
    num_tries = 1
    ok = True
    while ok and password != confirm_password:
      password, ok = QInputDialog().getText(self, "Attention",
                                            "Password:",
                                            QLineEdit.EchoMode.Password if num_tries <= 2 else QLineEdit.EchoMode.Normal,
                                            "")
      if ok and password:
        pwd_chk = Crypto.password_check(password)
        if not pwd_chk['password_ok']:
          # weak password
          # Password should be longer than 8 characters
          # and have at least 1 upper case, 1 lower case, 1 number and 1 symbol
          reply = QMessageBox.question(self, 'Weak Password',
                                       'The password you entered is weak because:\n' + \
                                        pwd_chk['error_msg'] + \
                                       '\n\n\n Do you want to try a stronger password ?',
                               QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.Yes)
          if reply == QMessageBox.StandardButton.Yes:
            continue
        # strong password
        confirm_password, ok = QInputDialog().getText(self, "Attention",
                                            "Re-enter Password to confirm:",
                                            QLineEdit.EchoMode.Password if num_tries <= 2 else QLineEdit.EchoMode.Normal,
                                            "")
        if password != confirm_password:
          QMessageBox.critical(self, "Mismatch!", "Passwords don't match")
          num_tries = num_tries + 1
        else:
          return password
    return None

  def closeEvent(self, event):
    if self.needs_save:
      reply = QMessageBox.question(self, 'Window Close',
                                   'You have unsaved changes.\n Are you sure you want to close the window?',
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No)

      if reply == QMessageBox.StandardButton.No:
        event.ignore()
        return
    event.accept()

  def set_needs_save(self):
    self.needs_save = True
    self.status.setStyleSheet("background-color : red")
    self.status.showMessage("WARNING: Data changed and needs to be saved")

  def reset_needs_save(self):
    self.needs_save = False
    self.statusBar().setStyleSheet("")
    self.status.showMessage("")

class Crypto:

  delimiter = '|'

  @classmethod
  def password_check(cls, password):
    """
    credit: https://stackoverflow.com/a/32542964/8991379
    Verify the strength of 'password'
    Returns a dict indicating the wrong criteria
    A password is considered strong if:
        8 characters length or more
        1 digit or more
        1 symbol or more
        1 uppercase letter or more
        1 lowercase letter or more
    """
    error_msgs = []

    # calculating the length
    length_error = len(password) < 8
    if length_error:
      error_msgs.append("Length is less than 8.")

    # searching for digits
    digit_error = re.search(r"\d", password) is None
    if digit_error:
      error_msgs.append("Does not have at least 1 number.")

    # searching for uppercase
    uppercase_error = re.search(r"[A-Z]", password) is None
    if uppercase_error:
      error_msgs.append("Does not have at least 1 UPPER case letter.")

    # searching for lowercase
    lowercase_error = re.search(r"[a-z]", password) is None
    if lowercase_error:
      error_msgs.append("Does not have at least 1 lower case letter.")

    # searching for symbols
    # symbol_error = re.search(r"[ !#$%&'()*+,-./[\\\]^_`{|}~" + r'"]', password) is None
    symbol_error = re.search(r"\W", password) is None
    if symbol_error:
      error_msgs.append("Does not have at least 1 special symbol.")

    # overall result
    password_ok = not (length_error or digit_error or uppercase_error or lowercase_error or symbol_error)

    return {
      'password_ok': password_ok,
      'length_error': length_error,
      'digit_error': digit_error,
      'uppercase_error': uppercase_error,
      'lowercase_error': lowercase_error,
      'symbol_error': symbol_error,
      'error_msg': '\n'.join(error_msgs)
    }

  @classmethod
  def get_fernet(cls, password:bytes, salt: bytes):
    kdf = PBKDF2HMAC(
      algorithm=hashes.SHA256(),
      length=32,
      salt=salt,
      iterations=100000,
      backend=default_backend()
    )
    key = base64.urlsafe_b64encode(kdf.derive(password))
    f = Fernet(key)
    return f

  @classmethod
  def derive_key(cls, password:bytes, salt:bytes):
    kdf = PBKDF2HMAC(
      algorithm=hashes.SHA256(),
      length=32,
      salt=salt,
      iterations=100000,
      backend=default_backend()
    )
    key = kdf.derive(password)
    return key

  @classmethod
  def encrypt_aesgcm(cls, key, plaintext:bytes, associated_data:bytes):
    # Generate a random 96-bit IV.
    iv = os.urandom(12)

    # Construct an AES-GCM Cipher object with the given key and a
    # randomly generated IV.
    encryptor = Cipher(
      algorithms.AES(key),
      modes.GCM(iv),
      backend=default_backend()
    ).encryptor()

    # associated_data will be authenticated but not encrypted,
    # it must also be passed in on decryption.
    encryptor.authenticate_additional_data(associated_data)

    # Encrypt the plaintext and get the associated ciphertext.
    # GCM does not require padding.
    ciphertext = encryptor.update(plaintext) + encryptor.finalize()

    return (iv, ciphertext, encryptor.tag)

  @classmethod
  def decrypt_aesgcm(cls, key, associated_data:bytes, iv:bytes, ciphertext:bytes, tag:bytes):
    # Construct a Cipher object, with the key, iv, and additionally the
    # GCM tag used for authenticating the message.
    decryptor = Cipher(
      algorithms.AES(key),
      modes.GCM(iv, tag),
      backend=default_backend()
    ).decryptor()

    # We put associated_data back in or the tag will fail to verify
    # when we finalize the decryptor.
    decryptor.authenticate_additional_data(associated_data)

    # Decryption gets us the authenticated plaintext.
    # If the tag does not match an InvalidTag exception will be raised.
    return decryptor.update(ciphertext) + decryptor.finalize()

  @classmethod
  def encrypt_row(cls, key, row:List[str]):
    associated_data = bytes(datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3], 'utf-8')
    encr_row = []
    for field in row:
      if not field:
        encr_row.append('')
        continue
      field_bytes = bytes(field, 'utf-8')
      iv, ciphertext, tag = Crypto.encrypt_aesgcm(key, field_bytes, associated_data)
      encr_field = base64.urlsafe_b64encode(associated_data).decode('utf-8') + Crypto.delimiter \
                  + base64.urlsafe_b64encode(ciphertext).decode('utf-8') + Crypto.delimiter \
                  + base64.urlsafe_b64encode(iv).decode('utf-8') + Crypto.delimiter \
                  + base64.urlsafe_b64encode(tag).decode('utf-8')
      encr_row.append(encr_field)
    return encr_row

  @classmethod
  def decrypt_row(cls, key, encr_row):
    row = []
    for field in encr_row:
      if not field:
        row.append('')
        continue
      field_splits = field.split(Crypto.delimiter)
      associated_data = base64.urlsafe_b64decode(bytes(field_splits[0], 'utf-8'))
      ciphertext = base64.urlsafe_b64decode(bytes(field_splits[1], 'utf-8'))
      iv = base64.urlsafe_b64decode(bytes(field_splits[2], 'utf-8'))
      tag = base64.urlsafe_b64decode(bytes(field_splits[3], 'utf-8'))
      plaintext_bytes = Crypto.decrypt_aesgcm(key, associated_data, iv, ciphertext, tag)
      row.append(plaintext_bytes.decode('utf-8'))
    return row

if __name__=='__main__':
  # You need one (and only one) QApplication instance per application.
  # Pass in sys.argv to allow command line arguments for your app.
  # If you know you won't use command line arguments QApplication([]) works too.
  app = QApplication(sys.argv)
  # Create a Qt widget, which will be our window.
  widget = TableWidget(None)
  window = MainWindow(widget)
  window.show()
  sys.exit(app.exec())
# Your application won't reach here until you exit and the event
# loop has stopped.
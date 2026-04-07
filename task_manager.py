#---------------------------------#
#Nama   : Didy Ardiyanto
#NIM    : F1D02310046
#Kelas  : C
#----------------------------------#
import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QTableWidget, 
    QTableWidgetItem, QToolBar, QStatusBar, QPushButton, QLineEdit, 
    QComboBox, QDialog, QFormLayout, QDateEdit, QDialogButtonBox, 
    QMessageBox, QHeaderView, QLabel
)
from PySide6.QtGui import QAction, QColor, QBrush, QIcon
from PySide6.QtCore import Qt, QDate

class TaskDialog(QDialog):
    def __init__(self, parent=None, task_data=None):
        super().__init__(parent)
        self.setWindowTitle("Formulir Pengisian Tugas")
        self.setMinimumWidth(300)
        
        layout = QFormLayout(self)
        
        self.judul_edit = QLineEdit()
        self.judul_edit.setPlaceholderText("Masukkan judul tugas...")
        
        self.prioritas_combo = QComboBox()
        self.prioritas_combo.addItems(["Low", "Medium", "High"])
        
        self.status_combo = QComboBox()
        self.status_combo.addItems(["Pending", "In Progress", "Completed"])
        
        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDate(QDate.currentDate())

        if task_data:
            self.judul_edit.setText(task_data['judul'])
            self.prioritas_combo.setCurrentText(task_data['prioritas'])
            self.status_combo.setCurrentText(task_data['status'])
            self.date_edit.setDate(QDate.fromString(task_data['due_date'], Qt.DateFormat.ISODate))
 
        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        
        layout.addRow("Judul Tugas:", self.judul_edit)
        layout.addRow("Prioritas:", self.prioritas_combo)
        layout.addRow("Status:", self.status_combo)
        layout.addRow("Due Date:", self.date_edit)
        layout.addWidget(self.button_box)

    def get_data(self):
        return {
            "judul": self.judul_edit.text(),
            "prioritas": self.prioritas_combo.currentText(),
            "status": self.status_combo.currentText(),
            "due_date": self.date_edit.date().toString(Qt.DateFormat.ISODate)
        }

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Aplikasi Pengelola Tugas")
        self.resize(800, 500)

        self.apply_qss()
    
        self.setup_ui()
        self.update_statusbar()

    def apply_qss(self):
        self.setStyleSheet("""
            QMainWindow { background-color: #f4f6f9; }
            QTableWidget { 
                background-color: #ffffff; 
                gridline-color: #d1d5db; 
                font-size: 13px; 
                border: 1px solid #d1d5db;
                border-radius: 5px;
            }
            QHeaderView::section { 
                background-color: #2c3e50; 
                color: white; 
                padding: 6px; 
                font-weight: bold; 
                border: none;
            }
            QPushButton { 
                background-color: #3498db; 
                color: white; 
                border-radius: 4px; 
                padding: 6px 12px; 
                font-weight: bold;
            }
            QPushButton:hover { background-color: #2980b9; }
            
            QPushButton[text="Tambah"] { background-color: #2ecc71; }
            QPushButton[text="Tambah"]:hover { background-color: #27ae60; }
            
            QPushButton[text="Hapus"] { background-color: #e74c3c; }
            QPushButton[text="Hapus"]:hover { background-color: #c0392b; }
            
            QLineEdit, QComboBox, QDateEdit { 
                padding: 5px; 
                border: 1px solid #bdc3c7; 
                border-radius: 4px; 
                background: white;
            }
            QStatusBar { background-color: #ecf0f1; color: #2c3e50; font-weight: bold; }
        """)

    def setup_ui(self):

        menubar = self.menuBar()
        file_menu = menubar.addMenu("File")
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        toolbar = QToolBar("Main Toolbar")
        self.addToolBar(toolbar)
        
        self.btn_add = QPushButton("Tambah")
        self.btn_add.clicked.connect(self.add_task)
        toolbar.addWidget(self.btn_add)
        
        self.btn_edit = QPushButton("Edit")
        self.btn_edit.clicked.connect(self.edit_task)
        toolbar.addWidget(self.btn_edit)
        
        self.btn_delete = QPushButton("Hapus")
        self.btn_delete.clicked.connect(self.delete_task)
        toolbar.addWidget(self.btn_delete)
        
        toolbar.addSeparator()
   
        toolbar.addWidget(QLabel("  Filter: "))
        self.filter_combo = QComboBox()
        self.filter_combo.addItems(["All", "High", "Medium", "Low"])
        self.filter_combo.currentIndexChanged.connect(self.filter_tasks)
        toolbar.addWidget(self.filter_combo)
        
        toolbar.addSeparator()

        toolbar.addWidget(QLabel("  Search: "))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Cari judul...")
        self.search_input.textChanged.connect(self.filter_tasks)
        toolbar.addWidget(self.search_input)

        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["No", "Judul", "Prioritas", "Status", "Due Date"])
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
 
        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)
        layout.addWidget(self.table)
        self.setCentralWidget(central_widget)

        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)

    def add_task(self):
        dialog = TaskDialog(self)
        if dialog.exec():
            data = dialog.get_data()
            if not data['judul'].strip():
                QMessageBox.warning(self, "Peringatan", "Judul tidak boleh kosong!")
                return
            self.insert_row(data)
            self.update_statusbar()

    def edit_task(self):
        selected_row = self.table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "Peringatan", "Pilih baris yang ingin diedit!")
            return

        current_data = {
            "judul": self.table.item(selected_row, 1).text(),
            "prioritas": self.table.item(selected_row, 2).text(),
            "status": self.table.item(selected_row, 3).text(),
            "due_date": self.table.item(selected_row, 4).text()
        }

        dialog = TaskDialog(self, current_data)
        if dialog.exec():
            new_data = dialog.get_data()
            self.update_row(selected_row, new_data)

    def delete_task(self):
        selected_row = self.table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "Peringatan", "Pilih baris yang ingin dihapus!")
            return

        judul_task = self.table.item(selected_row, 1).text()
        reply = QMessageBox.question(self, 'Konfirmasi Hapus', 
                                     f"Apakah Anda yakin ingin menghapus task '{judul_task}'?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            self.table.removeRow(selected_row)
            self.reindex_table()
            self.update_statusbar()

    def insert_row(self, data):
        row_idx = self.table.rowCount()
        self.table.insertRow(row_idx)
        self.update_row(row_idx, data)
        self.reindex_table()

    def update_row(self, row_idx, data):
        self.table.setItem(row_idx, 1, QTableWidgetItem(data['judul']))
        self.table.setItem(row_idx, 2, QTableWidgetItem(data['prioritas']))
        self.table.setItem(row_idx, 3, QTableWidgetItem(data['status']))
        self.table.setItem(row_idx, 4, QTableWidgetItem(data['due_date']))
        self.apply_row_color(row_idx, data['prioritas'])

    def apply_row_color(self, row_idx, prioritas):
        color = QColor(255, 255, 255)
        if prioritas == "High":
            color = QColor(255, 182, 193)
        elif prioritas == "Medium":
            color = QColor(255, 250, 160)
        elif prioritas == "Low":
            color = QColor(144, 238, 144)

        brush = QBrush(color)
        for col in range(5):
            item = self.table.item(row_idx, col)
            if item:
                item.setBackground(brush)

    def reindex_table(self):
        for i in range(self.table.rowCount()):
            item_no = QTableWidgetItem(str(i + 1))

            if self.table.item(i, 2): 
                prioritas = self.table.item(i, 2).text()
                self.apply_row_color(i, prioritas)
            self.table.setItem(i, 0, item_no)
            self.table.item(i, 0).setBackground(self.table.item(i, 1).background())

    def filter_tasks(self):
        search_query = self.search_input.text().lower()
        filter_prio = self.filter_combo.currentText()

        visible_count = 0
        for row in range(self.table.rowCount()):
            item_judul = self.table.item(row, 1)
            item_prio = self.table.item(row, 2)
            
            if item_judul and item_prio:
                match_search = search_query in item_judul.text().lower()
                match_prio = (filter_prio == "All") or (item_prio.text() == filter_prio)
        
                if match_search and match_prio:
                    self.table.setRowHidden(row, False)
                    visible_count += 1
                else:
                    self.table.setRowHidden(row, True)
                    
        self.statusbar.showMessage(f"Menampilkan {visible_count} dari total {self.table.rowCount()} task.")

    def update_statusbar(self):
        total = self.table.rowCount()
        self.statusbar.showMessage(f"Total Task: {total}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
# ui_loader.py
from PySide6.QtWidgets import QFileDialog, QApplication, QLineEdit, QToolBar, QWidget, QPushButton, QDialog
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile, Qt, QObject
from PySide6.QtGui import QWheelEvent, QKeyEvent
from pdf_handler import PDFHandler
from organize_dialog import OrganizeDialog
import os

class MainWindow(QObject):
    def __init__(self):
        super().__init__()
        loader = QUiLoader()

        file = QFile("mainwindow.ui")
        file.open(QFile.ReadOnly)

        self.ui = loader.load(file)
        file.close()
        
        self.pdf_handler = PDFHandler(self.ui.pdfView)
        self.setup_search_bar()
        
        self.ui.pdfView.installEventFilter(self)
        self.ui.installEventFilter(self)
        self.ui.pdfView.viewport().installEventFilter(self)

        self.ui.buttonOpen.clicked.connect(self.open_pdf)
        self.ui.actionZoomIn.triggered.connect(self.pdf_handler.zoom_in)
        self.ui.actionZoomOut.triggered.connect(self.pdf_handler.zoom_out)
        self.ui.actionPrint.triggered.connect(lambda: self.pdf_handler.print_pdf())
        self.ui.actionPrintPreview.triggered.connect(lambda: self.pdf_handler.print_preview())
        self.ui.pdfView.verticalScrollBar().valueChanged.connect(self.update_page_indicator)
        self.ui.actionFind.triggered.connect(self.toggle_search)
        self.ui.actionOpen_menu.triggered.connect(self.open_pdf)
        self.ui.buttonOrganize.clicked.connect(self.open_organize_dialog)

    def show(self):
        self.ui.show()

    def open_pdf(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self.ui,
            "Open PDF File",
            "",
            "PDF Files (*.pdf)"  # PDF only
        )

        if file_path:
            self.pdf_handler.load_pdf(file_path)
            filename = os.path.basename(file_path)
            self.ui.setWindowTitle(f"Portal PDF - {filename}")
            self.update_page_indicator()
    
    def update_page_indicator(self):
        if self.pdf_handler.doc:
            current = self.pdf_handler.get_current_page()
            total = self.pdf_handler.get_page_count()
            self.ui.statusBar().showMessage(f"Page {current} of {total}")
    
    def eventFilter(self, obj, event):
        if isinstance(event, QWheelEvent) and obj == self.ui.pdfView.viewport():
            if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
                if event.angleDelta().y() > 0:
                    self.pdf_handler.zoom_in()
                else:
                    self.pdf_handler.zoom_out()
                return True

        if isinstance(event, QKeyEvent):
            if event.key() == Qt.Key.Key_Escape:
                if not self.search_toolbar.isHidden():
                    self.toggle_search()
                    return True
        return False
    
    def setup_search_bar(self):       
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search...")
        self.buttonCloseSearch = QPushButton("✕")       
        
        self.search_bar.returnPressed.connect(self.do_search)
        self.buttonCloseSearch.clicked.connect(self.toggle_search)
        
        self.search_toolbar = QToolBar("Search")
        self.ui.addToolBar(Qt.ToolBarArea.TopToolBarArea, self.search_toolbar)
        
        self.search_toolbar.addWidget(self.search_bar)
        self.search_toolbar.addWidget(self.buttonCloseSearch)
        self.search_toolbar.hide()
           
    def toggle_search(self):
        if self.search_toolbar.isHidden():
            self.search_toolbar.show()
            self.search_bar.setFocus()
        else:
            self.search_toolbar.hide()
            self.search_bar.clear()
            self.pdf_handler.clear_search()
    
    def do_search(self):
        query = self.search_bar.text()
        if query:
            self.pdf_handler.search_text(query)
    
    def open_organize_dialog(self):
        if not self.pdf_handler.doc:
            return
        
        dialog = OrganizeDialog(self.pdf_handler.doc, self.ui)
        if dialog.exec() == QDialog.Accepted:
            new_order = dialog.get_new_order()
            self.pdf_handler.apply_organize(new_order)
            self.update_page_indicator()
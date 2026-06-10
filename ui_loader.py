# ui_loader.py
from PySide6.QtWidgets import QFileDialog, QApplication
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile, Qt, QObject
from PySide6.QtGui import QWheelEvent
from pdf_handler import PDFHandler
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
        
        self.ui.pdfView.installEventFilter(self)
        self.ui.pdfView.viewport().installEventFilter(self)

        self.ui.buttonOpen.clicked.connect(self.open_pdf)
        self.ui.actionZoomIn.triggered.connect(self.pdf_handler.zoom_in)
        self.ui.actionZoomOut.triggered.connect(self.pdf_handler.zoom_out)
        self.ui.actionPrint.triggered.connect(lambda: self.pdf_handler.print_pdf())
        self.ui.actionPrintPreview.triggered.connect(lambda: self.pdf_handler.print_preview())
        self.ui.pdfView.verticalScrollBar().valueChanged.connect(self.update_page_indicator)

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
        return False
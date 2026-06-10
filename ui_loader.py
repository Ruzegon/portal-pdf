# ui_loader.py
from PySide6.QtWidgets import QFileDialog
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile
from pdf_handler import PDFHandler
import os

class MainWindow:
    def __init__(self):
        loader = QUiLoader()

        file = QFile("mainwindow.ui")
        file.open(QFile.ReadOnly)

        self.ui = loader.load(file)
        file.close()
        
        self.pdf_handler = PDFHandler(self.ui.pdfView)

        self.ui.buttonOpen.clicked.connect(self.open_pdf)
        self.ui.actionZoomIn.triggered.connect(self.pdf_handler.zoom_in)
        self.ui.actionZoomOut.triggered.connect(self.pdf_handler.zoom_out)
        self.ui.actionPrint.triggered.connect(lambda: self.pdf_handler.print_pdf())
        self.ui.actionPrintPreview.triggered.connect(lambda: self.pdf_handler.print_preview())

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
            page_count = self.pdf_handler.get_page_count()
            self.ui.statusBar().showMessage(f"Pages: {page_count}")
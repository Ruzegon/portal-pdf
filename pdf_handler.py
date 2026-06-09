# pdf_handler.py
import fitz
from PySide6.QtWidgets import QLabel, QWidget, QVBoxLayout
from PySide6.QtPrintSupport import QPrinter, QPrintDialog, QPrintPreviewDialog
from PySide6.QtGui import QPixmap, QImage, QPainter
from PySide6.QtCore import Qt

class PDFHandler:
    def __init__(self, scroll_area):
        self.doc = None
        self.scroll_area = scroll_area
        self.zoom_factor = 1.0
        self.base_dpi = 3.0

    def load_pdf(self, file_path):
        # open PDF
        self.doc = fitz.open(file_path)
        self.render_pages()         
    
    def render_pages(self):
        container = QWidget()
        layout = QVBoxLayout(container)

        # loop page
        for page_num in range(len(self.doc)):
            page = self.doc[page_num]

            # page to img
            mat = fitz.Matrix(self.base_dpi * self.zoom_factor, self.base_dpi * self.zoom_factor)
            pix = page.get_pixmap(matrix=mat)

            img = QImage(pix.samples, pix.width, pix.height, pix.stride, QImage.Format.Format_RGB888)
            qt_image = QPixmap.fromImage(img)
            scaled = qt_image.scaledToWidth(
                int(page.rect.width * self.zoom_factor * (96/72)),
                Qt.TransformationMode.SmoothTransformation
            )

            label = QLabel()
            label.setPixmap(scaled)
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(label)
        self.scroll_area.setWidget(container)

    def zoom_in(self):
        self.zoom_factor += 0.1
        self.render_pages()
    
    def zoom_out(self):
        if self.zoom_factor > 0.1:
            self.zoom_factor -= 0.1
            self.render_pages()
    
    def print_pdf(self, printer=None):
        if not self.doc:
            return
        
        if printer is None:
            printer = QPrinter()
            dialog = QPrintDialog(printer)
            if dialog.exec() != QPrintDialog.DialogCode.Accepted:
                return
        if isinstance(printer, QPrinter):
            self._paint_pages(printer)
        
    def _paint_pages(self, printer):
        painter = QPainter(printer)
        page_rect = printer.pageRect(QPrinter.Unit.DevicePixel)
        for page_num in range(len(self.doc)):
            page = self.doc[page_num]
            mat = fitz.Matrix(self.base_dpi, self.base_dpi)
            pix = page.get_pixmap(matrix=mat)

            img = QImage(pix.samples, pix.width, pix.height, pix.stride, QImage.Format.Format_RGB888)
            qt_image = QPixmap.fromImage(img)
            
            scaled = qt_image.scaled(
                int(page_rect.width()),
                int(page_rect.height()),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )

            painter.drawPixmap(0, 0, scaled)
            
            if page_num < len(self.doc) - 1:
                printer.newPage()
        painter.end()
    
    def print_preview(self):
        if not self.doc:
            return
        
        printer = QPrinter()
        preview = QPrintPreviewDialog(printer)
        preview.paintRequested.connect(lambda p: self._paint_pages(p))
        preview.exec()
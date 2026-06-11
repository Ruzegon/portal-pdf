# pdf_handler.py
import fitz
from PySide6.QtWidgets import QLabel, QWidget, QVBoxLayout
from PySide6.QtPrintSupport import QPrinter, QPrintDialog, QPrintPreviewDialog
from PySide6.QtGui import QColor, QPixmap, QImage, QPainter
from PySide6.QtCore import Qt

class PDFHandler:
    def __init__(self, scroll_area):
        self.doc = None
        self.scroll_area = scroll_area
        self.zoom_factor = 1.0
        self.base_dpi = 3.0
        
        self.search_term = ""
        
        self.current_file_path = None

    def load_pdf(self, file_path):
        # open PDF
        self.doc = fitz.open(file_path)
        self.current_file_path = file_path
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

            results = page.search_for(self.search_term) if self.search_term else []
            if results:
                painter = QPainter(scaled)
                painter.setBrush(QColor(255, 255, 0, 128))
                painter.setPen(Qt.PenStyle.NoPen)
                
                scale_x = scaled.width() / qt_image.width()
                scale_y = scaled.height() / qt_image.height()
                render_scale = self.base_dpi * self.zoom_factor
                for rect in results:
                    painter.drawRect(
                        int(rect.x0 * render_scale * scale_x),
                        int(rect.y0 * render_scale * scale_y),
                        int((rect.x1 - rect.x0) * render_scale * scale_x),
                        int((rect.y1 - rect.y0) * render_scale * scale_y)
                    )
                painter.end()

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

    def get_page_count(self):
        if self.doc:
            return len(self.doc)
        return 0
    
    def get_current_page(self):
        scroll_y = self.scroll_area.verticalScrollBar().value()
        total_height = self.scroll_area.verticalScrollBar().maximum()
        if total_height == 0:
            return 1
        current = ((scroll_y / total_height) * len(self.doc)) + 1
        return max(1, min(int(current), len(self.doc)))

    def search_text(self, search_term):
        self.search_term = search_term
        self.render_pages()
    
    def clear_search(self):
        self.search_term = ""
        self.render_pages()
    
    def apply_organize(self, new_order):
        if not self.doc:
            return
        
        new_doc = fitz.open()
        for page_num in new_order:
            new_doc.insert_pdf(self.doc, from_page=page_num, to_page=page_num)
        
        self.doc.close()
        self.doc = new_doc
        self.render_pages()
    
    def save_pdf(self, file_path=None):
        if not self.doc:
            return
        
        if file_path is None:
            file_path = self.current_file_path
        
        if file_path:
            self.doc.save(file_path)
    
    def save_pdf_as(self, file_path):
        if not self.doc:
            return
        
        self.doc.save(file_path)
        self.current_file_path = file_path
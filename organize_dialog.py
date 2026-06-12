# organize_dialog.py
import fitz
from PySide6.QtWidgets import QDialog, QListWidget, QListWidgetItem, QMenu, QPushButton, QVBoxLayout, QHBoxLayout, QAbstractItemView
from PySide6.QtGui import QPixmap, QImage, QIcon
from PySide6.QtCore import Qt, QSize

class OrganizeDialog(QDialog):
    def __init__(self, doc, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Organize Pages")
        self.resize(800, 600)
        self.doc = doc
        self.page_order = list(range(len(doc)))

        self.list_widget = QListWidget()
        self.list_widget.setIconSize(QSize(80, 100))
        self.list_widget.setSpacing(5)
        self.list_widget.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.list_widget.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)
        self.list_widget.setDefaultDropAction(Qt.DropAction.MoveAction)
        self.list_widget.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.list_widget.customContextMenuRequested.connect(self.show_context_menu)
        self.load_thumbnails()
        
        # button
        self.buttonCancel = QPushButton("Cancel")
        self.buttonApply = QPushButton("Apply")
        self.buttonCancel.clicked.connect(self.reject)
        self.buttonApply.clicked.connect(self.accept)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.buttonCancel)
        button_layout.addWidget(self.buttonApply)

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.list_widget)
        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)
    
    def load_thumbnails(self):
        for i in range(len(self.doc)):
            item = QListWidgetItem(QIcon(self.load_thumbnail(i)), f"Page {i+1}")
            item.setData(Qt.ItemDataRole.UserRole, i)  # Store original page index
            self.list_widget.addItem(item)
    
    def load_thumbnail(self, page_num):
        page = self.doc[page_num]
        mat = fitz.Matrix(0.2, 0.2)
        pix = page.get_pixmap(matrix=mat)
        img = QImage(pix.samples, pix.width, pix.height, pix.stride, QImage.Format.Format_RGB888)
        return QPixmap.fromImage(img)
    
    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Delete:
            for item in self.list_widget.selectedItems():
                self.list_widget.takeItem(self.list_widget.row(item))
    
    def get_new_order(self):
        new_order = []
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            original_index = item.data(Qt.ItemDataRole.UserRole)
            new_order.append(original_index)
        return new_order
    
    def show_context_menu(self, pos):
        item = self.list_widget.itemAt(pos)
        if not item:
            return
        
        page_num = item.data(Qt.ItemDataRole.UserRole)
        
        menu = QMenu()
        rotRightAction = menu.addAction("Rotate Right")
        rotLeftAction = menu.addAction("Rotate Left")
        menu.addSeparator()
        deleteAction = menu.addAction("Delete page")
        action = menu.exec(self.list_widget.mapToGlobal(pos))
        
        if action == rotRightAction:
            self.doc[page_num].set_rotation((self.doc[page_num].rotation + 90) % 360)
            item.setIcon(QIcon(self.load_thumbnail(page_num)))
        elif action == rotLeftAction:
            self.doc[page_num].set_rotation((self.doc[page_num].rotation - 90) % 360)
            item.setIcon(QIcon(self.load_thumbnail(page_num)))
        elif action == deleteAction:
            self.delete_page(page_num)
    
    def rotate_page(self, page_num, angle):
        self.doc[page_num].set_rotation((self.doc[page_num].rotation + angle) % 360)
        item = self.list_widget.findItems(f"Page {page_num+1}", Qt.MatchFlag.MatchExactly)[0]
        item.setIcon(QIcon(self.load_thumbnail(page_num)))
    
    def delete_page(self, page_num):
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            if item.data(Qt.ItemDataRole.UserRole) == page_num:
                self.list_widget.takeItem(i)
                break
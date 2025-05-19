from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QListWidget, 
                            QLabel, QPushButton, QGroupBox, QListWidgetItem,
                            QFrame, QScrollArea, QSizePolicy)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont, QPalette, QColor
from mutagen.easyid3 import EasyID3
import os

class SmoothScrollArea(QScrollArea):
    def wheelEvent(self, event):
        # Reduce scroll speed for smoother experience
        num_degrees = event.angleDelta().y() / 8
        num_steps = num_degrees / 15
        self.verticalScrollBar().setValue(self.verticalScrollBar().value() - int(num_steps * 10))

class AlbumView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.mp3_files = []
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Header
        header = QWidget()
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)
        
        title = QLabel("Album View")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #333; margin-top: 18px;")
        header_layout.addWidget(title)
        
        # Accept button
        accept_btn = QPushButton("Save Track Order")
        accept_btn.setMinimumWidth(150)
        accept_btn.setStyleSheet("margin-right: 18px; margin-top: 6px; margin-bottom: 6px;")
        accept_btn.clicked.connect(self.accept_track_order)
        header_layout.addWidget(accept_btn, alignment=Qt.AlignmentFlag.AlignRight)
        
        layout.addWidget(header)
        
        # Add instructional description
        description = QLabel("Drag and drop tracks within each album to reorder them. Click 'Save Track Order' to update track numbers in the files.")
        description.setWordWrap(True)
        description.setStyleSheet("color: #444; font-size: 14px; background: #f8f9fa; border: 1px solid #e0e0e0; border-radius: 4px; padding: 8px 12px; margin-bottom: 8px;")
        layout.addWidget(description)
        
        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setStyleSheet("background-color: #ddd;")
        layout.addWidget(separator)
        
        # Album list in a scroll area
        scroll_area = SmoothScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:vertical {
                border: none;
                background: #f0f2f5;
                width: 10px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: #c1c1c1;
                min-height: 20px;
                border-radius: 5px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)
        
        self.album_list = QListWidget()
        self.album_list.setDragDropMode(QListWidget.DragDropMode.InternalMove)
        self.album_list.setStyleSheet("""
            QListWidget {
                background-color: transparent;
                border: none;
            }
            QListWidget::item {
                background-color: white;
                border-radius: 8px;
                margin: 8px;
                padding: 8px;
            }
            QListWidget::item:selected {
                background-color: #e8f0fe;
            }
        """)
        
        scroll_area.setWidget(self.album_list)
        layout.addWidget(scroll_area)
    
    def load_albums(self, mp3_files):
        self.mp3_files = mp3_files
        self.album_list.clear()
        
        # Group files by album
        albums = {}
        for mp3_file in mp3_files:
            album = mp3_file.metadata.get('album', 'Unknown Album')
            if album not in albums:
                albums[album] = []
            albums[album].append(mp3_file)
        
        # Create album groups
        for album_name, files in albums.items():
            # Create a widget to hold the album group
            album_widget = QWidget()
            album_layout = QVBoxLayout(album_widget)
            album_layout.setSpacing(8)
            album_layout.setContentsMargins(16, 30, 16, 30)
            album_widget.setStyleSheet('''
                background: #fff;
                border: 1.5px solid #d0d7e2;
                border-radius: 10px;
                margin-bottom: 18px;
            ''')
            
            # Add album name label
            album_label = QLabel(album_name)
            album_label.setMinimumHeight(75)
            album_label.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
            album_label.setStyleSheet("""
                font-weight: bold;
                font-size: 20px;
                color: #111;
                padding: 5px 0px 5px 0px;
                border-bottom: 1px solid #eee;
            """)
            album_layout.addWidget(album_label)
            
            # Add track labels directly to the album layout
            for file in files:
                title = file.metadata.get('title', os.path.basename(file.path))
                if not title:
                    title = "(No Title)" # Keep placeholder for debugging if needed
                track_label = QLabel(title)
                track_label.setMinimumHeight(60)
                track_label.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
                track_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.MinimumExpanding)
                track_label.setStyleSheet("color: #000; font-size: 15px; padding: 10px 12px;")
                album_layout.addWidget(track_label)
            
            # Calculate total height needed for the album widget content
            content_height = album_label.sizeHint().height()
            content_height += album_layout.spacing() * (len(files) > 0)
            for track_label in album_widget.findChildren(QLabel):
                 # Exclude the album_label itself from this loop's height calculation
                if track_label is not album_label:
                     content_height += track_label.sizeHint().height() + album_layout.spacing()

            # Add margins from the album_layout
            total_widget_height = content_height + album_layout.contentsMargins().top() + album_layout.contentsMargins().bottom()

            # Create list item and set the widget
            item = QListWidgetItem()
            item.setSizeHint(QSize(album_widget.sizeHint().width(), total_widget_height))
            self.album_list.addItem(item)
            self.album_list.setItemWidget(item, album_widget)
    
    def accept_track_order(self):
        for i in range(self.album_list.count()):
            album_widget = self.album_list.itemWidget(self.album_list.item(i))
            track_list = album_widget.findChild(QListWidget)
            
            for j in range(track_list.count()):
                track_name = track_list.item(j).text()
                # Find the corresponding MP3 file
                for mp3_file in self.mp3_files:
                    if mp3_file.metadata.get('title', os.path.basename(mp3_file.path)) == track_name:
                        try:
                            audio = EasyID3(mp3_file.path)
                            audio['tracknumber'] = str(j + 1)
                            audio.save()
                        except Exception as e:
                            print(f"Error saving track number for {mp3_file.path}: {str(e)}") 
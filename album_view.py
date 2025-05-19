from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QListWidget, 
                            QLabel, QPushButton, QGroupBox, QListWidgetItem)
from PyQt6.QtCore import Qt
from mutagen.easyid3 import EasyID3
import os

class AlbumView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.mp3_files = []
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Album list
        self.album_list = QListWidget()
        self.album_list.setDragDropMode(QListWidget.DragDropMode.InternalMove)
        layout.addWidget(QLabel("Albums:"))
        layout.addWidget(self.album_list)
        
        # Accept button
        accept_btn = QPushButton("Accept Track Order")
        accept_btn.clicked.connect(self.accept_track_order)
        layout.addWidget(accept_btn)
    
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
            
            # Add album name label
            album_label = QLabel(album_name)
            album_label.setStyleSheet("font-weight: bold; font-size: 14px;")
            album_layout.addWidget(album_label)
            
            # Create list widget for tracks
            track_list = QListWidget()
            track_list.setDragDropMode(QListWidget.DragDropMode.InternalMove)
            
            for file in files:
                title = file.metadata.get('title', os.path.basename(file.path))
                item = QListWidgetItem(title)
                font = item.font()
                font.setPointSize(14)  # Keep larger font size
                item.setFont(font)
                track_list.addItem(item)
            
            # Resize track_list to fit all items (no scroll bar for typical album sizes)
            row_height = track_list.sizeHintForRow(0) if track_list.count() > 0 else 24
            total_height = row_height * track_list.count() + 6  # 6 for padding/border
            track_list.setFixedHeight(total_height)
            
            album_layout.addWidget(track_list)
            
            # Create list item and set the widget
            item = QListWidgetItem()
            item.setSizeHint(album_widget.sizeHint())
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
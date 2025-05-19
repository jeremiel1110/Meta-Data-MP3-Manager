import sys
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QPushButton, QFileDialog, QListWidget, 
                            QLabel, QLineEdit, QGroupBox, QCheckBox, QTabWidget,
                            QListWidgetItem)
from PyQt6.QtCore import Qt
from mutagen.easyid3 import EasyID3
from album_view import AlbumView

class MP3File:
    def __init__(self, path):
        self.path = path
        self.active = True
        self.metadata = self.load_metadata()
    
    def load_metadata(self):
        try:
            audio = EasyID3(self.path)
            return {
                'artist': audio.get('artist', [''])[0],
                'album': audio.get('album', [''])[0],
                'year': audio.get('date', [''])[0],
                'genre': audio.get('genre', [''])[0],
                'title': audio.get('title', [''])[0]
            }
        except:
            return {
                'artist': '',
                'album': '',
                'year': '',
                'genre': '',
                'title': os.path.basename(self.path)
            }

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Meta Data MP3 Manager")
        self.setMinimumSize(1000, 700)
        
        self.mp3_files = []
        self.setup_ui()
    
    def setup_ui(self):
        # Main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        
        # Folder selection
        folder_btn = QPushButton("Select Folder")
        folder_btn.clicked.connect(self.select_folder)
        layout.addWidget(folder_btn)
        
        # Tab widget
        tab_widget = QTabWidget()
        
        # File list tab
        file_list_tab = QWidget()
        file_list_layout = QHBoxLayout(file_list_tab)
        
        # Left panel for file list
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        # File list
        self.file_list = QListWidget()
        self.file_list.setAcceptDrops(True)
        self.file_list.dragEnterEvent = self.dragEnterEvent
        self.file_list.dropEvent = self.dropEvent
        left_layout.addWidget(QLabel("MP3 Files:"))
        left_layout.addWidget(self.file_list)
        
        # Right panel for metadata editing
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        # Metadata group
        metadata_group = QGroupBox("Edit Metadata")
        metadata_layout = QVBoxLayout(metadata_group)
        
        # Artist
        artist_layout = QHBoxLayout()
        artist_layout.addWidget(QLabel("Artist:"))
        self.artist_input = QLineEdit()
        artist_layout.addWidget(self.artist_input)
        metadata_layout.addLayout(artist_layout)
        
        # Album
        album_layout = QHBoxLayout()
        album_layout.addWidget(QLabel("Album:"))
        self.album_input = QLineEdit()
        album_layout.addWidget(self.album_input)
        metadata_layout.addLayout(album_layout)
        
        # Year
        year_layout = QHBoxLayout()
        year_layout.addWidget(QLabel("Year:"))
        self.year_input = QLineEdit()
        year_layout.addWidget(self.year_input)
        metadata_layout.addLayout(year_layout)
        
        # Genre
        genre_layout = QHBoxLayout()
        genre_layout.addWidget(QLabel("Genre:"))
        self.genre_input = QLineEdit()
        genre_layout.addWidget(self.genre_input)
        metadata_layout.addLayout(genre_layout)
        
        # Apply button
        apply_btn = QPushButton("Apply Changes")
        apply_btn.clicked.connect(self.apply_changes)
        metadata_layout.addWidget(apply_btn)
        
        right_layout.addWidget(metadata_group)
        right_layout.addStretch()
        
        # Add panels to file list tab
        file_list_layout.addWidget(left_panel, 1)
        file_list_layout.addWidget(right_panel, 1)
        
        # Album view tab
        self.album_view = AlbumView()
        
        # Add tabs
        tab_widget.addTab(file_list_tab, "File List")
        tab_widget.addTab(self.album_view, "Album View")
        
        layout.addWidget(tab_widget)
    
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()
    
    def dropEvent(self, event):
        files = [url.toLocalFile() for url in event.mimeData().urls()]
        for file_path in files:
            if file_path.lower().endswith('.mp3'):
                self.add_mp3_file(file_path)
    
    def add_mp3_file(self, file_path):
        mp3_file = MP3File(file_path)
        self.mp3_files.append(mp3_file)
        
        # Create list item with checkbox
        item = QListWidgetItem()
        checkbox = QCheckBox(os.path.basename(file_path))
        checkbox.setChecked(True)
        self.file_list.addItem(item)
        self.file_list.setItemWidget(item, checkbox)
        
        # Update album view
        self.album_view.load_albums(self.mp3_files)
    
    def select_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select MP3 Folder")
        if folder:
            self.load_mp3_files(folder)
    
    def load_mp3_files(self, folder):
        self.mp3_files = []
        self.file_list.clear()
        
        for file in os.listdir(folder):
            if file.lower().endswith('.mp3'):
                file_path = os.path.join(folder, file)
                self.add_mp3_file(file_path)
    
    def apply_changes(self):
        for i in range(self.file_list.count()):
            item = self.file_list.item(i)
            checkbox = self.file_list.itemWidget(item)
            
            if checkbox.isChecked():
                mp3_file = self.mp3_files[i]
                try:
                    audio = EasyID3(mp3_file.path)
                    
                    # Only update fields that have values
                    if self.artist_input.text().strip():
                        audio['artist'] = self.artist_input.text()
                    if self.album_input.text().strip():
                        audio['album'] = self.album_input.text()
                    if self.year_input.text().strip():
                        audio['date'] = self.year_input.text()
                    if self.genre_input.text().strip():
                        audio['genre'] = self.genre_input.text()
                    
                    audio.save()
                except Exception as e:
                    print(f"Error saving {mp3_file.path}: {str(e)}")
        
        # Refresh album view after changes
        self.album_view.load_albums(self.mp3_files)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec()) 
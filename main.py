import sys
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QPushButton, QFileDialog, QListWidget, 
                            QLabel, QLineEdit, QGroupBox, QCheckBox, QTabWidget,
                            QListWidgetItem, QFrame, QMessageBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPalette, QColor, QFont
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
        self.setMinimumSize(1200, 800)
        
        # Set application style
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f0f2f5;
            }
            QPushButton {
                background-color: #4a90e2;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #357abd;
            }
            QPushButton:pressed {
                background-color: #2d6da3;
            }
            QLineEdit {
                padding: 8px;
                border: 1px solid #ddd;
                border-radius: 4px;
                background-color: white;
            }
            QLineEdit:focus {
                border: 1px solid #4a90e2;
            }
            QGroupBox {
                background-color: white;
                border-radius: 8px;
                padding: 16px;
                margin-top: 16px;
            }
            QGroupBox::title {
                color: #222;
                font-weight: bold;
                font-size: 18px;
            }
            QListWidget {
                background-color: white;
                border: 1px solid #bbb;
                border-radius: 4px;
                padding: 4px;
            }
            QListWidget::item {
                padding: 12px 8px;
                border-bottom: 1px solid #eee;
                font-size: 16px;
                background: #f7faff;
                color: #000;
            }
            QListWidget::item:selected {
                background-color: #e8f0fe;
                color: #222;
            }
            QTabWidget::pane {
                border: 1px solid #bbb;
                border-radius: 4px;
                background-color: #f8f9fa;
            }
            QTabBar::tab {
                background-color: #e6e9ef;
                color: #222;
                padding: 10px 20px;
                margin-right: 2px;
                border: 1px solid #bbb;
                border-bottom: none;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                font-size: 16px;
                font-weight: bold;
            }
            QTabBar::tab:selected {
                background-color: #fff;
                color: #111;
                border-bottom: 1px solid #fff;
            }
            QLabel {
                color: #222;
            }
            QCheckBox {
                spacing: 8px;
                font-size: 16px;
                font-weight: 500;
            }
            QCheckBox::indicator {
                width: 20px;
                height: 20px;
                background-color: #a0a0a0; /* Default grey background for all states */
                border-radius: 4px; /* Add some rounding */
            }
            QCheckBox::indicator:checked {
                background-color: #4a90e2; /* Blue background when checked */
                image: url(./icons/check.png); /* Display the check icon */
            }
        """)
        
        self.mp3_files = []
        self.setup_ui()
    
    def setup_ui(self):
        # Main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        layout.setSpacing(16)
        layout.setContentsMargins(16, 16, 16, 16)
        
        # Header
        header = QWidget()
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)
        
        title = QLabel("Meta Data MP3 Manager")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #333;")
        header_layout.addWidget(title)
        
        # Spacer to push button to the right
        header_layout.addStretch(1)
        
        # Folder selection button with icon
        self.folder_btn = QPushButton("Select Folder")
        self.folder_btn.setMinimumWidth(150)
        self.folder_btn.setStyleSheet("margin-right: 18px; margin-top: 6px; margin-bottom: 6px;")
        self.folder_btn.clicked.connect(self.select_folder)
        header_layout.addWidget(self.folder_btn, alignment=Qt.AlignmentFlag.AlignRight)
        
        layout.addWidget(header)
        
        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setStyleSheet("background-color: #ddd;")
        layout.addWidget(separator)
        
        # Tab widget
        tab_widget = QTabWidget()
        
        # File list tab
        file_list_tab = QWidget()
        file_list_layout = QHBoxLayout(file_list_tab)
        file_list_layout.setSpacing(16)
        
        # Left panel for file list
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)
        
        # File list header
        file_list_header = QWidget()
        file_list_header_layout = QHBoxLayout(file_list_header)
        file_list_header_layout.setContentsMargins(0, 0, 0, 8)
        
        file_list_label = QLabel("MP3 Files")
        file_list_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #222; background: #e6e9ef; padding: 6px 12px; border-radius: 4px;")
        file_list_header_layout.addWidget(file_list_label)
        
        left_layout.addWidget(file_list_header)
        
        # Drag-and-drop zone
        self.drop_zone = QLabel("Drop MP3 files here or use the Select Folder button.")
        self.drop_zone.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.drop_zone.setStyleSheet('''
            QLabel {
                border: 2px dashed #4a90e2;
                background: #eaf3fb;
                color: #357abd;
                font-size: 16px;
                padding: 24px 0;
                border-radius: 8px;
                margin-bottom: 12px;
            }
        ''')
        self.drop_zone.setAcceptDrops(True)
        left_layout.addWidget(self.drop_zone)
        
        # File list
        self.file_list = QListWidget()
        self.file_list.setAcceptDrops(True)
        self.file_list.dragEnterEvent = self.dragEnterEvent
        self.file_list.dropEvent = self.dropEvent
        left_layout.addWidget(self.file_list)
        
        # Right panel for metadata editing
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)
        
        # Metadata group
        metadata_group = QGroupBox("Edit Metadata")
        metadata_layout = QVBoxLayout(metadata_group)
        metadata_layout.setSpacing(12)
        
        # Artist
        artist_layout = QHBoxLayout()
        artist_label = QLabel("Artist:")
        artist_label.setMinimumWidth(80)
        artist_layout.addWidget(artist_label)
        self.artist_input = QLineEdit()
        artist_layout.addWidget(self.artist_input)
        metadata_layout.addLayout(artist_layout)
        
        # Album
        album_layout = QHBoxLayout()
        album_label = QLabel("Album:")
        album_label.setMinimumWidth(80)
        album_layout.addWidget(album_label)
        self.album_input = QLineEdit()
        album_layout.addWidget(self.album_input)
        metadata_layout.addLayout(album_layout)
        
        # Year
        year_layout = QHBoxLayout()
        year_label = QLabel("Year:")
        year_label.setMinimumWidth(80)
        year_layout.addWidget(year_label)
        self.year_input = QLineEdit()
        year_layout.addWidget(self.year_input)
        metadata_layout.addLayout(year_layout)
        
        # Genre
        genre_layout = QHBoxLayout()
        genre_label = QLabel("Genre:")
        genre_label.setMinimumWidth(80)
        genre_layout.addWidget(genre_label)
        self.genre_input = QLineEdit()
        genre_layout.addWidget(self.genre_input)
        metadata_layout.addLayout(genre_layout)
        
        # Apply button
        apply_btn = QPushButton("Apply Changes")
        apply_btn.setMinimumHeight(40)
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
            # Highlight drop zone if dragging over
            if hasattr(self, 'drop_zone'):
                self.drop_zone.setStyleSheet('''
                    QLabel {
                        border: 2px solid #357abd;
                        background: #d0e7fa;
                        color: #357abd;
                        font-size: 16px;
                        padding: 24px 0;
                        border-radius: 8px;
                        margin-bottom: 12px;
                    }
                ''')
        else:
            event.ignore()
    
    def dragLeaveEvent(self, event):
        # Remove highlight from drop zone
        if hasattr(self, 'drop_zone'):
            self.drop_zone.setStyleSheet('''
                QLabel {
                    border: 2px dashed #4a90e2;
                    background: #eaf3fb;
                    color: #357abd;
                    font-size: 16px;
                    padding: 24px 0;
                    border-radius: 8px;
                    margin-bottom: 12px;
                }
            ''')
        event.accept()
    
    def dropEvent(self, event):
        files = [url.toLocalFile() for url in event.mimeData().urls()]
        for file_path in files:
            if file_path.lower().endswith('.mp3'):
                self.add_mp3_file(file_path)
        # Remove highlight from drop zone
        if hasattr(self, 'drop_zone'):
            self.drop_zone.setStyleSheet('''
                QLabel {
                    border: 2px dashed #4a90e2;
                    background: #eaf3fb;
                    color: #357abd;
                    font-size: 16px;
                    padding: 24px 0;
                    border-radius: 8px;
                    margin-bottom: 12px;
                }
            ''')
    
    def add_mp3_file(self, file_path):
        # Check for duplicates before adding
        for existing_file in self.mp3_files:
            if existing_file.path == file_path:
                msg_box = QMessageBox(self) # Create a QMessageBox instance
                msg_box.setIcon(QMessageBox.Icon.Warning)
                msg_box.setWindowTitle("Duplicate File")
                msg_box.setText(f"File with path:\n{file_path}\nis already loaded.")
                # Apply stylesheet for white mode
                msg_box.setStyleSheet("QMessageBox { background-color: white; color: black; } QLabel { color: black; } QPushButton { background-color: #4a90e2; color: white; border: none; padding: 5px 10px; border-radius: 3px; }")
                msg_box.exec() # Use exec() to show the dialog
                return # Stop adding the file if it's a duplicate
                
        mp3_file = MP3File(file_path)
        self.mp3_files.append(mp3_file)
        
        # Create list item with checkbox
        item = QListWidgetItem()
        checkbox = QCheckBox(os.path.basename(file_path))
        checkbox.setChecked(True)
        checkbox.setStyleSheet('color: #000; font-size: 16px; font-weight: 500;')
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
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QListWidget, 
                            QLabel, QPushButton, QGroupBox, QListWidgetItem,
                            QFrame, QScrollArea, QSizePolicy)
from PyQt6.QtCore import Qt, QSize, QMimeData, QPoint
from PyQt6.QtGui import QFont, QPalette, QColor, QDrag, QPixmap
from mutagen.easyid3 import EasyID3
import os

class SmoothScrollArea(QScrollArea):
    def wheelEvent(self, event):
        # Make scrolling fluid based on estimated track height

        # Estimate track height including padding, margin, and layout spacing
        # MinHeight (60) + VertPadding (10+10) + MarginBottom (2) + LayoutSpacing (10) = 92
        estimated_track_height = 92

        # Get degrees of wheel rotation (standard is 15 degrees per detent)
        degrees = event.angleDelta().y() / 8.0

        # Calculate scroll amount to approximate scrolling by track height
        # Assuming one detent (15 degrees) should scroll by roughly one track height
        # Pixels per degree = estimated_track_height / degrees_per_detent = 92 / 15 ≈ 6.13
        pixels_per_degree = estimated_track_height / 15.0 # Use float division

        scroll_amount = int(degrees * pixels_per_degree)

        self.verticalScrollBar().setValue(self.verticalScrollBar().value() - scroll_amount)

class DraggableTrackLabel(QLabel):
    def __init__(self, title, mp3_file_path, parent=None):
        super().__init__(title, parent)
        self.mp3_file_path = mp3_file_path # Store the file path
        self.setMinimumHeight(60)
        self.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.MinimumExpanding)
        self.setStyleSheet("color: #000; font-size: 15px; padding: 10px 12px; background-color: #f0f0f0; margin-bottom: 2px; border-radius: 4px;") # Added background for visibility and margin

    def mouseMoveEvent(self, e):
        if e.buttons() == Qt.MouseButton.LeftButton:
            drag = QDrag(self)
            mime = QMimeData()
            mime.setText(self.mp3_file_path) # Store the file path in mime data
            drag.setMimeData(mime)

            pixmap = QPixmap(self.size())
            self.render(pixmap)
            drag.setPixmap(pixmap)

            drag.exec(Qt.DropAction.MoveAction)

class AlbumContainerWidget(QWidget):
    def __init__(self, album_name, files, parent=None):
        super().__init__(parent)
        self.album_name = album_name
        self.files = files
        self.setAcceptDrops(True)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(10) # Increased spacing between tracks
        layout.setContentsMargins(20, 30, 20, 20) # Increased padding within the box
        self.setStyleSheet('''
            AlbumContainerWidget {
                background: #ffffff; /* White background */
                border: 1px solid #d0d0d0; /* Slightly more prominent border */
                border-radius: 10px; /* Slightly more rounded corners */
                margin-bottom: 20px; /* More space between album boxes */
                /* box-shadow: 2px 2px 5px rgba(0, 0, 0, 0.1); /* Subtle shadow */ */
            }
            /* Styles for QLabel:first-child removed to apply directly */
        ''')

        album_label = QLabel(self.album_name)
        album_label.setMinimumHeight(75)
        album_label.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
        # Apply styles directly to the album_label
        album_label.setStyleSheet("""
            font-weight: bold;
            font-size: 32px; /* Further increased font size */
            color: #000000; /* Black text for maximum prominence */
            padding: 0px 0px 15px 0px; /* Adjusted padding */
            border-bottom: 1px solid #cccccc; /* Slightly darker separator */
            margin-bottom: 15px; /* More space below album name */
        """)
        layout.addWidget(album_label)

        for file in self.files:
            # Use the filename for the track label text
            title = os.path.basename(file.path)
            # if not title:
            #     title = "(No Title)"
            track_label = DraggableTrackLabel(title, file.path) # Pass file path
            layout.addWidget(track_label)

    def dragEnterEvent(self, event):
        if event.mimeData().hasText():
            event.acceptProposedAction()

    def dragMoveEvent(self, event):
        if event.mimeData().hasText():
            event.acceptProposedAction()

    def dropEvent(self, event):
        if event.mimeData().hasText():
            # dropped_file_path = event.mimeData().text() # Not used in drop logic, retrieved from source_widget later
            source_widget = event.source()

            # Ensure the source of the drop is a DraggableTrackLabel from this album
            if not isinstance(source_widget, DraggableTrackLabel) or source_widget.parent() != self:
                event.ignore()
                return

            drop_pos_in_container = event.position().toPoint() # Corrected method
            target_index = -1

            # Find the position to insert the dropped widget
            for i in range(self.layout().count()):
                widget = self.layout().itemAt(i).widget()
                # Only consider track labels for drop position calculation
                if isinstance(widget, DraggableTrackLabel):
                    widget_geometry = widget.geometry()
                    # Check if the drop position is above the vertical midpoint of the widget
                    if drop_pos_in_container.y() < widget_geometry.center().y():
                        target_index = i
                        break

            # If target_index is still -1, it means drop at the end
            if target_index == -1:
                 target_index = self.layout().count()

            # Remove the source widget from its original position
            # Need to find the source widget in the current layout first
            source_index = -1
            for i in range(self.layout().count()):
                widget = self.layout().itemAt(i).widget()
                if widget == source_widget:
                    source_index = i
                    break

            if source_index != -1:
                # Remove the widget from the layout without deleting it
                self.layout().takeAt(source_index)

                # Adjust target_index if dropping after the original position
                if target_index > source_index:
                    target_index -= 1

            # Insert the source widget at the target position
            self.layout().insertWidget(target_index, source_widget)

            event.acceptProposedAction()

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
            album_widget = AlbumContainerWidget(album_name, files)
            
            # Calculate total height needed for the album widget content
            content_height = album_widget.sizeHint().height()

            # Create list item and set the widget
            item = QListWidgetItem()
            item.setSizeHint(QSize(album_widget.sizeHint().width(), content_height))
            self.album_list.addItem(item)
            self.album_list.setItemWidget(item, album_widget)
    
    def get_album_track_order(self):
        album_track_orders = {}
        for i in range(self.album_list.count()):
            item = self.album_list.item(i)
            album_widget = self.album_list.itemWidget(item)
            if isinstance(album_widget, AlbumContainerWidget):
                album_name = album_widget.album_name
                track_order = []
                # Iterate through the layout of the AlbumContainerWidget
                for j in range(album_widget.layout().count()):
                    widget = album_widget.layout().itemAt(j).widget()
                    # Check if the widget is a DraggableTrackLabel and not the album_label
                    if isinstance(widget, DraggableTrackLabel):
                         track_order.append(widget.mp3_file_path)
                album_track_orders[album_name] = track_order
        return album_track_orders

    def accept_track_order(self):
        album_track_orders = self.get_album_track_order()

        for album_name, track_list in album_track_orders.items():
            for index, file_path in enumerate(track_list):
                try:
                    audio = EasyID3(file_path)
                    audio['tracknumber'] = str(index + 1)
                    audio.save()
                except Exception as e:
                    print(f"Error saving track number for {file_path}: {str(e)}") 
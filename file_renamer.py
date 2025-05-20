from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QListWidget, QAbstractItemView, QMessageBox, QListWidgetItem, QCheckBox)
from PyQt6.QtCore import Qt, QSize
import os
from PyQt6.QtGui import QPalette

class FileRenamer(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.mp3_files = []
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Apply stylesheet for consistent appearance, including black text for list items and checkbox styles
        self.setStyleSheet("""
            QListWidget::item {
                color: black; /* Ensure list item text color is black */
            }
            QLineEdit {
                color: black; /* Ensure pattern input text color is black */
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
        
        # Instructions
        instruction_label = QLabel("Enter the renaming pattern using metadata tags (e.g., artist - album - track - title).")
        instruction_label.setWordWrap(True)
        layout.addWidget(instruction_label)
        
        # Pattern input
        pattern_layout = QHBoxLayout()
        pattern_label = QLabel("Pattern:")
        pattern_layout.addWidget(pattern_label)
        self.pattern_input = QLineEdit("title - artist") # Default pattern changed
        
        # Remove palette setting as stylesheet should be sufficient and palette caused errors
        # palette = self.pattern_input.palette()
        # palette.setColor(QPalette.ColorRole.Text, Qt.GlobalColor.black)
        # self.pattern_input.setPalette(palette)
        
        pattern_layout.addWidget(self.pattern_input)
        layout.addLayout(pattern_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        self.preview_button = QPushButton("Preview Rename")
        self.preview_button.clicked.connect(self.preview_rename)
        button_layout.addWidget(self.preview_button)
        
        # Add Cancel button to the right of Preview
        self.cancel_button = QPushButton("Cancel Preview") # Changed text
        self.cancel_button.clicked.connect(self.cancel_rename)
        button_layout.addWidget(self.cancel_button)
        
        # Add some space between Cancel and Apply
        button_layout.addSpacing(20)

        self.apply_button = QPushButton("Apply Rename")
        self.apply_button.clicked.connect(self.apply_rename)
        self.apply_button.setEnabled(False) # Disable initially
        button_layout.addWidget(self.apply_button)
        
        button_layout.addStretch() # Push buttons to the left
        layout.addLayout(button_layout)
        
        # File list (for preview)
        self.file_list = QListWidget()
        self.file_list.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection) # Selection handled by checkboxes
        layout.addWidget(self.file_list)
        
    def load_files(self, mp3_files):
        self.mp3_files = mp3_files
        self.file_list.clear()
        self.apply_button.setEnabled(False) # Disable apply button when files are loaded/cleared
        
        # print(f"FileRenamer.load_files called with {len(mp3_files)} files.") # Debug print

        for i, mp3_file in enumerate(self.mp3_files):
            # Create the list item
            item = QListWidgetItem(self.file_list) # Pass list widget as parent
            item.setData(Qt.ItemDataRole.UserRole, i) # Store the index of the file
            
            # Create the checkbox
            checkbox = QCheckBox(os.path.basename(mp3_file.path))
            checkbox.setChecked(True) # Start with all files selected
            # Apply inline stylesheet for text color and font - indicator style comes from parent stylesheet
            checkbox.setStyleSheet('color: #000; font-size: 16px; font-weight: 500;')
            
            # Set the checkbox as the item widget
            self.file_list.setItemWidget(item, checkbox)

    def preview_rename(self):
        raw_pattern = self.pattern_input.text()
        # Automatically add curly braces around known tags
        pattern = raw_pattern.replace("artist", "{artist}").replace("album", "{album}").replace("year", "{year}").replace("genre", "{genre}").replace("title", "{title}").replace("track", "{tracknumber}")
        
        # --- Start: Get checked items before clearing ---
        files_to_preview_indices = []
        # print(f"Preview Rename: Getting checked items. List count: {self.file_list.count()}") # Debug print
        for i in range(self.file_list.count()):
            item = self.file_list.item(i)
            # Assuming the item widget is the checkbox itself
            checkbox = self.file_list.itemWidget(item)
            if checkbox and checkbox.isChecked():
                 files_to_preview_indices.append(item.data(Qt.ItemDataRole.UserRole))
        # --- End: Get checked items before clearing ---

        self.file_list.clear() # Clear and re-populate with previews
        preview_available = False
        
        # print(f"Preview Rename: Found {len(files_to_preview_indices)} files to preview.") # Debug print

        for i in files_to_preview_indices:
            mp3_file = self.mp3_files[i]
            original_name = os.path.basename(mp3_file.path)
            try:
                # Build the new filename based on the pattern and metadata
                new_name = pattern.format(
                    artist=mp3_file.metadata.get('artist', 'Unknown Artist'),
                    album=mp3_file.metadata.get('album', 'Unknown Album'),
                    year=mp3_file.metadata.get('year', 'Unknown Year'),
                    genre=mp3_file.metadata.get('genre', 'Unknown Genre'),
                    title=mp3_file.metadata.get('title', 'Unknown Title'),
                    tracknumber=mp3_file.metadata.get('tracknumber', '') # Include tracknumber in format
                ) + os.path.splitext(original_name)[1] # Keep original extension
                
                # Simple validation for invalid characters (platform dependent, but covers common issues)
                # Replace invalid characters with underscores, for example
                invalid_chars = '<|>|:|"|/|\\|\?|\*'
                for char in invalid_chars:
                     new_name = new_name.replace(char, '_')

                # Create the list item
                item = QListWidgetItem(self.file_list) # Pass list widget as parent
                item.setData(Qt.ItemDataRole.UserRole, i) # Store index in new item
                
                # Create the checkbox with preview text
                checkbox = QCheckBox(f"'{original_name}' -> '{new_name}'")
                checkbox.setChecked(True) # Keep the item checked in preview
                 # Apply inline stylesheet for text color and font
                checkbox.setStyleSheet('color: #000; font-size: 16px; font-weight: 500;')
                
                # Set the checkbox as the item widget
                self.file_list.setItemWidget(item, checkbox)
                # print(f"Preview Rename: Added item for {original_name}") # Debug print
                preview_available = True

            except Exception as e:
                # Create the list item
                item = QListWidgetItem(self.file_list) # Pass list widget as parent
                item.setData(Qt.ItemDataRole.UserRole, i) # Store index
                
                # Create the checkbox with error text
                checkbox = QCheckBox(f"Error processing {original_name}: {str(e)}")
                checkbox.setChecked(True) # Keep checked
                 # Apply inline stylesheet for text color and font
                checkbox.setStyleSheet('color: #000; font-size: 16px; font-weight: 500;')
                
                # Set the checkbox as the item widget
                self.file_list.setItemWidget(item, checkbox)
                # print(f"Preview Rename: Error adding item for {original_name}: {str(e)}") # Debug print

        # print(f"Preview Rename: Finished processing. Preview available: {preview_available}") # Debug print
        self.apply_button.setEnabled(preview_available)

    def apply_rename(self):
        renamed_count = 0
        
        # Get indices of checked items from the preview list
        files_to_rename_indices = []
        for i in range(self.file_list.count()):
            item = self.file_list.item(i)
            checkbox = self.file_list.itemWidget(item) # Get the checkbox widget directly
            if checkbox and checkbox.isChecked():
                 files_to_rename_indices.append(item.data(Qt.ItemDataRole.UserRole))

        for i in files_to_rename_indices:
            mp3_file = self.mp3_files[i]
            original_path = mp3_file.path
            original_name = os.path.basename(original_path)
            
            try:
                # Re-generate the new name to ensure consistency with preview
                raw_pattern = self.pattern_input.text()
                # Automatically add curly braces around known tags
                pattern = raw_pattern.replace("artist", "{artist}").replace("album", "{album}").replace("year", "{year}").replace("genre", "{genre}").replace("title", "{title}").replace("track", "{tracknumber}")
                
                new_name = pattern.format(
                    artist=mp3_file.metadata.get('artist', 'Unknown Artist'),
                    album=mp3_file.metadata.get('album', 'Unknown Album'),
                    year=mp3_file.metadata.get('year', 'Unknown Year'),
                    genre=mp3_file.metadata.get('genre', 'Unknown Genre'),
                    title=mp3_file.metadata.get('title', 'Unknown Title'),
                    tracknumber=mp3_file.metadata.get('tracknumber', '') # Include tracknumber in format
                ) + os.path.splitext(original_name)[1]
                
                invalid_chars = '<|>|:|"|/|\\|\?|\*'
                for char in invalid_chars:
                     new_name = new_name.replace(char, '_')

                new_path = os.path.join(os.path.dirname(original_path), new_name)
                
                if original_path != new_path:
                    os.rename(original_path, new_path)
                    mp3_file.path = new_path # Update the path in the MP3File object
                    renamed_count += 1
                    
            except Exception as e:
                # Optionally show a message box for critical errors
                # print(f"Error renaming {original_name} to {new_name}: {str(e)}") # Debug print
                pass # Suppress error print for now
                # Optionally show a message box for critical errors
                
        # Replace static QMessageBox.information with instance for styling
        msg_box = QMessageBox(self) # Create a QMessageBox instance
        msg_box.setIcon(QMessageBox.Icon.Information) # Set the information icon
        msg_box.setWindowTitle("Rename Complete")
        msg_box.setText(f"Successfully renamed {renamed_count} files.")
        # Apply stylesheet for white mode, matching the duplicate file warning
        msg_box.setStyleSheet("QMessageBox { background-color: white; color: black; } QLabel { color: black; } QPushButton { background-color: #4a90e2; color: white; border: none; padding: 5px 10px; border-radius: 3px; }")
        msg_box.exec() # Use exec() to show the styled dialog
        
        self.load_files(self.mp3_files) # Reload files to show updated names

    def cancel_rename(self):
        """Clears the current list and reloads the original files, preserving selection."""
        # Store the indices of currently checked files
        checked_indices = []
        for i in range(self.file_list.count()):
            item = self.file_list.item(i)
            # Assuming the item widget is the checkbox itself
            checkbox = self.file_list.itemWidget(item)
            if checkbox and checkbox.isChecked():
                 checked_indices.append(item.data(Qt.ItemDataRole.UserRole))

        self.file_list.clear() # Clear the current list display
        self.load_files(self.mp3_files) # Reload the original list (defaults to all checked)
        
        # Restore the selection state based on stored indices
        for i in range(self.file_list.count()):
            item = self.file_list.item(i)
            checkbox = self.file_list.itemWidget(item)
            file_index = item.data(Qt.ItemDataRole.UserRole)
            
            if checkbox and file_index not in checked_indices:
                 checkbox.setChecked(False) # Uncheck if it was not checked before cancel

# 🎵 Meta Data MP3 Manager

<div align="center">

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![PyQt6](https://img.shields.io/badge/PyQt6-6.0+-blue.svg)
![mutagen](https://img.shields.io/badge/mutagen-latest-orange.svg)

*A powerful desktop application for managing MP3 metadata with style and efficiency*

[Features](#-features) • [Installation](#-installation) • [Usage](#-how-it-works) • [Technologies](#-technologies) • [Contributing](#-contributing)

</div>

## ✨ Overview

**Meta Data MP3 Manager** is a lightweight desktop application that helps you efficiently organize and update the metadata of your MP3 files. Perfect for music enthusiasts and professionals who want to maintain a clean and organized music library.

## 🚀 Features

### 📁 Smart File Management
- **Folder-based Scanning**  
  Load all MP3 files from a selected folder and display them in a user-friendly interface.
- **Drag-and-Drop Support**  
  Easily add MP3 files by dragging them directly into the application window.

### 🎛️ Advanced Editing
- **Selective Editing**  
  Disable (ignore) specific tracks from editing with a simple toggle.
- **Batch Metadata Editing**  
  Edit the following metadata in bulk for all selected MP3 files:
  - 🎤 Artist (Interprète de l'album)
  - 💿 Album
  - 📅 Year
  - 🎶 Genre
  - _(Leave a field blank to preserve the original value in each file)_

### 🎧 Album Management
- **Album View & Track Ordering**  
  Group your tracks by album and visually organize them:
  - Drag & drop tracks to reorder them by album number
  - The album view automatically resizes to fit all tracks (no scroll bar for typical albums)
  - Track numbers are not shown for a cleaner look
  - Once satisfied, click **Accept** to save the track numbers to the metadata of each file

## 🧩 How It Works

1. **Launch the app** and select a folder containing your MP3 files, or drag MP3 files directly into the window
2. **Browse through the list** of found tracks. You can toggle off any track you don't want to include
3. **Edit metadata** in bulk using the edit panel. Leave fields blank to keep existing values
4. **Use the Album View** to fine-tune the track order of each album. The list will auto-size to fit all tracks
5. **Click Accept** to write all changes directly into the MP3 metadata

## 📥 Installation

1. **Install Python 3.8+** if you haven't already
2. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/meta-data-mp3-manager.git
   cd meta-data-mp3-manager
   ```
3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
4. **Run the application:**
   ```bash
   python main.py
   ```

## 🛠 Technologies

- **Python 3.8+** - Core programming language
- **[mutagen](https://mutagen.readthedocs.io/)** - MP3 tag editing library
- **[PyQt6](https://pypi.org/project/PyQt6/)** - Modern GUI framework
- **Other Dependencies** - See `requirements.txt` for full list

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📃 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

<div align="center">

> 🎧 Made with care for audiophiles who love clean libraries

[⬆ Back to top](#-meta-data-mp3-manager)

</div>

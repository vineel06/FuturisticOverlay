# 🚀 FuturisticOverlay

A real-time desktop performance monitoring overlay built using **Python**, **PyQt6**, and **NVIDIA NVML**.

This project was developed as both:

- 🎓 A personal student learning project  
- 💼 A professional portfolio project  

It demonstrates real-time system monitoring, GPU integration, UI engineering, and software packaging using Python.

---

## 🖥️ Features

- ✅ Real-time CPU usage monitoring
- ✅ Real-time GPU usage monitoring (NVIDIA NVML)
- ✅ GPU temperature monitoring
- ✅ GPU memory usage monitoring
- ✅ Active GPU process detection (e.g., GTA5.exe)
- ✅ FPS estimation
- ✅ Live CPU usage graph visualization
- ✅ Adjustable overlay opacity
- ✅ Frameless draggable UI
- ✅ System tray integration
- ✅ Export performance logs (CSV)
- ✅ Custom EXE build with icon and version metadata

---

## 🧠 Technologies Used

- Python 3.x
- PyQt6
- psutil
- nvidia-ml-py (NVIDIA NVML)
- WMI (optional CPU temperature)
- PyInstaller (for packaging)

---

## ⚙️ Installation (Run from Source)
Clone the repository:
```bash
git clone https://github.com/vineel06/FuturisticOverlay.git
cd FuturisticOverlay

Install dependencies:
pip install -r requirements.txt

Run the application:
python FuturisticOverlay.py
📦 Build Standalone EXE

To build a single executable file:
pyinstaller --noconfirm --onefile --windowed FuturisticOverlay.py --icon=icon.ico --version-file=version.txt --name FuturisticOverlay

The compiled executable will be located inside:
dist/FuturisticOverlay.exe

🧩 System Requirements
Windows 10 / Windows 11
NVIDIA GPU (required for GPU monitoring)
Python 3.9+
Optional: OpenHardwareMonitor (for CPU temperature monitoring)
If OpenHardwareMonitor is not running, CPU temperature will safely return 0 without crashing.

🎓 Learning Objectives
This project helped strengthen:
Desktop UI engineering using PyQt6
Real-time data visualization
Hardware API integration (NVML)
System performance monitoring concepts
Software packaging with PyInstaller
Clean modular architecture structuring
Exception-safe system programming

📈 Future Improvements
In-game DirectX overlay support
Cross-platform (Linux/macOS) support
Auto-update mechanism
Advanced theme customization
Professional installer packaging
Performance history logging system

📂 Project Structure
FuturisticOverlay/
│
├── FuturisticOverlay.py
├── icon.ico
├── version.txt
├── requirements.txt
├── README.md
├── .gitignore

👨‍💻 Author
Vineel
AI & ML Engineering 1st Year Student


Built as a hands-on systems programming and desktop application engineering project.

## 📸 Preview
![Overlay Screenshot](screenshot.png)

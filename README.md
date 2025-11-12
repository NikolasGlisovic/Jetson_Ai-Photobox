# AI PhotoBox - Jetson AGX Orin

An interactive photo booth with AI image processing, based on NVIDIA Jetson AGX Orin Development Kit.

## 🎯 Project Goal

Development of a standalone photo booth that:
- Captures photos with webcam
- Shows live preview during countdown
- Processes images artistically with AI (e.g. astronaut, superhero)
- Prints photos directly (Canon SELPHY CP1500)
- Works completely offline
- Provides images for download via local hotspot

## 🛠️ Hardware

- **Computer:** NVIDIA Jetson AGX Orin Development Kit
- **Camera:** USB Webcam (1920x1080)
- **Display:** Touchscreen for operation
- **Input:** Zero Delay Encoder (Arcade button)
- **Printer:** Canon SELPHY CP1500 (wired connection via USB)

## 📦 Tech Stack

### Backend
- **Python 3.10** with Flask
- **OpenCV** for camera control
- **Flask-SocketIO** for real-time hardware button events
- **CUPS** for printer integration
- **PyTorch** for AI inference (planned)
- Filesystem-based image storage (no database)

### Frontend
- **HTML/CSS/JavaScript** (Single Page Application)
- Runs in browser (Chromium Kiosk mode)
- Touch-optimized interface
- Real-time integration with physical button via WebSocket
- Socket.IO client (served locally for offline operation)

### Planned AI Integration
- Stable Diffusion XL/-turbo for image transformations
- Optimized for Jetson GPU (CUDA/TensorRT)

## 🚀 Current Status

### ✅ Implemented (Milestone 1 & 2)

**Core Functionality:**
- Flask web server with REST API (Port 5000)
- Webcam integration with live video preview
- Photo capture with 5-4-3-2-1 countdown animation
- Responsive web interface with gradient design
- Camera buffer optimization for fresh frames
- Cache-busting for correct image refresh
- Temporary image storage in `static/photos/`

**Hardware Integration:**
- ✅ Physical Zero Delay Encoder button fully integrated
- ✅ Real-time button events via WebSocket (Flask-SocketIO)
- ✅ Button triggers countdown and photo capture
- ✅ Works during all app states (can always restart capture)

**Printer Integration:**
- ✅ Canon SELPHY CP1500 printer support via CUPS
- ✅ One-click printing from web interface
- ✅ Automatic printer status check
- ✅ Print with optimized settings (4x6 photo, fit-to-page)
- ✅ Visual feedback for print jobs

**Photo Sharing:**
- ✅ Separate image share server (Port 8080)
- ✅ Auto-displays latest photo
- ✅ Download button for easy sharing
- ✅ Auto-refresh every 5 seconds
- ✅ Accessible via WiFi hotspot (e.g., http://10.42.0.1:8080)
- ✅ Responsive design for mobile devices

**Offline Operation:**
- ✅ Socket.IO served locally (no CDN dependency)
- ✅ Fully functional without internet connection
- ✅ All resources hosted on Jetson

### 🔄 In Progress

- **AI Image Processing:** Testing phase SDXL/SDXL-Turbo for Jetson
  - Implement SDXL/SDXL-Turbo in camera app for live image transformation

### 📋 Planned

- [ ] Stable Diffusion XL Image-to-Image pipeline integration
- [ ] Effect selection in frontend (Astronaut, Superhero, Vintage, etc.)
- [ ] Multiple effect options at random in backend
- [ ] Auto-cleanup of old photos (configurable time threshold)
- [ ] Kiosk mode auto-start script
- [ ] QR code generation for easy photo sharing access
- [ ] Photo gallery view
- [ ] Multi-language support

## 📁 Project Structure

```
nikolasglisovic-jetson_ai-photobox/
├── README.md
├── app.py                    # Main Flask server (Port 5000)
├── image_server.py           # Image sharing server (Port 8080)
├── camera.py                 # Camera control module
├── printer.py                # Printer integration module
├── static/
│   ├── js/
│   │   └── socket.io.min.js  # Socket.IO client (local)
│   └── photos/               # Captured photos storage
│       └── .gitkeep
└── templates/
    └── index.html            # Main web interface
```

## 🚦 Getting Started

### Prerequisites

```bash
# Install system dependencies
sudo apt-get update
sudo apt-get install python3-opencv cups

# Install Python packages
pip3 install flask flask-socketio opencv-python pillow inputs python-socketio eventlet
```

### Running the PhotoBox

```bash
# Start both servers
python3 app.py

# The app will automatically start:
# - Main PhotoBox UI on http://127.0.0.1:5000
# - Image sharing on http://127.0.0.1:8080 (or hotspot IP)
```

### Accessing the PhotoBox

**On the Jetson:**
- PhotoBox UI: http://127.0.0.1:5000
- Image sharing: http://127.0.0.1:8080

**From smartphone/tablet (via hotspot):**
- Image sharing: http://10.42.0.1:8080 (or your hotspot IP)

**REMOTE from smartphone/tablet (via hotspot):**
- Image sharing: http://10.42.0.1:5000 (or your hotspot IP)

### Setting up the Printer

```bash
# Add Canon SELPHY CP1500 to CUPS
# Make sure printer is connected via Hotspot and powered on

# Check if printer is detected
lpstat -p -d

# The printer should be named "Canon_SELPHY_CP1500"
```

### Hardware Button Setup

The Zero Delay Encoder is detected as a gamepad device. Ensure the `inputs` library can access it:

```bash
# Test button detection
python3 -c "from inputs import get_gamepad; print('Press button...'); get_gamepad()"

# If permission denied, add user to input group
sudo usermod -a -G input $USER
```

## 🎨 Features

### Main PhotoBox Interface (Port 5000)
- Live camera preview with video feed
- Big capture button with countdown animation
- Photo display with actions:
  - 🎨 AI processing (coming soon)
  - 🖨️ Print directly to Canon SELPHY
  - 🔄 Take new photo
- Physical arcade button integration
- Real-time status feedback

### Image Sharing Server (Port 8080)
- Automatically shows the latest captured photo
- Large, mobile-friendly interface
- One-click download button
- Auto-refresh every 5 seconds
- Perfect for guests to download their photos via hotspot

### REMOTE PhotoBox Interface (Port 5000)
- Connect your mobile device via hotspot
- go to http://10.42.0.1:5000 (or your hotspot IP)
- now you can controll the photobox with your remote device from your brwoser

## 🔧 Configuration

### Camera Settings
Edit `camera.py` to adjust:
- Resolution (default: 1920x1080, current:1280x720)
- JPEG quality (default: 95)
- Camera index (default: 0)

### Printer Settings
Edit `printer.py` to adjust:
- Printer name (default: Canon_SELPHY_CP1500)
- Paper size (default: photo-4x6)
- Print quality settings

### Server Ports
- Main app: Port 5000 (change in `app.py`)
- Image sharing: Port 8080 (change in `image_server.py`)

## 🐛 Troubleshooting

**Button not working:**
- Check if `inputs` library is installed
- Verify user is in `input` group
- Test with: `python3 -c "from inputs import get_gamepad; get_gamepad()"`

**Printer not found:**
- Ensure printer is powered on and connected via hotspot
- Verify CUPS is running: `systemctl status cups`

**Socket.IO not connecting:**
- Ensure `socket.io.min.js` exists in `static/js/`
- Check browser console for errors (F12)
- Verify Flask-SocketIO is installed

**Image sharing not accessible on phone:**
- Check hotspot IP with: `hostname -I`
- Use the displayed IP addresses from server startup
- Ensure phone is connected to Jetson's hotspot

## 🤝 Development

This project is in active development. Current focus is on integrating Stable Diffusion XL for creative image transformations.

## 👤 Author

Nikolas Glisovic

---

**Status:** Fully functional photo booth with camera, button, printer, and sharing capabilities. AI integration in progress.
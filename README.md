# AI PhotoBox - Jetson AGX Orin

An interactive photo booth with AI image processing, based on NVIDIA Jetson AGX Orin Development Kit.

## 🎯 Project Goal

Development of a standalone photo booth that:
- Captures photos with webcam
- Shows live preview during countdown
- Processes images artistically with AI (Stable Diffusion 1.5 + IP-Adapter)
- Adds automatic branding (Logo + QR-Code) to prints
- Prints photos directly (Canon SELPHY CP1500)
- Works completely offline
- Provides images for download via local hotspot
- Can be used as normal Photobooth if whished 

## 🛠️ Hardware

- **Computer:** NVIDIA Jetson AGX Orin Development Kit
- **Camera:** USB Webcam (1920x1080)
- **Display:** Touchscreen for operation
- **Input:** Zero Delay Encoder (Arcade button)
- **Printer:** Canon SELPHY CP1500 (wireless connection via Jetson Hotspot)
- **Storage:** External SSD for SD1.5 models and cache

## 📦 Tech Stack

### Backend
- **Python 3.10** with Flask
- **OpenCV** for camera control
- **Flask-SocketIO** for real-time hardware button events
- **CUPS** for printer integration
- **Stable Diffusion 1.5 + IP-Adapter** for AI image transformations
- **PIL/Pillow + CairoSVG** for image branding
- Filesystem-based image storage (no database)

### Frontend
- **HTML/CSS/JavaScript** (Single Page Application)
- Runs in browser (Chromium Kiosk mode)
- Touch-optimized interface
- Real-time integration with physical button via WebSocket
- Socket.IO client (served locally for offline operation)

### AI Integration
- **Stable Diffusion 1.5** with IP-Adapter-Full-Face for portrait transformations
- Random prompt selection from curated collection
- Runs in separate virtual environment on external SSD
- Face detection and cropping with OpenCV

## 🚀 Current Status

### ✅ Fully Implemented

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

**AI Image Processing:**
- ✅ Stable Diffusion 1.5 with IP-Adapter integration
- ✅ Random prompt selection from optimized collection
- ✅ Face detection and cropping for optimal results
- ✅ Separate virtual environment (no library conflicts)
- ✅ Process via subprocess call to external SD1.5 installation
- ✅ Input/Output handling with fixed filenames
- ✅ Generation time: ~30-60 seconds per image

**Printer Integration:**
- ✅ Canon SELPHY CP1500 printer support via CUPS
- ✅ Automatic branding with HS-Esslingen Logo (top-left)
- ✅ Automatic QR-Code placement (bottom-right)
- ✅ Image normalization to print size (1800x1200px @ 300 DPI)
- ✅ Letterbox handling for different aspect ratios (white borders)
- ✅ Logo and QR-Code with white background and rounded borders 
- ✅ One-click printing from web interface
- ✅ Automatic printer status check
- ✅ Print with optimized settings (fit-to-page)
- ✅ Visual feedback for print jobs
- ✅ Temporary print file cleanup

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
- ✅ AI models cached locally on external SSD

### 📋 Planned cherry on top Features

- [ ] Auto-start script
- [ ] Better file handling 
- [ ] Performance optimization (persistent AI model in memory)

## 📁 Project Structure

```
nikolasglisovic-jetson_ai-photobox/
├── README.md                   # This file
├── app.py                      # Main Flask server (Port 5000)
├── image_server.py             # Image sharing server (Port 8080)
├── camera.py                   # Camera control module
├── printer.py                  # Printer integration with branding
├── ai_processor.py             # AI processing bridge (subprocess handler)
├── image_branding.py           # Logo + QR-Code branding module
├── static/
│   ├── js/
│   │   └── socket.io.min.js    # Socket.IO client (local)
│   ├── branding/
│   │   ├── HS-Esslingen_Logo.svg    # University logo
│   │   └── HS-Esslingen_Code.png    # QR-Code for photo sharing
│   └── photos/                 # Captured photos storage
│       └── .gitkeep
└── templates/
    └── index.html              # Main web interface
```

**External SD1.5 Installation (on SSD):**
```
/media/user/SSD/sdxl-project/
├── venv/                       # Separate Python environment
├── generate_from_photobox.py   # SD1.5 processing script (can be found in static/examples)
├── prompts_optimized.py        # AI prompts collection (can be found in static/examples)
├── models/                     # SD1.5 models and weights
├── input_images/               # Input from PhotoBox
│   └── photobox_input.jpg      # Fixed filename (overwritten)
└── output_images/              # AI-processed output
    └── photobox_output.jpg     # Fixed filename (overwritten)
```

## 🚦 Getting Started

### Prerequisites

**System dependencies:**
```bash
sudo apt-get update
sudo apt-get install python3-opencv cups libcairo2-dev
```

**PhotoBox Python packages:**
```bash
cd ~/Ai_Photobox/Jetson_Ai-Photobox
python3 -m venv venv
source venv/bin/activate
pip3 install flask flask-socketio opencv-python pillow inputs python-socketio eventlet cairosvg
```

**SD1.5 Installation (on external SSD):**
```bash
cd /media/user/SSD/sdxl-project
source venv/bin/activate
# Dependencies already installed in SD1.5 environment
# - torch, diffusers, transformers
# - IP-Adapter repository
```

### Running the PhotoBox

```bash
cd ~/Ai_Photobox/Jetson_Ai-Photobox
source venv/bin/activate
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
- Remote Control: http://10.42.0.1:5000
- Image sharing: http://10.42.0.1:8080

### Setting up the Printer

```bash
# Add Canon SELPHY CP1500 to CUPS
# Make sure printer is connected via USB and powered on

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
# Logout and login again
```

### Branding Setup

Place your branding assets in `static/branding/`:
- `HS-Esslingen_Logo.svg` - Logo (SVG format, auto-converted)
- `HS-Esslingen_Code.png` - QR-Code (PNG with white background)

The system will automatically:
- Convert SVG logo to PNG
- Scale both to 350px width (~3cm at 300 DPI)
- Add white background with 11px rounded border
- Place logo top-left, QR-Code bottom-right
- Normalize all images to 1800x1200px print size

## 🎨 Features

### Main PhotoBox Interface (Port 5000)
- Live camera preview with video feed
- Big capture button with countdown animation
- Photo display with actions:
  - 🎨 **AI processing** - Random artistic transformation (30-60 sec)
  - 🖨️ **Print** - Direct printing of the current image (AI or not) with automatic branding
  - 🔄 **Take new photo** - Restart process
- Physical arcade button integration
- Real-time status feedback

### Image Sharing Server (Port 8080)
- Automatically shows the latest captured photo
- Large, mobile-friendly interface
- One-click download button
- Auto-refresh every 5 seconds
- Perfect for guests to download their photos via hotspot

### AI Image Processing
- **Stable Diffusion 1.5** with IP-Adapter-Full-Face
- Random prompt selection from curated collection
- Automatic face detection and cropping
- Themes include: Astronaut, Superhero, Royal, Doctor, etc.
- Preserves facial features while transforming style
- Processing isolated in separate environment (no conflicts)

### Print Branding System
- **Automatic logo placement** (top-left, 350px width)
- **QR-Code integration** (bottom-right, 350px width)
- **Smart image normalization:**
  - Camera photos (1920x1080) → scaled to 1800x1200
  - AI photos (512x512) → centered with white letterbox bars
  - Ensures consistent logo/QR size across all prints

## 🔧 Configuration

### Camera Settings
Edit `camera.py` to adjust:
- Resolution (current: 1920x1080)
- JPEG quality (default: 95)
- Camera index (default: 0)

### AI Processing Settings
Edit `/media/user/SSD/sdxl-project/generate_from_photobox.py`:
- Face crop scale (default: 1.4)
- IP-Adapter scale (default: 0.62)
- Inference steps (default: 45)
- Guidance scale (default: 10)

### Printer Settings
Edit `printer.py` to adjust:
- Printer name (default: Canon_SELPHY_CP1500)
- Paper size (default: photo-4x6)
- Print quality settings
- Enable/disable branding (`enable_branding=True`)

### Branding Settings
Edit `image_branding.py` to adjust:
- Logo width (default: 350px)
- QR-Code width (default: 350px)
- Border thickness (default: 11px)
- Border radius (default: 15px)
- Padding from edges (default: 20px)
- Print size normalization (default: 1800x1200px @ 300 DPI)

### Server Ports
- Main app: Port 5000 (change in `app.py`)
- Image sharing: Port 8080 (change in `image_server.py`)

## 🐛 Troubleshooting

**Button not working:**
- Check if `inputs` library is installed
- Verify user is in `input` group: `groups $USER`
- Test with: `python3 -c "from inputs import get_gamepad; get_gamepad()"`
- Reconnect USB or reboot if necessary

**Printer not found:**
- Ensure printer is powered on and connected via local jetson Hotspot
- Verify CUPS is running: `systemctl status cups`
- Check printer name: `lpstat -p`
- Restart CUPS if needed: `sudo systemctl restart cups`

**AI processing fails:**
- Check if SD1.5 installation is accessible: `ls /media/user/SSD/sdxl-project/`
- Verify Python environment: `/media/user/SSD/sdxl-project/venv/bin/python --version`
- Test SD1.5 directly: `cd /media/user/SSD/sdxl-project && source venv/bin/activate && python generate_from_photobox.py`
- Check CUDA availability: `python -c "import torch; print(torch.cuda.is_available())"`

**Branding not applied:**
- Check if branding files exist: `ls static/branding/`
- Verify CairoSVG is installed: `pip list | grep cairosvg`
- Check printer logs in console output
- Test branding directly: `python3 image_branding.py`

**Socket.IO not connecting:**
- Ensure `socket.io.min.js` exists in `static/js/`
- Check browser console for errors (F12)
- Verify Flask-SocketIO is installed: `pip list | grep flask-socketio`

**Image sharing not accessible on phone:**
- Check hotspot is active: `nmcli connection show --active`
- Get IP address: `hostname -I`
- Use the displayed IP addresses from server startup
- Ensure phone is connected to Jetson's hotspot (JetsonHotspot)

## ⚡ Performance Notes

**Current Performance:**
- Photo capture: Instant
- AI processing: 45-60 seconds (includes model loading)
- Print job submission: 1-5 seconds
- Actual printing: ~45 seconds (printer hardware)

**Known Limitations:**
- AI model loads fresh for each image (subprocess overhead)
- Fixed 512x512 AI output resolution

**Future Optimizations:**
- Persistent AI model service
- Batch processing capability
- Higher resolution AI output options

## 🤝 Development

This project is in active development for the Hochschule Esslingen.

**Current Focus:**
- System stability and reliability
- User experience improvements
- Performance optimization

**Author:** Nikolas Glisovic

---

**Status:** ✅ Fully functional AI-powered photo booth with camera, button, AI processing, automatic branding, printer integration, and photo sharing capabilities.

**Last Updated:** November 2025
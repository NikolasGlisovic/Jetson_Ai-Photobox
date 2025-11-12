from flask import Flask, render_template, jsonify, send_file
from camera import Camera
from printer import Printer  # NEU
import os
from datetime import datetime
from pathlib import Path
import uuid
import threading
from flask_socketio import SocketIO

app = Flask(__name__)

# SocketIO mit besserer Konfiguration für localhost UND Netzwerk
socketio = SocketIO(
    app, 
    cors_allowed_origins="*",
    async_mode='threading',
    logger=True,
    engineio_logger=True
)

# Konfiguration
PHOTO_DIR = Path("static/photos")
PHOTO_DIR.mkdir(exist_ok=True)

# Kamera-Instanz (wird lazy initialisiert)
camera = None

# Drucker-Instanz (wird lazy initialisiert) - NEU
printer = None

def get_camera():
    """Kamera lazy initialisieren"""
    global camera
    if camera is None:
        camera = Camera()
    return camera

def get_printer():
    """Drucker lazy initialisieren"""
    global printer
    if printer is None:
        printer = Printer()
    return printer

@app.route('/')
def index():
    """Hauptseite laden"""
    return render_template('index.html')

@app.route('/api/capture', methods=['POST'])
def capture_photo():
    """Foto aufnehmen"""
    try:
        # Eindeutigen Dateinamen generieren
        photo_id = str(uuid.uuid4())
        filename = f"{photo_id}.jpg"
        filepath = PHOTO_DIR / filename
        
        # Foto aufnehmen und speichern
        success = get_camera().capture(str(filepath))
        
        if success:
            return jsonify({
                'success': True,
                'photo_id': photo_id,
                'url': f'/static/photos/{filename}',
                'timestamp': datetime.now().isoformat()
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Kamera konnte kein Foto aufnehmen'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/preview')
def get_preview():
    """Live-Preview Frame holen"""
    frame = get_camera().get_frame()
    if frame:
        return send_file(frame, mimetype='image/jpeg')
    return jsonify({'error': 'Kein Frame verfügbar'}), 500

@app.route('/api/video_feed')
def video_feed():
    """Video-Stream für Live-Preview"""
    def generate():
        camera_instance = get_camera()
        while True:
            frame = camera_instance.get_frame()
            if frame:
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame.getvalue() + b'\r\n')
            else:
                break
    
    from flask import Response
    return Response(generate(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/api/photos')
def list_photos():
    """Alle verfügbaren Fotos auflisten"""
    photos = []
    for photo in PHOTO_DIR.glob("*.jpg"):
        photos.append({
            'id': photo.stem,
            'filename': photo.name,
            'url': f'/static/photos/{photo.name}',
            'timestamp': photo.stat().st_mtime
        })
    
    # Nach Zeitstempel sortieren (neueste zuerst)
    photos.sort(key=lambda x: x['timestamp'], reverse=True)
    return jsonify(photos)

@app.route('/download/<photo_id>')
def download_photo(photo_id):
    """Foto zum Download bereitstellen"""
    filepath = PHOTO_DIR / f"{photo_id}.jpg"
    if filepath.exists():
        return send_file(
            filepath,
            as_attachment=True,
            download_name=f"photobox_{photo_id}.jpg"
        )
    return jsonify({'error': 'Foto nicht gefunden'}), 404

# NEU: Drucker-Endpunkte
@app.route('/api/print/<photo_id>', methods=['POST'])
def print_photo(photo_id):
    """
    Foto drucken
    
    Args:
        photo_id: ID des zu druckenden Fotos
    """
    try:
        filepath = PHOTO_DIR / f"{photo_id}.jpg"
        
        if not filepath.exists():
            return jsonify({
                'success': False,
                'error': 'Foto nicht gefunden'
            }), 404
        
        # Drucker holen und drucken
        printer_instance = get_printer()
        result = printer_instance.print_image(str(filepath))
        
        if result['success']:
            return jsonify({
                'success': True,
                'message': result['message'],
                'job_id': result['job_id']
            })
        else:
            return jsonify({
                'success': False,
                'error': result['message']
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Unerwarteter Fehler: {str(e)}'
        }), 500

@app.route('/api/printer/status')
def printer_status():
    """Drucker-Status abfragen"""
    try:
        printer_instance = get_printer()
        status = printer_instance.get_printer_status()
        return jsonify(status)
    except Exception as e:
        return jsonify({
            'available': False,
            'status': 'Fehler',
            'details': str(e)
        }), 500

@app.route('/api/cleanup', methods=['POST'])
def cleanup_old_photos():
    """Alte Fotos löschen (älter als 1 Stunde)"""
    import time
    deleted = 0
    current_time = time.time()
    
    for photo in PHOTO_DIR.glob("*.jpg"):
        if current_time - photo.stat().st_mtime > 3600:  # 1 Stunde
            photo.unlink()
            deleted += 1
    
    return jsonify({
        'success': True,
        'deleted': deleted
    })

def listen_button():
    """Physischen Button überwachen und Events senden"""
    try:
        from inputs import get_gamepad
        print("🎮  Warte auf physische Knopfdrücke...")
        print("🎮  Erwarteter Event-Code: BTN_TRIGGER")
        
        while True:
            events = get_gamepad()
            for event in events:
                # Nur auf Button-Press reagieren (state == 1), nicht auf Release (state == 0)
                if event.ev_type == "Key" and event.state == 1:
                    print(f"✓ Button gedrückt: {event.code} (state={event.state})")
                    
                    # WebSocket-Event an alle verbundenen Clients senden
                    socketio.emit("button_pressed", {"code": event.code})
                    print("📡 WebSocket-Event 'button_pressed' gesendet")
                    
    except ImportError:
        print("⚠ Warning: 'inputs' library nicht gefunden - Button-Funktion deaktiviert")
        print("   Installiere mit: pip3 install inputs")
    except Exception as e:
        print(f"❌ Fehler im Button-Handler: {e}")


def start_image_server():
    """Startet den Image-Share-Server auf Port 8080"""
    try:
        import subprocess
        import sys
        
        # Starte image_server.py als separaten Prozess
        print("🌐 Starte Image-Share-Server auf Port 8080...")
        subprocess.Popen(
            [sys.executable, "image_server.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        print("✓ Image-Share-Server gestartet!")
        
    except Exception as e:
        print(f"⚠ Warnung: Image-Share-Server konnte nicht gestartet werden: {e}")


if __name__ == '__main__':
    # Image-Share-Server starten
    start_image_server()
    
    # Button-Listener starten
    threading.Thread(target=listen_button, daemon=True).start()
    
    # Hauptserver starten
    print("=" * 60)
    print("📸 PhotoBox Hauptserver")
    print("=" * 60)
    print("🌐 PhotoBox UI: http://127.0.0.1:5000")
    print("📱 Foto-Sharing: http://127.0.0.1:8080")
    print("=" * 60)
    
    socketio.run(app, host='0.0.0.0', port=5000, debug=True, allow_unsafe_werkzeug=True)
from flask import Flask, render_template, jsonify, send_file
from camera import Camera
import os
from datetime import datetime
from pathlib import Path
import uuid
import threading
from flask_socketio import SocketIO

app = Flask(__name__)

socketio = SocketIO(app, cors_allowed_origins="*")

# Konfiguration
PHOTO_DIR = Path("static/photos")
PHOTO_DIR.mkdir(exist_ok=True)

# Kamera-Instanz (wird lazy initialisiert)
camera = None

def get_camera():
    """Kamera lazy initialisieren"""
    global camera
    if camera is None:
        camera = Camera()
    return camera

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
    from inputs import get_gamepad
    print("🎮  Warte auf physische Knopfdrücke...")
    while True:
        events = get_gamepad()
        for event in events:
            if event.ev_type == "Key" and event.state == 1:
                print(f"Button gedrückt: {event.code}")
                socketio.emit("button_pressed")   # 🔔 an Browser senden


if __name__ == '__main__':

    threading.Thread(target=listen_button, daemon=True).start()
    # Server starten
    # host='0.0.0.0' macht Server im Netzwerk erreichbar
    app.run(host='0.0.0.0', port=5000, debug=True)
#!/usr/bin/env python3
"""
Image Share Server für PhotoBox
Zeigt das aktuellste Foto an und bietet Download an
Läuft auf Port 8080 parallel zur Hauptapp
"""
from flask import Flask, send_file, jsonify
from pathlib import Path
import os

app = Flask(__name__)

# Pfad zum Foto-Verzeichnis (gleicher wie in app.py)
PHOTO_DIR = Path("static/photos")

def get_latest_photo():
    """
    Findet das neueste Foto im Verzeichnis
    
    Returns:
        Path-Objekt oder None wenn kein Foto vorhanden
    """
    try:
        photos = list(PHOTO_DIR.glob("*.jpg"))
        if not photos:
            return None
        
        # Sortiere nach Änderungsdatum, neuestes zuerst
        latest = max(photos, key=lambda p: p.stat().st_mtime)
        return latest
    except Exception as e:
        print(f"Fehler beim Suchen des Fotos: {e}")
        return None

@app.route("/")
def show_image():
    """Hauptseite - zeigt aktuellstes Foto"""
    latest_photo = get_latest_photo()
    
    if not latest_photo:
        return '''
            <html>
            <head>
                <title>PhotoBox - Kein Foto</title>
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <style>
                    body {
                        text-align: center;
                        font-family: Arial, sans-serif;
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        color: white;
                        margin: 0;
                        padding: 50px 20px;
                        min-height: 100vh;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                    }
                    .message {
                        font-size: 24px;
                    }
                </style>
            </head>
            <body>
                <div class="message">
                    <h1>📸 PhotoBox</h1>
                    <p>Noch kein Foto aufgenommen!</p>
                    <p style="font-size: 16px; opacity: 0.8;">Mache ein Foto an der PhotoBox um es hier zu sehen.</p>
                </div>
            </body>
            </html>
        '''
    
    # Foto-Info
    photo_name = latest_photo.name
    photo_size = latest_photo.stat().st_size / 1024  # KB
    
    return f'''
        <html>
        <head>
            <title>PhotoBox - Dein Foto</title>
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                * {{
                    margin: 0;
                    padding: 0;
                    box-sizing: border-box;
                }}
                body {{
                    text-align: center;
                    font-family: Arial, sans-serif;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 20px;
                    min-height: 100vh;
                }}
                h1 {{
                    margin: 20px 0;
                    font-size: 2.5em;
                    text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
                }}
                .container {{
                    max-width: 1200px;
                    margin: 0 auto;
                }}
                img {{
                    max-width: 90%;
                    height: auto;
                    border-radius: 20px;
                    box-shadow: 0 10px 40px rgba(0,0,0,0.4);
                    margin: 20px 0;
                }}
                .download-btn {{
                    display: inline-block;
                    margin-top: 30px;
                    padding: 20px 60px;
                    font-size: 24px;
                    font-weight: bold;
                    color: white;
                    background-color: #4CAF50;
                    border: none;
                    border-radius: 50px;
                    text-decoration: none;
                    transition: all 0.3s ease;
                    box-shadow: 0 5px 20px rgba(0,0,0,0.3);
                    cursor: pointer;
                }}
                .download-btn:hover {{
                    background-color: #45a049;
                    transform: translateY(-3px);
                    box-shadow: 0 8px 25px rgba(0,0,0,0.4);
                }}
                .info {{
                    margin-top: 20px;
                    font-size: 14px;
                    opacity: 0.8;
                }}
                .refresh-btn {{
                    display: inline-block;
                    margin-top: 20px;
                    padding: 12px 30px;
                    font-size: 16px;
                    color: white;
                    background-color: rgba(255,255,255,0.2);
                    border: 2px solid white;
                    border-radius: 25px;
                    text-decoration: none;
                    transition: all 0.3s ease;
                    cursor: pointer;
                }}
                .refresh-btn:hover {{
                    background-color: rgba(255,255,255,0.3);
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>📸 Dein PhotoBox Foto</h1>
                <img src="/bild" alt="Dein Foto">
                
                <br>
                <a class="download-btn" href="/download" download>⬇️ Foto herunterladen</a>
                
                <br>
                <a class="refresh-btn" href="/" onclick="location.reload()">🔄 Aktualisieren</a>
                
                <p class="info">
                    Größe: {photo_size:.1f} KB
                </p>
            </div>
            
            <script>
                // Auto-Refresh alle 5 Sekunden um neues Foto zu zeigen
                setTimeout(() => {{
                    location.reload();
                }}, 5000);
            </script>
        </body>
        </html>
    '''

@app.route("/bild")
def bild():
    """Sendet das Bild zum Anzeigen"""
    latest_photo = get_latest_photo()
    
    if not latest_photo:
        return jsonify({'error': 'Kein Foto verfügbar'}), 404
    
    return send_file(latest_photo, mimetype="image/jpeg")

@app.route("/download")
def download():
    """Sendet das Bild als Download"""
    latest_photo = get_latest_photo()
    
    if not latest_photo:
        return jsonify({'error': 'Kein Foto verfügbar'}), 404
    
    # Download mit schönem Namen
    return send_file(
        latest_photo,
        as_attachment=True,
        download_name=f"photobox_foto.jpg"
    )

@app.route("/api/status")
def status():
    """API-Endpunkt für Status-Check"""
    latest_photo = get_latest_photo()
    
    if latest_photo:
        return jsonify({
            'has_photo': True,
            'filename': latest_photo.name,
            'size_kb': latest_photo.stat().st_size / 1024,
            'timestamp': latest_photo.stat().st_mtime
        })
    else:
        return jsonify({
            'has_photo': False
        })

if __name__ == "__main__":
    print("=" * 60)
    print("📸 PhotoBox Image Share Server")
    print("=" * 60)
    print("🌐 Server läuft auf:")
    print("   - http://127.0.0.1:8080 (localhost)")
    print("   - http://0.0.0.0:8080 (alle Netzwerk-Interfaces)")
    print("")
    print("📱 Verbinde dich mit deinem Smartphone/Tablet über:")
    print("   http://<JETSON-IP>:8080")
    print("=" * 60)
    
    app.run(host="0.0.0.0", port=8080, debug=False)
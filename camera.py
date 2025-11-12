import cv2
import numpy as np
from io import BytesIO
from PIL import Image

class Camera:
    def __init__(self, camera_index=0, width=1280, height=720):
        """
        Kamera initialisieren
        
        Args:
            camera_index: Index der Webcam (0 für erste Kamera)
            width: Bildbreite
            height: Bildhöhe
        """
        self.camera_index = camera_index
        self.width = width
        self.height = height
        self.cap = None
        
        # Kamera beim Start initialisieren
        self._init_camera()
    
    def _init_camera(self):
        """Kamera initialisieren"""
        try:
            self.cap = cv2.VideoCapture(self.camera_index)
            
            # Auflösung setzen
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
            
            # Auto-Focus deaktivieren für schnellere Aufnahmen (falls unterstützt)
            self.cap.set(cv2.CAP_PROP_AUTOFOCUS, 0)
            
            # Kamera "aufwärmen" - erste Frames verwerfen
            for _ in range(5):
                self.cap.read()
                
            print(f"Kamera erfolgreich initialisiert: {self.width}x{self.height}")
            return True
            
        except Exception as e:
            print(f"Fehler beim Initialisieren der Kamera: {e}")
            return False
    
    def capture(self, filepath):
        """
        Foto aufnehmen und speichern
        
        Args:
            filepath: Pfad wo das Foto gespeichert werden soll
            
        Returns:
            bool: True wenn erfolgreich, False sonst
        """
        if self.cap is None or not self.cap.isOpened():
            print("Kamera ist nicht initialisiert, versuche neu zu initialisieren...")
            self._init_camera()
        
        try:
            # Mehrere Frames verwerfen um aktuelles Bild zu bekommen
            # Dies ist wichtig weil Webcams oft alte Frames im Buffer haben
            for _ in range(5):
                ret, frame = self.cap.read()
                if not ret:
                    print("Warnung: Frame konnte nicht gelesen werden")
            
            # Jetzt das echte aktuelle Frame aufnehmen
            ret, frame = self.cap.read()
            
            if not ret or frame is None:
                print("Fehler: Kein Frame empfangen")
                return False
            
            # Optional: Bild spiegeln (wenn Webcam gespiegelt ist)
            # frame = cv2.flip(frame, 1)
            
            # Bild speichern
            cv2.imwrite(filepath, frame, [cv2.IMWRITE_JPEG_QUALITY, 95])
            print(f"Foto gespeichert: {filepath}")
            return True
            
        except Exception as e:
            print(f"Fehler beim Aufnehmen: {e}")
            return False
    
    def get_frame(self):
        """
        Einzelnes Frame für Preview holen (optional)
        
        Returns:
            BytesIO: JPEG-kodiertes Bild oder None
        """
        if self.cap is None or not self.cap.isOpened():
            return None
        
        try:
            ret, frame = self.cap.read()
            if not ret:
                return None
            
            # Frame in JPEG konvertieren
            ret, jpeg = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
            if not ret:
                return None
            
            return BytesIO(jpeg.tobytes())
            
        except Exception as e:
            print(f"Fehler beim Holen des Frames: {e}")
            return None
    
    def release(self):
        """Kamera-Ressourcen freigeben"""
        if self.cap is not None:
            self.cap.release()
            print("Kamera freigegeben")
    
    def __del__(self):
        """Destruktor - Kamera automatisch freigeben"""
        self.release()
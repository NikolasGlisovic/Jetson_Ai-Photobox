#!/usr/bin/env python3
"""
Canon SELPHY CP1500 Printer Integration für PhotoBox
"""
import subprocess
import os
from PIL import Image

class Printer:
    def __init__(self, printer_name="Canon_SELPHY_CP1500"):
        """
        Drucker initialisieren
        
        Args:
            printer_name: Name des Druckers in CUPS (Standard: Canon_SELPHY_CP1500)
        """
        self.printer_name = printer_name
        self._check_printer_available()
    
    def _check_printer_available(self):
        """Prüft ob Drucker verfügbar ist"""
        try:
            result = subprocess.run(
                ['lpstat', '-p', self.printer_name],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                print(f"✓ Drucker '{self.printer_name}' gefunden und bereit")
                return True
            else:
                print(f"⚠ Warnung: Drucker '{self.printer_name}' nicht gefunden")
                return False
        except Exception as e:
            print(f"⚠ Warnung: Drucker-Status konnte nicht geprüft werden: {e}")
            return False
    
    def print_image(self, image_path, media="photo-4x6", fit_to_page=True):
        """
        Druckt ein Bild auf dem Canon SELPHY CP1500
        
        Args:
            image_path: Pfad zum Bild
            media: Papierformat (z.B. "photo-4x6", "postcard")
            fit_to_page: Bild an Seite anpassen
            
        Returns:
            dict: {'success': bool, 'message': str, 'job_id': str oder None}
        """
        # Prüfen ob Datei existiert
        if not os.path.exists(image_path):
            return {
                'success': False,
                'message': f"Datei '{image_path}' nicht gefunden",
                'job_id': None
            }
        
        # Bild-Info laden (optional, für Logging)
        try:
            img = Image.open(image_path)
            print(f"Drucke Bild: {os.path.basename(image_path)} ({img.size[0]}x{img.size[1]}px)")
        except Exception as e:
            print(f"Warnung: Bild konnte nicht geladen werden: {e}")
        
        # Druckoptionen zusammenstellen
        options = []
        if media:
            options.extend(['-o', f'media={media}'])
        if fit_to_page:
            options.extend(['-o', 'fit-to-page'])
        
        # Druckbefehl ausführen
        try:
            cmd = ['lp', '-d', self.printer_name] + options + [image_path]
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True,
                timeout=10
            )
            
            # Job-ID aus Ausgabe extrahieren (z.B. "request id is Canon_SELPHY_CP1500-123")
            job_id = None
            if "request id is" in result.stdout:
                job_id = result.stdout.split("request id is")[-1].strip()
            
            print(f"✓ Druckauftrag erfolgreich gesendet! Job-ID: {job_id}")
            
            return {
                'success': True,
                'message': 'Druckauftrag erfolgreich gesendet',
                'job_id': job_id
            }
            
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'message': 'Druckbefehl hat zu lange gedauert (Timeout)',
                'job_id': None
            }
        except subprocess.CalledProcessError as e:
            error_msg = e.stderr if e.stderr else str(e)
            print(f"✗ Druckfehler: {error_msg}")
            return {
                'success': False,
                'message': f'Druckfehler: {error_msg}',
                'job_id': None
            }
        except Exception as e:
            print(f"✗ Unerwarteter Fehler: {e}")
            return {
                'success': False,
                'message': f'Unerwarteter Fehler: {str(e)}',
                'job_id': None
            }
    
    def get_printer_status(self):
        """
        Holt den aktuellen Drucker-Status
        
        Returns:
            dict: {'available': bool, 'status': str}
        """
        try:
            result = subprocess.run(
                ['lpstat', '-p', self.printer_name],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                # Status-Text parsen
                status_text = result.stdout.strip()
                is_idle = 'idle' in status_text.lower()
                
                return {
                    'available': True,
                    'status': 'Bereit' if is_idle else 'Beschäftigt',
                    'details': status_text
                }
            else:
                return {
                    'available': False,
                    'status': 'Nicht verfügbar',
                    'details': result.stderr
                }
                
        except Exception as e:
            return {
                'available': False,
                'status': 'Fehler',
                'details': str(e)
            }
    
    def cancel_job(self, job_id):
        """
        Bricht einen Druckauftrag ab
        
        Args:
            job_id: ID des Druckauftrags
            
        Returns:
            dict: {'success': bool, 'message': str}
        """
        try:
            subprocess.run(
                ['cancel', job_id],
                capture_output=True,
                text=True,
                check=True,
                timeout=5
            )
            return {
                'success': True,
                'message': f'Druckauftrag {job_id} abgebrochen'
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Fehler beim Abbrechen: {str(e)}'
            }


# Test-Funktion
if __name__ == "__main__":
    printer = Printer()
    
    # Status prüfen
    status = printer.get_printer_status()
    print(f"\nDrucker-Status: {status}")
    
    # Test-Druck (optional)
    # test_image = "/path/to/test.jpg"
    # result = printer.print_image(test_image)
    # print(f"\nDruck-Ergebnis: {result}")
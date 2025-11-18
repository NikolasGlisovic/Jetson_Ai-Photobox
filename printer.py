#!/usr/bin/env python3
"""
Canon SELPHY CP1500 Printer Integration für PhotoBox
MIT automatischem Branding (Logo + QR-Code)
"""
import subprocess
import os
from PIL import Image
from pathlib import Path
from image_branding import ImageBranding

class Printer:
    def __init__(self, printer_name="Canon_SELPHY_CP1500", enable_branding=True):
        """
        Drucker initialisieren
        
        Args:
            printer_name: Name des Druckers in CUPS (Standard: Canon_SELPHY_CP1500)
            enable_branding: Logo + QR-Code automatisch hinzufügen
        """
        self.printer_name = printer_name
        self.enable_branding = enable_branding
        
        # Branding-Modul initialisieren
        if self.enable_branding:
            try:
                self.branding = ImageBranding()
                print(f"✓ Branding aktiviert (Logo + QR-Code)")
            except Exception as e:
                print(f"⚠ Warnung: Branding konnte nicht geladen werden: {e}")
                self.enable_branding = False
        
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
        WICHTIG: Fügt automatisch Logo + QR-Code hinzu!
        
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
        
        # Bild-Info laden
        try:
            img = Image.open(image_path)
            print(f"Drucke Bild: {os.path.basename(image_path)} ({img.size[0]}x{img.size[1]}px)")
        except Exception as e:
            print(f"Warnung: Bild konnte nicht geladen werden: {e}")
        
        # BRANDING HINZUFÜGEN (falls aktiviert)
        print_path = image_path
        
        if self.enable_branding:
            try:
                # Temporäre Kopie mit Branding erstellen
                branded_path = str(Path(image_path).parent / f"_print_{Path(image_path).name}")
                
                print(f"\n🎨 Füge Branding hinzu...")
                self.branding.add_branding(image_path, branded_path)
                
                # Diese gebrandete Version drucken
                print_path = branded_path
                print(f"✓ Branding erfolgreich hinzugefügt")
                
            except Exception as e:
                print(f"⚠ Warnung: Branding fehlgeschlagen, drucke Original: {e}")
                print_path = image_path
        
        # Druckoptionen zusammenstellen
        options = []
        if media:
            options.extend(['-o', f'media={media}'])
        if fit_to_page:
            options.extend(['-o', 'fit-to-page'])
        
        # Druckbefehl ausführen
        try:
            cmd = ['lp', '-d', self.printer_name] + options + [print_path]
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True,
                timeout=10
            )
            
            # Job-ID aus Ausgabe extrahieren
            job_id = None
            if "request id is" in result.stdout:
                job_id = result.stdout.split("request id is")[-1].strip()
            
            print(f"✓ Druckauftrag erfolgreich gesendet! Job-ID: {job_id}")
            
            # Temporäre gebrandete Datei löschen
            if self.enable_branding and print_path != image_path:
                try:
                    os.remove(print_path)
                    print(f"✓ Temporäre Druckdatei gelöscht")
                except:
                    pass
            
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
    
    # Test-Druck mit Branding
    test_image = "static/photos/test.jpg"  # Ersetze mit echtem Pfad
    if Path(test_image).exists():
        print(f"\n🖨️  Starte Test-Druck mit Branding...")
        result = printer.print_image(test_image)
        print(f"\nDruck-Ergebnis: {result}")
    else:
        print(f"\n⚠️  Test-Bild nicht gefunden: {test_image}")
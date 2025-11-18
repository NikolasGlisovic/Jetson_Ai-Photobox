#!/usr/bin/env python3
"""
AI Processor für PhotoBox
Ruft externe SD1.5 Pipeline auf ohne Library-Konflikte
"""
import subprocess
import shutil
from pathlib import Path
import time

class AIProcessor:
    def __init__(self):
        # Pfade zur SD1.5 Installation
        self.sd_project_dir = Path("/media/user/SSD/sdxl-project")
        self.sd_venv_python = self.sd_project_dir / "venv/bin/python"
        self.sd_script = self.sd_project_dir / "generate_from_photobox.py"
        
        # Input/Output Pfade (feste Namen für Überschreiben)
        self.sd_input_dir = self.sd_project_dir / "input_images"
        self.sd_output_dir = self.sd_project_dir / "output_images"
        self.input_filename = "photobox_input.jpg"
        self.output_filename = "photobox_output.jpg"
        
        print(f"🎨 AI Processor initialisiert")
        print(f"   SD Project: {self.sd_project_dir}")
        print(f"   Input: {self.sd_input_dir / self.input_filename}")
        print(f"   Output: {self.sd_output_dir / self.output_filename}")
    
    def process_image(self, input_image_path):
        """
        Verarbeitet ein Bild mit SD1.5
        
        Args:
            input_image_path: Pfad zum Original-Foto
            
        Returns:
            dict: {'success': bool, 'output_path': str, 'message': str, 'theme': str}
        """
        try:
            # 1. Input-Bild kopieren (überschreibt altes)
            input_dest = self.sd_input_dir / self.input_filename
            print(f"📋 Kopiere Input: {input_image_path} → {input_dest}")
            shutil.copy2(input_image_path, input_dest)
            
            # 2. SD1.5 Pipeline aufrufen
            print(f"🚀 Starte SD1.5 Pipeline...")
            start_time = time.time()
            
            result = subprocess.run(
                [str(self.sd_venv_python), str(self.sd_script)],
                cwd=str(self.sd_project_dir),
                capture_output=True,
                text=True,
                timeout=120  # 2 Minuten Timeout
            )
            
            elapsed = time.time() - start_time
            print(f"⏱️  Verarbeitung dauerte {elapsed:.1f} Sekunden")
            
            # 3. Output checken
            if result.returncode != 0:
                print(f"❌ SD1.5 Fehler:\n{result.stderr}")
                return {
                    'success': False,
                    'message': f'SD1.5 Fehler: {result.stderr[:200]}',
                    'output_path': None,
                    'theme': None
                }
            
            # 4. Prüfen ob Output existiert
            output_path = self.sd_output_dir / self.output_filename
            if not output_path.exists():
                return {
                    'success': False,
                    'message': 'Output-Bild wurde nicht erstellt',
                    'output_path': None,
                    'theme': None
                }
            
            # 5. Theme aus stdout extrahieren (falls vorhanden)
            theme = "Unknown"
            for line in result.stdout.split('\n'):
                if "Theme:" in line:
                    theme = line.split("Theme:")[-1].strip()
                    break
            
            print(f"✅ AI-Verarbeitung erfolgreich!")
            print(f"   Theme: {theme}")
            print(f"   Output: {output_path}")
            
            return {
                'success': True,
                'message': 'Bild erfolgreich verarbeitet',
                'output_path': str(output_path),
                'theme': theme
            }
            
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'message': 'Timeout: Verarbeitung dauerte zu lange',
                'output_path': None,
                'theme': None
            }
        except Exception as e:
            print(f"❌ Unerwarteter Fehler: {e}")
            return {
                'success': False,
                'message': f'Fehler: {str(e)}',
                'output_path': None,
                'theme': None
            }
    
    def check_availability(self):
        """
        Prüft ob SD1.5 verfügbar ist
        
        Returns:
            dict: {'available': bool, 'message': str}
        """
        # Prüfe ob Verzeichnisse existieren
        if not self.sd_project_dir.exists():
            return {
                'available': False,
                'message': f'SD Project nicht gefunden: {self.sd_project_dir}'
            }
        
        if not self.sd_venv_python.exists():
            return {
                'available': False,
                'message': f'Python venv nicht gefunden: {self.sd_venv_python}'
            }
        
        if not self.sd_script.exists():
            return {
                'available': False,
                'message': f'Skript fehlt: {self.sd_script}'
            }
        
        # Directories erstellen falls nötig
        self.sd_input_dir.mkdir(exist_ok=True)
        self.sd_output_dir.mkdir(exist_ok=True)
        
        return {
            'available': True,
            'message': 'SD1.5 bereit'
        }


# Test-Funktion
if __name__ == "__main__":
    processor = AIProcessor()
    
    # Status prüfen
    status = processor.check_availability()
    print(f"\nStatus: {status}")
    
    # Optional: Test mit Beispielbild
    # test_image = "/path/to/test.jpg"
    # result = processor.process_image(test_image)
    # print(f"\nErgebnis: {result}")
#!/usr/bin/env python3
"""
Image Branding für PhotoBox
Fügt HS-Esslingen Logo und QR-Code zu Fotos hinzu
Normalisiert alle Bilder auf Druckgröße (1800x1200px @ 300 DPI für 10x15cm)
"""
from PIL import Image, ImageDraw
from pathlib import Path
import cairosvg
from io import BytesIO

class ImageBranding:
    def __init__(self, logo_path="static/branding/HS-Esslingen_Logo.svg", 
                 qr_path="static/branding/HS-Esslingen_Code.png"):
        """
        Image Branding initialisieren
        
        Args:
            logo_path: Pfad zum SVG Logo
            qr_path: Pfad zum QR-Code PNG
        """
        self.logo_path = Path(logo_path)
        self.qr_path = Path(qr_path)
        
        # Zielgröße für Druck (10x15cm bei 300 DPI)
        self.print_width = 1800
        self.print_height = 1200
        
        # Konfiguration für Logo/QR
        self.logo_width = 350  # Pixel (entspricht ca. 3cm bei 300 DPI)
        self.qr_width = 350    # Pixel
        self.border_thickness = 11  # 3mm bei 300 DPI ≈ 11 Pixel
        self.border_radius = 15  # Abgerundete Ecken
        self.padding = 20  # Abstand vom Rand des Fotos
        
        print(f"🎨 Image Branding initialisiert")
        print(f"   Logo: {self.logo_path}")
        print(f"   QR-Code: {self.qr_path}")
        print(f"   Druckgröße: {self.print_width}x{self.print_height}px")
    
    def _svg_to_png(self, svg_path, width):
        """
        Konvertiert SVG zu PNG mit gewünschter Breite
        
        Args:
            svg_path: Pfad zum SVG
            width: Gewünschte Breite in Pixel
            
        Returns:
            PIL Image
        """
        # SVG zu PNG konvertieren
        png_data = cairosvg.svg2png(
            url=str(svg_path),
            output_width=width
        )
        
        # PNG als PIL Image laden
        return Image.open(BytesIO(png_data)).convert("RGBA")
    
    def _create_logo_with_background(self, logo_img):
        """
        Erstellt Logo mit weißem Hintergrund und abgerundetem Rahmen
        
        Args:
            logo_img: PIL Image des Logos (RGBA)
            
        Returns:
            PIL Image mit Hintergrund und Rahmen
        """
        # Größe des finalen Bildes (Logo + Padding für Rahmen)
        border = self.border_thickness
        total_width = logo_img.width + 2 * border
        total_height = logo_img.height + 2 * border
        
        # Neues Bild mit weißem Hintergrund erstellen
        result = Image.new('RGBA', (total_width, total_height), (255, 255, 255, 0))
        
        # Weiße Füllung mit abgerundeten Ecken zeichnen
        draw = ImageDraw.Draw(result)
        
        # Äußerer Rahmen (grau)
        draw.rounded_rectangle(
            [(0, 0), (total_width, total_height)],
            radius=self.border_radius,
            fill=(255, 255, 255, 255),
            outline=(200, 200, 200, 255),
            width=border
        )
        
        # Logo in die Mitte setzen
        logo_x = border
        logo_y = border
        result.paste(logo_img, (logo_x, logo_y), logo_img)
        
        return result
    
    def _create_qr_with_background(self, qr_img):
        """
        Erstellt QR-Code mit abgerundetem Rahmen
        
        Args:
            qr_img: PIL Image des QR-Codes
            
        Returns:
            PIL Image mit Rahmen
        """
        # QR-Code hat schon weißen Hintergrund, nur Rahmen hinzufügen
        border = self.border_thickness
        total_width = qr_img.width + 2 * border
        total_height = qr_img.height + 2 * border
        
        # Neues Bild erstellen
        result = Image.new('RGBA', (total_width, total_height), (255, 255, 255, 0))
        
        # Weißer Hintergrund mit Rahmen
        draw = ImageDraw.Draw(result)
        draw.rounded_rectangle(
            [(0, 0), (total_width, total_height)],
            radius=self.border_radius,
            fill=(255, 255, 255, 255),
            outline=(200, 200, 200, 255),
            width=border
        )
        
        # QR-Code in die Mitte setzen
        qr_x = border
        qr_y = border
        
        # QR-Code konvertieren falls nötig
        if qr_img.mode != 'RGBA':
            qr_img = qr_img.convert('RGBA')
        
        result.paste(qr_img, (qr_x, qr_y), qr_img)
        
        return result
    
    def _normalize_to_print_size(self, photo):
        """
        Normalisiert Foto auf Druckgröße mit Letterbox (weiße Balken)
        
        Args:
            photo: PIL Image
            
        Returns:
            PIL Image in Druckgröße (1800x1200px)
        """
        original_width, original_height = photo.size
        print(f"   Original: {original_width}x{original_height}px")
        
        # Seitenverhältnis berechnen
        aspect_original = original_width / original_height
        aspect_target = self.print_width / self.print_height
        
        # Neue Größe berechnen (fit inside, kein Crop)
        if aspect_original > aspect_target:
            # Breiter als Ziel → an Breite anpassen
            new_width = self.print_width
            new_height = int(self.print_width / aspect_original)
        else:
            # Höher als Ziel → an Höhe anpassen
            new_height = self.print_height
            new_width = int(self.print_height * aspect_original)
        
        # Bild skalieren
        photo_resized = photo.resize((new_width, new_height), Image.LANCZOS)
        print(f"   Skaliert: {new_width}x{new_height}px")
        
        # Weißen Canvas erstellen
        canvas = Image.new('RGB', (self.print_width, self.print_height), (255, 255, 255))
        
        # Bild zentrieren auf Canvas (Letterbox)
        x_offset = (self.print_width - new_width) // 2
        y_offset = (self.print_height - new_height) // 2
        
        canvas.paste(photo_resized, (x_offset, y_offset))
        print(f"   Letterbox: {x_offset}px links/rechts, {y_offset}px oben/unten")
        print(f"   Final: {self.print_width}x{self.print_height}px (Druckgröße)")
        
        return canvas
    
    def add_branding(self, input_image_path, output_image_path=None):
        """
        Fügt Logo und QR-Code zum Bild hinzu
        Normalisiert auf Druckgröße mit weißen Letterbox-Balken
        
        Args:
            input_image_path: Pfad zum Original-Bild
            output_image_path: Pfad für Ausgabe (wenn None, wird Original überschrieben)
            
        Returns:
            str: Pfad zum gebrandeten Bild
        """
        print(f"\n🎨 Füge Branding hinzu: {input_image_path}")
        
        # Original-Bild laden
        photo = Image.open(input_image_path).convert("RGB")
        
        # AUF DRUCKGRÖSSE NORMALISIEREN (mit weißen Balken)
        photo_normalized = self._normalize_to_print_size(photo)
        
        # Logo vorbereiten (SVG → PNG → mit Hintergrund)
        print(f"   Lade Logo...")
        logo_png = self._svg_to_png(self.logo_path, self.logo_width)
        logo_final = self._create_logo_with_background(logo_png)
        
        # QR-Code vorbereiten
        print(f"   Lade QR-Code...")
        qr_img = Image.open(self.qr_path).convert("RGBA")
        
        # QR-Code auf gewünschte Größe skalieren
        aspect_ratio = qr_img.height / qr_img.width
        qr_height = int(self.qr_width * aspect_ratio)
        qr_img = qr_img.resize((self.qr_width, qr_height), Image.LANCZOS)
        
        qr_final = self._create_qr_with_background(qr_img)
        
        # Foto in RGBA konvertieren für Transparenz
        photo_rgba = photo_normalized.convert("RGBA")
        
        # Logo oben links platzieren
        logo_x = self.padding
        logo_y = self.padding
        photo_rgba.paste(logo_final, (logo_x, logo_y), logo_final)
        print(f"   Logo platziert: ({logo_x}, {logo_y})")
        
        # QR-Code unten rechts platzieren
        qr_x = photo_rgba.width - qr_final.width - self.padding
        qr_y = photo_rgba.height - qr_final.height - self.padding
        photo_rgba.paste(qr_final, (qr_x, qr_y), qr_final)
        print(f"   QR-Code platziert: ({qr_x}, {qr_y})")
        
        # Zurück zu RGB konvertieren und speichern
        photo_final = photo_rgba.convert("RGB")
        
        # Output-Pfad bestimmen
        if output_image_path is None:
            output_image_path = input_image_path
        
        photo_final.save(output_image_path, "JPEG", quality=95)
        print(f"   ✅ Gespeichert: {output_image_path}")
        
        return output_image_path


# Test-Funktion
if __name__ == "__main__":
    branding = ImageBranding()
    
    # Test mit einem Beispielbild
    test_image = "static/photos/test.jpg"  # Ersetze mit echtem Pfad
    
    if Path(test_image).exists():
        result = branding.add_branding(
            test_image,
            output_image_path="static/photos/test_branded.jpg"
        )
        print(f"\n✅ Test erfolgreich: {result}")
    else:
        print(f"\n⚠️  Test-Bild nicht gefunden: {test_image}")
        print("   Erstelle erst ein Foto in der PhotoBox!")
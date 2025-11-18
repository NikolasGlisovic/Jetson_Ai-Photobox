#!/usr/bin/env python3
"""
SD1.5 Pipeline für PhotoBox
Liest: /media/user/SSD/sdxl-project/input_images/photobox_input.jpg
Schreibt: /media/user/SSD/sdxl-project/output_images/photobox_output.jpg
"""
import torch
import os
import sys
import random
from PIL import Image
import cv2
import numpy as np

sys.path.insert(0, '/media/user/SSD/sdxl-project/IP-Adapter')

from diffusers import StableDiffusionPipeline, DDIMScheduler
from ip_adapter import IPAdapterFull
from prompts_optimized import PROMPTS, NEGATIVE_PROMPT

class SimpleFaceCropper:
    def __init__(self):
        cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        self.face_cascade = cv2.CascadeClassifier(cascade_path)
    
    def crop_face_plus(self, image_path, output_size=(512, 512), face_scale=1.4):
        if isinstance(image_path, str):
            img = cv2.imread(image_path)
        else:
            img = cv2.cvtColor(np.array(image_path), cv2.COLOR_RGB2BGR)
        
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, 1.1, 5, minSize=(30, 30))
        
        if len(faces) == 0:
            faces = self.face_cascade.detectMultiScale(gray, 1.05, 3, minSize=(20, 20))
        
        if len(faces) == 0:
            print("⚠️  Kein Gesicht gefunden, nutze Original")
            if isinstance(image_path, str):
                return Image.open(image_path).convert("RGB").resize(output_size, Image.LANCZOS)
            else:
                return image_path.resize(output_size, Image.LANCZOS)
        
        face = max(faces, key=lambda x: x[2] * x[3])
        x, y, w, h = face
        
        print(f"   Gesicht gefunden: x={x}, y={y}, w={w}, h={h}")
        
        center_x = x + w // 2
        center_y = y + h // 2
        
        new_w = int(w * face_scale)
        new_h = int(h * face_scale)
        
        x1 = max(0, center_x - new_w // 2)
        y1 = max(0, center_y - new_h // 2)
        x2 = min(img.shape[1], center_x + new_w // 2)
        y2 = min(img.shape[0], center_y + new_h // 2)
        
        print(f"   Crop-Bereich: [{x1}, {y1}] → [{x2}, {y2}]")
        
        cropped = img[y1:y2, x1:x2]
        cropped_rgb = cv2.cvtColor(cropped, cv2.COLOR_BGR2RGB)
        
        pil_img = Image.fromarray(cropped_rgb)
        pil_img = pil_img.resize(output_size, Image.LANCZOS)
        
        print(f"   ✅ Gesicht zugeschnitten (scale: {face_scale})")
        
        return pil_img

# KONFIGURATION
BASE_DIR = "/media/user/SSD/sdxl-project"
INPUT_IMAGE = f"{BASE_DIR}/input_images/photobox_input.jpg"
OUTPUT_IMAGE = f"{BASE_DIR}/output_images/photobox_output.jpg"

device = "cuda"

# OPTIMALE EINSTELLUNGEN
FACE_SCALE = 1.4
IP_SCALE = 0.62
STEPS = 45
GUIDANCE_SCALE = 10
SEED = 42 # Zufälliger Seed für Variation

print("=" * 60)
print("🎨 PhotoBox AI Processor")
print("=" * 60)
print(f"Input: {INPUT_IMAGE}")
print(f"Output: {OUTPUT_IMAGE}")
print("=" * 60)

# Pipeline laden
print("\n🚀 Lade Modelle...")
pipe = StableDiffusionPipeline.from_pretrained(
    "runwayml/stable-diffusion-v1-5",
    torch_dtype=torch.float16,
    cache_dir=f"{BASE_DIR}/huggingface"
).to(device)

pipe.scheduler = DDIMScheduler(
    num_train_timesteps=1000,
    beta_start=0.00085,
    beta_end=0.012,
    beta_schedule="scaled_linear",
    clip_sample=False,
    set_alpha_to_one=False,
    steps_offset=1,
)

pipe.enable_vae_slicing()

ip_model = IPAdapterFull(
    pipe,
    image_encoder_path=f"{BASE_DIR}/models/ip-adapter/models/image_encoder",
    ip_ckpt=f"{BASE_DIR}/models/ip-adapter/models/ip-adapter-full-face_sd15.bin",
    device=device,
    num_tokens=257,
)

print("✅ Modelle geladen!\n")

# Bild croppen
print("📸 Verarbeite Input-Bild...")
cropper = SimpleFaceCropper()
input_image = cropper.crop_face_plus(
    INPUT_IMAGE,
    output_size=(512, 512),
    face_scale=FACE_SCALE
)

# Zufälligen Prompt wählen
selected_name = random.choice(list(PROMPTS.keys()))
selected_prompt = PROMPTS[selected_name]

print(f"\n{'='*60}")
print(f"🎲 Zufälliger Prompt: {selected_name.upper()}")
print(f"{'='*60}")
print(f"Prompt: {selected_prompt}")
print(f"Seed: {SEED}")
print(f"{'='*60}\n")

# Generierung
print("🎨 Generiere Bild...")
torch.cuda.empty_cache()

images = ip_model.generate(
    pil_image=input_image,
    prompt=selected_prompt,
    negative_prompt=NEGATIVE_PROMPT,
    scale=IP_SCALE,
    num_samples=1,
    seed=SEED,
    guidance_scale=GUIDANCE_SCALE,
    num_inference_steps=STEPS,
)

# Speichern (überschreibt altes Bild)
images[0].save(OUTPUT_IMAGE)

print(f"\n{'='*60}")
print(f"✅ Fertig!")
print(f"   Theme: {selected_name}")
print(f"   Seed: {SEED}")
print(f"   Output: {OUTPUT_IMAGE}")
print(f"{'='*60}")
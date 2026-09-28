import os
from PIL import Image
import numpy as np
from collections import deque

SOURCE_PATH = r"C:\Users\ASUS\.gemini\antigravity-ide\brain\1631bb5a-84c0-4dc0-93ec-758c9fe3d60b\.user_uploaded\media_1790518151167.png"
OUTPUT_DIR = r"c:\Users\ASUS\sih\frontend\public"

os.makedirs(OUTPUT_DIR, exist_ok=True)

# 1. Load source image
src_im = Image.open(SOURCE_PATH).convert('RGB')
w, h = src_im.size
arr = np.array(src_im, dtype=float)

# Save exact original as logo.png
src_im.save(os.path.join(OUTPUT_DIR, "logo.png"), quality=95)
print("Saved logo.png")

# 2. Compute background distance
bg_color = np.array([249.0, 246.0, 241.0])
diff = np.linalg.norm(arr - bg_color, axis=2)

# Shield area separation is at y = 734
shield_split_y = 734
barrier = (diff > 22.0)

# Flood fill from outside for the shield region
visited = np.zeros((shield_split_y, w), dtype=bool)
q = deque()
for x in range(w):
    if not barrier[0, x]:
        visited[0, x] = True
        q.append((0, x))
for y in range(shield_split_y):
    if not barrier[y, 0]:
        visited[y, 0] = True
        q.append((y, 0))
    if not barrier[y, w - 1]:
        visited[y, w - 1] = True
        q.append((y, w - 1))

while q:
    cy, cx = q.popleft()
    for dy, dx in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        ny, nx = cy + dy, cx + dx
        if 0 <= ny < shield_split_y and 0 <= nx < w:
            if not visited[ny, nx] and not barrier[ny, nx]:
                visited[ny, nx] = True
                q.append((ny, nx))

# Create alpha channel array (0.0 to 1.0)
alpha = np.zeros((h, w), dtype=float)

# For shield area (y < shield_split_y):
# Inside pixels (~visited) have full opacity
# Pixels on the visited side with diff > 4 get smooth antialiased alpha
for y in range(shield_split_y):
    for x in range(w):
        if not visited[y, x]:
            alpha[y, x] = 1.0
        else:
            d = diff[y, x]
            if d > 4.0:
                alpha[y, x] = np.clip((d - 4.0) / 18.0, 0.0, 1.0)

# For text area (y >= shield_split_y):
# diff <= 5 is background (alpha 0)
# diff >= 25 is solid stroke (alpha 1)
for y in range(shield_split_y, h):
    for x in range(w):
        d = diff[y, x]
        if d <= 4.0:
            alpha[y, x] = 0.0
        elif d >= 24.0:
            alpha[y, x] = 1.0
        else:
            alpha[y, x] = (d - 4.0) / 20.0

# 3. Defringe RGB channels where alpha is transparent to avoid cream halo
out_rgb = np.copy(arr)
mask_alpha = alpha > 0.005
# Defringing formula: fg = (observed - (1 - a) * bg) / a
a_expanded = np.expand_dims(alpha, axis=2)
denom = np.maximum(a_expanded, 0.05)
defringed = (arr - (1.0 - a_expanded) * bg_color) / denom
defringed = np.clip(defringed, 0.0, 255.0)

# For pixels inside the shield (not visited), keep original colors unaltered
for y in range(shield_split_y):
    for x in range(w):
        if not visited[y, x]:
            defringed[y, x] = arr[y, x]

# Combine into RGBA image
rgba_arr = np.zeros((h, w, 4), dtype=np.uint8)
rgba_arr[:, :, :3] = np.round(defringed).astype(np.uint8)
rgba_arr[:, :, 3] = np.round(alpha * 255.0).astype(np.uint8)

transparent_logo = Image.fromarray(rgba_arr, mode='RGBA')
transparent_logo.save(os.path.join(OUTPUT_DIR, "logo-transparent.png"), format='PNG', optimize=True)
print("Saved logo-transparent.png")

# 4. Generate Dark Theme Variant (White text for dark backgrounds)
# In text area (y >= shield_split_y), turn dark green letters into crisp white/silver (#FFFFFF with subtle emerald tint)
rgba_dark = np.copy(rgba_arr)
for y in range(shield_split_y, h):
    for x in range(w):
        a_val = rgba_dark[y, x, 3]
        if a_val > 0:
            # Original text is dark green; invert luminance to clean crisp white
            rgba_dark[y, x, 0] = 248 # R
            rgba_dark[y, x, 1] = 250 # G
            rgba_dark[y, x, 2] = 252 # B
            # Keep alpha as is

dark_logo = Image.fromarray(rgba_dark, mode='RGBA')
dark_logo.save(os.path.join(OUTPUT_DIR, "logo-dark.png"), format='PNG', optimize=True)
print("Saved logo-dark.png")

# 5. Generate Shield-Only Assets (Cropped to shield bounds with slight padding)
# Shield content is roughly x=[236, 792], y=[67, 734]
# Shield bounding box: width = 556, height = 667
# Let's crop a square region centered around the shield:
cx = 514
cy = int((67 + 734) / 2) # 400
half_size = int(667 / 2 + 30) # ~363px => 726x726 box

box = (
    max(0, cx - half_size),
    max(0, cy - half_size),
    min(w, cx + half_size),
    min(h, cy + half_size)
)

# Crop from transparent logo
shield_transparent = transparent_logo.crop(box)
# Resize to high-res standard 512x512
shield_512 = shield_transparent.resize((512, 512), Image.Resampling.LANCZOS)
shield_512.save(os.path.join(OUTPUT_DIR, "logo-shield-transparent.png"), format='PNG', optimize=True)

# Also create small icons (64x64, 32x32, 192x192) for favicons and web manifests
shield_192 = shield_transparent.resize((192, 192), Image.Resampling.LANCZOS)
shield_192.save(os.path.join(OUTPUT_DIR, "logo-192.png"), format='PNG', optimize=True)

shield_64 = shield_transparent.resize((64, 64), Image.Resampling.LANCZOS)
shield_64.save(os.path.join(OUTPUT_DIR, "logo-64.png"), format='PNG', optimize=True)

shield_32 = shield_transparent.resize((32, 32), Image.Resampling.LANCZOS)
shield_32.save(os.path.join(OUTPUT_DIR, "favicon.png"), format='PNG', optimize=True)

# Crop from original cream logo as well
shield_cream = src_im.crop(box).resize((512, 512), Image.Resampling.LANCZOS)
shield_cream.save(os.path.join(OUTPUT_DIR, "logo-shield.png"), format='PNG', quality=95)

print("Saved shield-only icons (logo-shield-transparent.png, logo-shield.png, favicon.png, logo-192.png)")

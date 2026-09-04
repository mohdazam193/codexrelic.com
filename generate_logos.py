from PIL import Image

palettes = {
    "default": (93, 209, 197),  # #5dd1c5
    "cyber": (16, 185, 129),    # #10b981
    "cosmic": (139, 92, 246),   # #8b5cf6
    "codex": (245, 158, 11),    # #f59e0b
    "steel": (59, 130, 246)     # #3b82f6
}

def generate_versions(path, prefix):
    img = Image.open(path).convert("RGBA")
    original_data = img.getdata()
    
    for palette_name, color in palettes.items():
        new_data = []
        replaced_count = 0
        for r, g, b, a in original_data:
            if a == 0:
                new_data.append((0,0,0,0))
                continue
            
            # The 'X' is currently teal (e.g. 93, 209, 197). 
            # So Green and Blue are much higher than Red.
            if g > r + 30 and b > r + 30:
                # Replace teal with palette color.
                # To preserve shading/anti-aliasing, we could blend, but the X is mostly solid.
                new_data.append((color[0], color[1], color[2], a))
                replaced_count += 1
            else:
                new_data.append((r, g, b, a))
                
        print(f"Generated {prefix}-{palette_name}.png. Replaced {replaced_count} pixels.")
        new_img = Image.new("RGBA", img.size)
        new_img.putdata(new_data)
        new_img.save(f"src/public/assets/images/{prefix}-{palette_name}.png")

generate_versions("src/public/assets/images/logo-dark.png", "logo-dark")
generate_versions("src/public/assets/images/logo-light.png", "logo-light")

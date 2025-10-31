import numpy as np
from PIL import Image, ImageTk, ImageOps
import tkinter as tk
from tkinter import filedialog, messagebox

def stereogram_from_depth_texture(depth_map, texture_img, pattern_width=80, depth_strength=20):
    h, w = depth_map.shape
    texture_img = texture_img.resize((w, h), Image.LANCZOS)
    texture = np.array(texture_img.convert('RGB'))
    sgram = np.zeros_like(texture)
    for y in range(h):
        indices = np.arange(w)
        for x in range(pattern_width, w):
            z = int(depth_strength * (1.0 - depth_map[y, x] / 255.0))
            left = x - pattern_width
            if left - z >= 0:
                indices[x] = indices[left - z]
        sgram[y, :pattern_width] = texture[y, :pattern_width]
        for x in range(pattern_width, w):
            sgram[y, x] = sgram[y, indices[x]]
    return Image.fromarray(sgram)

def load_and_resize(path, max_dim=600):
    img = Image.open(path)
    img = ImageOps.grayscale(img)
    aspect = img.width / img.height
    w = min(max_dim, img.width)
    h = int(w / aspect) if aspect > 1 else min(max_dim, img.height)
    img = img.resize((w, h), Image.LANCZOS)
    arr = np.array(img)
    # Auto-invert if mostly white (to help user error)
    if np.mean(arr) > 200: arr = 255 - arr
    return arr

def load_and_resize_texture(path, width, height):
    img = Image.open(path)
    img = img.convert('RGB').resize((width, height), Image.LANCZOS)
    return img

def update_preview():
    global depth_map, texture_img, current_sgram
    if depth_map is None or texture_img is None:
        preview.config(image="")
        status_label.config(text="Please load BOTH depth map and texture.")
        return

    try:
        pw = int(pattern_width.get())
        ds = int(depth_strength.get())
        current_sgram = stereogram_from_depth_texture(
            depth_map, texture_img, pw, ds)
        img = current_sgram.copy()
        img.thumbnail((550, 550))
        img_tk = ImageTk.PhotoImage(img)
        preview.config(image=img_tk)
        preview.image = img_tk
        status_label.config(text=f"Preview ({img.width}×{img.height}) OK.")
    except Exception as e:
        preview.config(image='')
        status_label.config(text=f"Error: {e}")

def select_depth_map():
    global depth_map, texture_img
    path = filedialog.askopenfilename(
        title="Select Depth Map (black on white)", filetypes=[("Image files", "*.png;*.jpg;*.jpeg;*.bmp")])
    if not path: return
    try:
        depth_map_arr = load_and_resize(path)
        status_label.config(text=f"Depth map loaded ({depth_map_arr.shape[1]}×{depth_map_arr.shape[0]})")
        depth_map = depth_map_arr
        # If texture already loaded, resize to match
        if texture_img is not None:
            texture_img_resized = texture_img.resize((depth_map.shape[1], depth_map.shape[0]), Image.LANCZOS)
            texture_img = texture_img_resized
        update_preview()
    except Exception as e:
        messagebox.showerror("Image error", f"Could not load/process image:\n{e}")

def select_texture_img():
    global texture_img, depth_map
    path = filedialog.askopenfilename(
        title="Select Texture/Pattern Image", filetypes=[("Image files", "*.png;*.jpg;*.jpeg;*.bmp")])
    if not path: return
    try:
        if depth_map is not None:
            texture_img_loaded = load_and_resize_texture(path, depth_map.shape[1], depth_map.shape[0])
        else:
            temp_img = Image.open(path)
            texture_img_loaded = temp_img.convert('RGB')
        texture_img = texture_img_loaded
        status_label.config(text=f"Texture image loaded ({texture_img.width}×{texture_img.height})")
        update_preview()
    except Exception as e:
        messagebox.showerror("Image error", f"Could not load/process image:\n{e}")

def save_image():
    if current_sgram is None:
        messagebox.showinfo("Nothing to save", "Generate a stereogram first!")
        return
    outpath = filedialog.asksaveasfilename(defaultextension=".png")
    if outpath:
        current_sgram.save(outpath)
        status_label.config(text=f"Saved to {outpath.split('/')[-1]}.")

# App state
depth_map = None
texture_img = None
current_sgram = None

root = tk.Tk()
root.title("Magic Eye Stereogram Generator — Textured Edition")

mainframe = tk.Frame(root)
mainframe.pack(padx=14, pady=10, expand=True, fill='both')

tk.Label(mainframe, text="Step 1 — Select black-on-white depth map:").grid(row=0, column=0, sticky='w')
tk.Button(mainframe, text="Select Depth Map", command=select_depth_map).grid(row=0, column=1, sticky='ew')

tk.Label(mainframe, text="Step 2 — Select cartoon/pattern texture:").grid(row=1, column=0, sticky='w')
tk.Button(mainframe, text="Select Texture Image", command=select_texture_img).grid(row=1, column=1, sticky='ew')

tk.Label(mainframe, text="Step 3 — Adjust stereogram settings:").grid(row=2, column=0, sticky='w')
pattern_width = tk.IntVar(value=80)
tk.Label(mainframe, text="Pattern Width").grid(row=3, column=0)
tk.Scale(mainframe, from_=30, to=200, orient=tk.HORIZONTAL, variable=pattern_width, command=lambda _: update_preview()).grid(row=3, column=1, sticky='ew')
depth_strength = tk.IntVar(value=20)
tk.Label(mainframe, text="Depth Strength").grid(row=4, column=0)
tk.Scale(mainframe, from_=6, to=40, orient=tk.HORIZONTAL, variable=depth_strength, command=lambda _: update_preview()).grid(row=4, column=1, sticky='ew')

tk.Button(mainframe, text="Save Stereogram", command=save_image).grid(row=5, column=1, sticky='ew')

preview = tk.Label(root, bg="black")
preview.pack(pady=15)
status_label = tk.Label(root, text="Load depth map and texture to begin.", anchor='w', fg='navy')
status_label.pack(fill='x')

tk.Label(root, text="Instructions:\n"
    "• Use a black shape/word/object on white for depth map. Use ANY image (cartoon, abstract, etc.) for texture.\n"
    "• Adjust sliders for effect. Save as PNG. For best viewing: relax eyes, stare through image, or cross eyes until 3D shape appears."
    "\nOutput is similar to professional stereogram book illustrations, with your chosen background!\n",
    fg='mediumblue', wraplength=600, justify='left').pack(pady=(0,10))

root.mainloop()

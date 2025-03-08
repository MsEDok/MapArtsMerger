import os
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image


def convert_to_webp():
    file_paths = filedialog.askopenfilenames(title="Select image files",
                                             filetypes=[("Image files", "*.png;*.jpg;*.jpeg;*.bmp;*.tiff")])

    if not file_paths:
        return

    save_dir = filedialog.askdirectory(title="Select destination folder")
    if not save_dir:
        return

    for file_path in file_paths:
        try:
            img = Image.open(file_path)
            file_name = os.path.splitext(os.path.basename(file_path))[0] + ".webp"
            save_path = os.path.join(save_dir, file_name)
            img.save(save_path, "WEBP", lossless=True)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to convert {file_path}: {e}")

    messagebox.showinfo("Success", "All images have been converted to WebP (lossless).")


root = tk.Tk()
root.title("Image to WebP Converter")
root.geometry("200x100")

btn_select = tk.Button(root, text="Select Images & Convert", command=convert_to_webp, padx=10, pady=5)
btn_select.pack(pady=20)

root.mainloop()

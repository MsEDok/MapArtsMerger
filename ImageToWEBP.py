import os
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image
from concurrent.futures import ThreadPoolExecutor
import threading
import time

VERSION = "1.0.1"

class ImageConverterApp:
    def __init__(self, root):
        self.root = root
        self.root.title(f"Image to WebP Converter | V{VERSION}")
        self.root.geometry("300x150")

        self.btn_select = tk.Button(root, text="Select Images & Convert", command=self.convert_to_webp, padx=10, pady=5)
        self.btn_select.pack(pady=10)

        self.progress_label = tk.Label(root, text="0/0 images processed", font=("Arial", 12))
        self.progress_label.pack(pady=5)

        self.status_label = tk.Label(root, text="", font=("Arial", 10), fg="green")
        self.status_label.pack(pady=5)

        self.start_time = 0
        self.completed_count = 0
        self.num_files = 0
        self.lock = None

    def convert_to_webp(self):
        file_paths = filedialog.askopenfilenames(title="Select image files",
                                                 filetypes=[("Image files", "*.png;*.jpg;*.jpeg")])
        if not file_paths:
            return

        save_dir = filedialog.askdirectory(title="Select destination folder")
        if not save_dir:
            return

        self.num_files = len(file_paths)
        self.progress_label.config(text=f"0/{self.num_files} images processed")
        self.status_label.config(text="", fg="green")

        self.start_time = time.time()
        self.completed_count = 0
        self.lock = None

        def convert_image(file_path):
            try:
                img = Image.open(file_path)
                file_name = os.path.splitext(os.path.basename(file_path))[0] + ".webp"
                save_path = os.path.join(save_dir, file_name)

                icc_profile = img.info.get("icc_profile")

                if img.mode in ("P", "CMYK"):
                    img = img.convert("RGBA" if img.mode == "P" else "RGB")

                if img.format == "JPEG":
                    img.save(save_path, "webp", lossy=True, icc_profile=icc_profile)
                else:
                    img.save(save_path, "webp", lossless=True, icc_profile=icc_profile)

                with self.lock:
                    self.completed_count += 1
                    self.update_progress()

            except Exception as e:
                print(f"Error converting {file_path}: {e}")

        def run_conversion():
            self.lock = threading.Lock()
            max_workers = max(1, os.cpu_count() // 2)
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                executor.map(convert_image, file_paths)

            self.show_completion_message()

        threading.Thread(target=run_conversion, daemon=True).start()

    def update_progress(self):
        self.progress_label.config(text=f"{self.completed_count}/{self.num_files} images processed")

    def show_completion_message(self):
        total_time = int(time.time() - self.start_time)
        self.root.after(0, lambda: self.status_label.config(text=f"Conversion completed in {total_time} seconds!", fg="blue"))

root = tk.Tk()
app = ImageConverterApp(root)
root.mainloop()

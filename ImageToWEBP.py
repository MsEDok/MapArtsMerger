import os
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image
from concurrent.futures import ThreadPoolExecutor
import threading
import time


def convert_to_webp():
    file_paths = filedialog.askopenfilenames(title="Select image files",
                                             filetypes=[("Image files", "*.png;*.jpg;*.jpeg;*.bmp;*.tiff")])

    if not file_paths:
        return

    save_dir = filedialog.askdirectory(title="Select destination folder")
    if not save_dir:
        return

    progress_label.config(text=f"0/{len(file_paths)} images processed")
    time_label.config(text="Elapsed time: 0 seconds")

    remaining_files = list(file_paths)

    start_time = time.time()

    def convert_image(file_path):
        try:
            img = Image.open(file_path)
            file_name = os.path.splitext(os.path.basename(file_path))[0] + ".webp"
            save_path = os.path.join(save_dir, file_name)
            if img.format == "JPEG":
                img.save(save_path, "webp", lossy=True)
            else:
                img.save(save_path, "webp", lossless=True)

            remaining_files.remove(file_path)
            progress_label.config(text=f"{len(file_paths) - len(remaining_files)}/{len(file_paths)} images processed")

            elapsed_time = time.time() - start_time
            time_label.config(text=f"Elapsed time: {int(elapsed_time)} seconds")
            root.update_idletasks()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to convert {file_path}: {e}")

    def convert_images():
        max_workers = os.cpu_count() // 2

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [executor.submit(convert_image, file_path) for file_path in file_paths]
            for future in futures:
                future.result()

        total_time = time.time() - start_time
        messagebox.showinfo("Success", f"All images have been converted to WebP.\nTotal time: {int(total_time)} seconds.")

    threading.Thread(target=convert_images, daemon=True).start()


root = tk.Tk()
root.title("Image to WebP Converter")
root.geometry("300x150")

btn_select = tk.Button(root, text="Select Images & Convert", command=convert_to_webp, padx=10, pady=5)
btn_select.pack(pady=10)

progress_label = tk.Label(root, text="0/0 images processed", font=("Arial", 12))
progress_label.pack(pady=5)

time_label = tk.Label(root, text="Elapsed time: 0 seconds", font=("Arial", 10))
time_label.pack(pady=5)

root.mainloop()

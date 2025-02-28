import re
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk

VERSION = "1.0.0"

class ImageMerger:
    def __init__(self, root):
        self.preview_frame = None
        self.swap_button = None
        self.map_name_entry = None
        self.map_id_entry = None
        self.row_entry = None
        self.col_entry = None
        self.root = root
        self.images = []
        self.labels = []
        self.image_cache = {}
        self.selected_images = []
        self.swap_mode = False
        self.row_count = 0
        self.col_count = 0
        self.blank_image = None
        self.preview_size = 128
        self.setup_ui()

    def setup_ui(self):
        frame = tk.Frame(self.root)
        frame.pack(pady=10, padx=10, fill=tk.X)

        tk.Label(frame, text="Columns:").grid(row=0, column=0)
        self.col_entry = tk.Entry(frame)
        self.col_entry.grid(row=0, column=1)

        tk.Label(frame, text="Rows:").grid(row=1, column=0)
        self.row_entry = tk.Entry(frame)
        self.row_entry.grid(row=1, column=1)

        tk.Label(frame, text="MapID:").grid(row=2, column=0)
        self.map_id_entry = tk.Entry(frame)
        self.map_id_entry.grid(row=2, column=1)

        tk.Label(frame, text="MapName:").grid(row=3, column=0)
        self.map_name_entry = tk.Entry(frame)
        self.map_name_entry.grid(row=3, column=1)

        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=10)

        tk.Button(button_frame, text="Select Images", command=self.select_images).grid(row=0, column=0, padx=5, pady=5)
        self.swap_button = tk.Button(button_frame, text="Swap Mode: OFF", command=self.toggle_swap_mode)
        self.swap_button.grid(row=0, column=1, padx=5, pady=5)

        tk.Button(button_frame, text="Merge", command=self.merge_images).grid(row=0, column=2, padx=5, pady=5)

        self.preview_frame = tk.Frame(self.root)
        self.preview_frame.pack()

    @staticmethod
    def extract_number(filename):
        match = re.search(r"(\d+)", filename)
        return int(match.group(1)) if match else float("inf")

    def select_images(self):
        try:
            self.row_count = int(self.row_entry.get())
            self.col_count = int(self.col_entry.get())
            if self.row_count > 100 or self.col_count > 100:
                messagebox.showerror("Error", "Row and Column values are too large. Maximum allowed is 100.")
                return
        except ValueError:
            messagebox.showerror("Error", "Row and Column must be integers")
            return

        self.preview_size = min(800 // self.col_count, 800 // self.row_count, 256)
        self.blank_image = ImageTk.PhotoImage(Image.new("RGB", (self.preview_size, self.preview_size), "white"))

        max_images = self.row_count * self.col_count
        files = sorted(filedialog.askopenfilenames(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")]),
                       key=self.extract_number)

        if len(files) > max_images:
            messagebox.showerror("Error", f"You selected too many images. Maximum allowed: {max_images}")
            return

        self.images = files + [None] * (max_images - len(files))
        self.image_cache.clear()
        self.swap_mode = False
        self.update_preview()

    def load_image(self, img_path, size):
        if img_path in self.image_cache:
            return self.image_cache[img_path]

        if img_path:
            img = Image.open(img_path).resize((size, size))
            img_tk = ImageTk.PhotoImage(img)
            self.image_cache[img_path] = img_tk
            return img_tk

        return self.blank_image

    def update_preview(self):
        for widget in self.preview_frame.winfo_children():
            widget.destroy()

        self.labels.clear()

        for i, img_path in enumerate(self.images):
            img = self.load_image(img_path, self.preview_size)
            label = tk.Label(self.preview_frame, image=img, borderwidth=0, relief="solid", bg="white")
            label.image = img
            label.grid(row=i // self.col_count, column=i % self.col_count)
            label.bind("<Button-1>", lambda e, idx=i: self.handle_image_click(idx))
            self.labels.append(label)
        self.root.update_idletasks()

    def handle_image_click(self, idx):
        if self.swap_mode:
            if idx in self.selected_images:
                self.selected_images.remove(idx)
            else:
                self.selected_images.append(idx)

            if len(self.selected_images) == 2:
                self.swap_images()
        else:
            self.replace_image(idx)

    def replace_image(self, idx):
        file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")])
        if file_path:
            self.image_cache.pop(self.images[idx], None)
            self.images[idx] = file_path
            img = self.load_image(file_path, self.preview_size)
            self.labels[idx].config(image=img)
            self.labels[idx].image = img

    def toggle_swap_mode(self):
        self.swap_mode = not self.swap_mode
        self.selected_images.clear()
        self.swap_button.config(text=f"Swap Mode: {'ON' if self.swap_mode else 'OFF'}")

    def swap_images(self):
        if len(self.selected_images) == 2:
            idx1, idx2 = self.selected_images
            self.images[idx1], self.images[idx2] = self.images[idx2], self.images[idx1]

            img1 = self.load_image(self.images[idx1], self.preview_size)
            img2 = self.load_image(self.images[idx2], self.preview_size)

            self.labels[idx1].config(image=img1)
            self.labels[idx2].config(image=img2)
            self.labels[idx1].image = img1
            self.labels[idx2].image = img2

            self.selected_images.clear()

    def merge_images(self):
        if not any(self.images):
            messagebox.showerror("Error", "No images selected")
            return

        map_id = self.map_id_entry.get().strip()
        map_name = self.map_name_entry.get().strip().replace(" ", "_")

        if not map_id.isdigit():
            messagebox.showerror("Error", "MapID must be a number")
            return

        merged = Image.new("RGB", (self.col_count * 128, self.row_count * 128))
        for i, img_path in enumerate(self.images):
            img = Image.open(img_path).resize((128, 128)) if img_path else Image.new("RGB", (128, 128), "white")
            merged.paste(img, ((i % self.col_count) * 128, (i // self.col_count) * 128))

        save_path = filedialog.asksaveasfilename(defaultextension=".png",
                                                 filetypes=[("PNG files", "*.png")],
                                                 initialfile=f"[{map_id}]-{map_name}")
        if save_path:
            merged.save(save_path)
            messagebox.showinfo("Success", "Image merged successfully!")

def on_closing():
    merger.image_cache.clear()
    merger.images.clear()
    app.quit()
    app.destroy()
    exit(0)


if __name__ == "__main__":
    app = tk.Tk()
    app.title(f"Map Arts Merger V:{VERSION}")
    merger = ImageMerger(app)

    app.protocol("WM_DELETE_WINDOW", on_closing)
    app.mainloop()

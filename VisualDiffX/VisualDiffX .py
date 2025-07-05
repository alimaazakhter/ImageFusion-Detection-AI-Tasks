import os
import cv2
import numpy as np
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk
import threading
import webbrowser

# Always use this output directory
OUTPUT_DIR = 'task_2_output-images'
os.makedirs(OUTPUT_DIR, exist_ok=True)

# --- Change Detection Logic as a Function ---
def process_image_pair(before_path, after_path):
    before_img = cv2.imread(before_path)
    after_img = cv2.imread(after_path)
    before_gray = cv2.cvtColor(before_img, cv2.COLOR_BGR2GRAY)
    after_gray = cv2.cvtColor(after_img, cv2.COLOR_BGR2GRAY)
    diff = cv2.absdiff(before_gray, after_gray)
    _, thresh = cv2.threshold(diff, 30, 255, cv2.THRESH_BINARY)
    kernel = np.ones((5,5), np.uint8)
    thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
    thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    output_img = after_img.copy()
    for cnt in contours:
        if cv2.contourArea(cnt) > 100:
            x, y, w, h = cv2.boundingRect(cnt)
            cv2.rectangle(output_img, (x, y), (x+w, y+h), (0, 0, 255), 4)  # Bright red, thickness 4
    return before_img, after_img, output_img

# --- Tkinter GUI ---
class ChangeDetectionApp:
    def __init__(self, root):
        self.root = root
        self.root.title('Change Detection Tool')
        self.root.configure(bg='#ffffff')
        self.root.geometry('900x600')
        try:
            self.root.iconbitmap('icon.ico')
        except:
            pass
        self.input_dir = ''
        self.image_pairs = []
        self.current_index = 0
        self.images = (None, None, None)
        self.processing = False
        self.cancel_requested = False
        self.errors = 0

        # --- Simple Color Palette ---
        self.colors = {
            'bg': '#ffffff',
            'primary': '#1976d2',
            'secondary': '#757575',
            'accent': '#757575',
            'danger': '#d32f2f',
            'success': '#388e3c',
            'button_fg': 'white',
            'frame': '#f5f5f5',
            'label': '#222222',
            'status_info': '#222222',
            'status_success': '#388e3c',
            'status_error': '#d32f2f',
        }

        # --- Top Bar ---
        top_frame = tk.Frame(root, bg=self.colors['bg'])
        top_frame.pack(fill='x', pady=(10,0))
        instr = tk.Label(top_frame, text="Change Detection Tool", font=('Segoe UI', 16, 'bold'), bg=self.colors['bg'], fg=self.colors['primary'])
        instr.pack(side='top', pady=0, padx=0, expand=True)
        help_btn = tk.Button(top_frame, text='Help/About', command=self.show_help, bg=self.colors['secondary'], fg='white', font=('Segoe UI', 10), bd=0, activebackground='#616161', disabledforeground='white')
        help_btn.pack(side='right', padx=10)
        self.add_hover(help_btn, '#616161', self.colors['secondary'])

        # --- Instructions ---
        instr2 = tk.Label(root, text="1. Select your input folder. 2. Click 'Process Images'. 3. Browse results. Output is saved in 'task_2_output-images'.", justify='left', bg=self.colors['bg'], fg=self.colors['status_info'], font=('Segoe UI', 10))
        instr2.pack(pady=2)

        # --- Folder and Process Buttons ---
        btn_frame = tk.Frame(root, bg=self.colors['bg'])
        btn_frame.pack(pady=2)
        folder_btn = tk.Button(btn_frame, text='Select Folder', command=self.select_folder, bg=self.colors['primary'], fg=self.colors['button_fg'], font=('Segoe UI', 10), bd=0, activebackground='#115293', disabledforeground='white')
        folder_btn.pack(side='left', padx=5)
        self.add_hover(folder_btn, '#115293', self.colors['primary'])
        self.process_btn = tk.Button(btn_frame, text='Process Images', command=self.process_images, state='disabled', bg=self.colors['secondary'], fg='white', font=('Segoe UI', 10), bd=0, activebackground='#616161', disabledforeground='white')
        self.process_btn.pack(side='left', padx=5)
        self.add_hover(self.process_btn, '#616161', self.colors['secondary'])
        self.cancel_btn = tk.Button(btn_frame, text='Cancel', command=self.cancel_processing, state='disabled', bg=self.colors['danger'], fg='white', font=('Segoe UI', 10), bd=0, activebackground='#b71c1c', disabledforeground='white')
        self.cancel_btn.pack(side='left', padx=5)
        self.add_hover(self.cancel_btn, '#b71c1c', self.colors['danger'])

        # --- Progress Bar ---
        self.progress = ttk.Progressbar(root, orient='horizontal', length=400, mode='determinate')
        self.progress.pack(pady=5)

        # --- Image Display Section ---
        img_section = tk.Frame(root, bg=self.colors['frame'], bd=2, relief='groove')
        img_section.pack(pady=10, padx=10, fill='x')
        self.img_frame = tk.Frame(img_section, bg=self.colors['frame'])
        self.img_frame.pack(pady=5)
        # Create three vertical frames for image+label
        self.img_columns = []
        self.labels = []
        self.img_titles = []
        img_titles_text = ['Before', 'After', 'Detected Changes']
        for i in range(3):
            col = tk.Frame(self.img_frame, bg=self.colors['frame'])
            col.pack(side='left', padx=10)
            img_label = tk.Label(col, bg=self.colors['frame'])
            img_label.pack()
            title_label = tk.Label(col, text=img_titles_text[i], bg=self.colors['frame'], fg=self.colors['label'], font=('Segoe UI', 10))
            title_label.pack(pady=(8,0))
            self.img_columns.append(col)
            self.labels.append(img_label)
            self.img_titles.append(title_label)
        # Image counter
        self.counter = tk.Label(img_section, text='', bg=self.colors['frame'], fg=self.colors['primary'], font=('Segoe UI', 10))
        self.counter.pack(pady=(5,0))
        # Zoom button
        self.zoom_btn = tk.Button(img_section, text='Zoom Output', command=self.zoom_image, state='disabled', bg=self.colors['accent'], fg='white', font=('Segoe UI', 10), bd=0, activebackground='#616161', disabledforeground='white')
        self.zoom_btn.pack(pady=5)
        self.add_hover(self.zoom_btn, '#616161', self.colors['accent'])

        # --- Navigation ---
        nav_frame = tk.Frame(root, bg=self.colors['bg'])
        nav_frame.pack(pady=2)
        self.prev_btn = tk.Button(nav_frame, text='Prev', command=self.show_prev, state='disabled', bg=self.colors['accent'], fg='white', font=('Segoe UI', 10), bd=0, activebackground='#616161', disabledforeground='white')
        self.prev_btn.pack(side='left', padx=5)
        self.add_hover(self.prev_btn, '#616161', self.colors['accent'])
        self.next_btn = tk.Button(nav_frame, text='Next', command=self.show_next, state='disabled', bg=self.colors['accent'], fg='white', font=('Segoe UI', 10), bd=0, activebackground='#616161', disabledforeground='white')
        self.next_btn.pack(side='left', padx=5)
        self.add_hover(self.next_btn, '#616161', self.colors['accent'])

        # --- Status label ---
        self.status = tk.Label(root, text='', bg=self.colors['bg'], fg=self.colors['status_info'], font=('Segoe UI', 10))
        self.status.pack(pady=2)

        # --- Keyboard Shortcuts ---
        self.root.bind('<Left>', lambda e: self.show_prev())
        self.root.bind('<Right>', lambda e: self.show_next())

    def add_hover(self, widget, hover_bg, normal_bg):
        def on_enter(e): widget['bg'] = hover_bg
        def on_leave(e): widget['bg'] = normal_bg
        widget.bind('<Enter>', on_enter)
        widget.bind('<Leave>', on_leave)

    def show_status(self, msg, level='info'):
        color = {'info': self.colors['status_info'], 'success': self.colors['status_success'], 'error': self.colors['status_error']}.get(level, self.colors['status_info'])
        self.status.config(text=msg, fg=color)
    def clear_status(self):
        self.status.config(text='')

    def select_folder(self):
        folder = filedialog.askdirectory(title='Select Input Folder')
        if folder:
            self.input_dir = folder
            self.process_btn.config(state='normal')
            self.show_status(f'Selected: {self.input_dir}', 'info')
            self.image_pairs = self.get_image_pairs()
            self.current_index = 0
            self.prev_btn.config(state='disabled')
            self.next_btn.config(state='disabled')
            self.zoom_btn.config(state='disabled')
            self.counter.config(text='')
            for lbl in self.labels:
                lbl.config(image='')

    def get_image_pairs(self):
        files = [f for f in os.listdir(self.input_dir) if f.endswith('.jpg') and '~2' not in f]
        pairs = []
        for before in files:
            base = before[:-4]
            after = f'{base}~2.jpg'
            if os.path.exists(os.path.join(self.input_dir, after)):
                pairs.append((before, after))
        return pairs

    def process_images(self):
        if not self.image_pairs:
            self.show_status('No valid image pairs found!', 'error')
            messagebox.showerror('Error', 'No valid image pairs found!')
            return
        self.processing = True
        self.cancel_requested = False
        self.errors = 0
        self.progress['maximum'] = len(self.image_pairs)
        self.progress['value'] = 0
        self.show_status('Processing images...', 'info')
        self.cancel_btn.config(state='normal')
        self.process_btn.config(state='disabled')
        thread = threading.Thread(target=self._process_images_thread)
        thread.start()

    def _process_images_thread(self):
        for idx, (before, after) in enumerate(self.image_pairs):
            if self.cancel_requested:
                self.show_status('Processing cancelled.', 'error')
                self.processing = False
                self.cancel_btn.config(state='disabled')
                self.process_btn.config(state='normal')
                return
            try:
                before_path = os.path.join(self.input_dir, before)
                after_path = os.path.join(self.input_dir, after)
                before_img, after_img, output_img = process_image_pair(before_path, after_path)
                out_path = os.path.join(OUTPUT_DIR, after)
                cv2.imwrite(out_path, output_img)
            except Exception as e:
                self.errors += 1
                self.show_status(f'Error processing {before} & {after}: {e}', 'error')
            self.progress['value'] = idx + 1
            self.root.update()
        self.processing = False
        self.cancel_btn.config(state='disabled')
        self.process_btn.config(state='normal')
        summary = f"Processing complete! {len(self.image_pairs)} pairs processed."
        if self.errors:
            summary += f" {self.errors} errors."
        self.show_status(summary, 'success' if self.errors == 0 else 'error')
        self.current_index = 0
        self.show_images()
        if len(self.image_pairs) > 1:
            self.next_btn.config(state='normal')
        self.prev_btn.config(state='disabled')
        self.zoom_btn.config(state='normal')

    def cancel_processing(self):
        self.cancel_requested = True
        self.cancel_btn.config(state='disabled')
        self.show_status('Cancelling...', 'error')

    def show_images(self):
        if not self.image_pairs:
            return
        before, after = self.image_pairs[self.current_index]
        before_path = os.path.join(self.input_dir, before)
        after_path = os.path.join(self.input_dir, after)
        out_path = os.path.join(OUTPUT_DIR, after)
        try:
            imgs = []
            for path in [before_path, after_path, out_path]:
                img = cv2.imread(path)
                img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(img)
                img = img.resize((256, 256))
                imgs.append(ImageTk.PhotoImage(img))
            self.images = imgs
            for lbl, im in zip(self.labels, imgs):
                lbl.config(image=im)
                lbl.image = im
            self.counter.config(text=f'Image {self.current_index+1} of {len(self.image_pairs)}')
            self.zoom_btn.config(state='normal')
        except Exception as e:
            self.show_status(f'Error displaying images: {e}', 'error')

    def show_prev(self):
        if self.current_index > 0:
            self.current_index -= 1
            self.show_images()
            self.next_btn.config(state='normal')
        if self.current_index == 0:
            self.prev_btn.config(state='disabled')

    def show_next(self):
        if self.current_index < len(self.image_pairs) - 1:
            self.current_index += 1
            self.show_images()
            self.prev_btn.config(state='normal')
        if self.current_index == len(self.image_pairs) - 1:
            self.next_btn.config(state='disabled')

    def zoom_image(self):
        if not self.image_pairs:
            return
        before, after = self.image_pairs[self.current_index]
        out_path = os.path.join(OUTPUT_DIR, after)
        try:
            if os.name == 'nt':
                os.startfile(out_path)
            elif os.name == 'posix':
                opener = 'open' if sys.platform == 'darwin' else 'xdg-open'
                os.system(f'{opener} "{out_path}"')
        except Exception as e:
            self.show_status(f'Could not open image: {e}', 'error')

    def show_help(self):
        msg = (
            "Change Detection Tool\n\n"
            "1. Select a folder with before/after image pairs (e.g., '1.jpg' and '1~2.jpg').\n"
            "2. Click 'Process Images' to run change detection.\n"
            "3. Browse results with Prev/Next or arrow keys.\n"
            "4. Click 'Zoom Output' to view the detected changes image.\n"
            "5. Cancel processing anytime with the Cancel button.\n\n"
            "Output images are saved in the 'task_2_output-images' folder.\n\n"
            "Developed for your assessment.\n"
        )
        messagebox.showinfo('Help / About', msg)

if __name__ == '__main__':
    root = tk.Tk()
    app = ChangeDetectionApp(root)
    root.mainloop()

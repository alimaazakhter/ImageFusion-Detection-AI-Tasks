import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from tkinter import font as tkfont
import os
import glob
import cv2
import numpy as np
import threading

# Import align_images from rgboverlay.py
from rgboverlay import align_images

class OverlayApp:
    def __init__(self, root):
        self.root = root
        self.root.title('RGB-Thermal Image Overlay')
        self.root.geometry("550x650")

        # --- Style Configuration ---
        self.setup_styles()

        # --- Main Frame ---
        main_frame = ttk.Frame(root, style='App.TFrame')
        main_frame.pack(padx=20, pady=20, fill='both', expand=True)

        # --- Widget Creation ---
        self.create_widgets(main_frame)
        
        # --- Variables ---
        self.input_dir = ''
        self.output_dir = ''
        self.alpha = tk.DoubleVar(value=0.5)
        # Re-apply alpha to slider after it's created
        self.alpha_slider.set(self.alpha.get())

    def setup_styles(self):
        # --- Color Palette (Light Grey and Blue Theme) ---
        self.BG_COLOR = '#F0F0F0'
        self.TEXT_COLOR = '#333333'
        self.BUTTON_BG = '#0078D7'
        self.BUTTON_FG = '#FFFFFF'
        self.BUTTON_HOVER = '#005A9E'
        self.ACCENT_COLOR = '#0078D7' 
        self.WIDGET_BG = '#FFFFFF'
        self.WIDGET_BORDER = '#CCCCCC'

        self.root.configure(bg=self.BG_COLOR)
        
        # --- Font Definitions ---
        self.title_font = tkfont.Font(family='Segoe UI', size=18, weight='bold')
        self.label_font = tkfont.Font(family='Segoe UI', size=10)
        self.button_font = tkfont.Font(family='Segoe UI', size=11, weight='bold')

        # --- TTK Styling ---
        style = ttk.Style(self.root)
        style.theme_use('clam')

        # General Styles
        style.configure('.', background=self.BG_COLOR, foreground=self.TEXT_COLOR, font=self.label_font)
        style.configure('App.TFrame', background=self.BG_COLOR)
        style.configure('App.TLabel', background=self.BG_COLOR, foreground=self.TEXT_COLOR, font=self.label_font)
        style.configure('Title.TLabel', background=self.BG_COLOR, foreground=self.ACCENT_COLOR, font=self.title_font)
        
        # Button Styles
        style.configure('App.TButton',
                        font=self.button_font,
                        borderwidth=0,
                        focusthickness=0,
                        padding=12,
                        anchor='center')
        style.map('App.TButton',
                  foreground=[('!disabled', self.BUTTON_FG)],
                  background=[('!disabled', self.BUTTON_BG), ('hover', self.BUTTON_HOVER)])
        
        # Style for the disabled button, defined once
        style.configure('Disabled.TButton',
                        background='#BDBDBD',
                        foreground='#666666',
                        font=self.button_font,
                        padding=12)

        # Slider Style
        style.configure('Horizontal.TScale', background=self.BG_COLOR, troughcolor='#E0E0E0', borderwidth=0)
        style.map('Horizontal.TScale', background=[('active', self.BG_COLOR)])

        # Progress Bar Style (Green)
        style.configure('Green.Horizontal.TProgressbar',
                        troughcolor='#E0E0E0',
                        background='#4CAF50',  # Green
                        thickness=20)
    
    def create_widgets(self, parent):
        # --- App Title ---
        ttk.Label(parent, text="RGB-Thermal Overlay", style='Title.TLabel').pack(pady=(0, 10))

        # --- Progress Bar ---
        self.progress = ttk.Progressbar(parent, orient='horizontal', length=400, mode='determinate', style='Green.Horizontal.TProgressbar')
        self.progress.pack(pady=(0, 10), fill='x')

        # --- Input Folder ---
        ttk.Button(parent, text='Select Input Folder', command=self.select_input, style='App.TButton').pack(pady=(0, 3), fill='x')
        self.input_label = tk.Label(parent, text='No input folder selected', bg=self.WIDGET_BG, fg=self.TEXT_COLOR, font=self.label_font, relief=tk.SOLID, borderwidth=1, padx=10, anchor='w')
        self.input_label.pack(fill='x', ipady=6)

        # --- Output Folder ---
        ttk.Button(parent, text='Select Output Folder', command=self.select_output, style='App.TButton').pack(pady=(10, 3), fill='x')
        self.output_label = tk.Label(parent, text='No output folder selected', bg=self.WIDGET_BG, fg=self.TEXT_COLOR, font=self.label_font, relief=tk.SOLID, borderwidth=1, padx=10, anchor='w')
        self.output_label.pack(fill='x', ipady=6)

        # --- Alpha Slider ---
        ttk.Label(parent, text='Alpha (Blending)', style='App.TLabel').pack(pady=(10, 3))
        self.alpha_slider = ttk.Scale(parent, from_=0.0, to=1.0, orient='horizontal', style='Horizontal.TScale', command=lambda s: self.alpha.set(float(s)))
        self.alpha_slider.pack(fill='x', pady=(0, 6))

        # --- File Listbox ---
        ttk.Label(parent, text="Image Files to Process:", style='App.TLabel').pack(pady=(6, 3))
        listbox_frame = tk.Frame(parent, bd=1, relief=tk.SOLID, bg=self.WIDGET_BORDER)
        listbox_frame.pack(pady=3, fill='both', expand=True)
        self.file_listbox = tk.Listbox(listbox_frame, height=8, bg=self.WIDGET_BG, fg=self.TEXT_COLOR, font=self.label_font, relief=tk.FLAT, highlightthickness=0, selectbackground=self.ACCENT_COLOR)
        self.file_listbox.pack(side=tk.LEFT, fill='both', expand=True)
        
        scrollbar = ttk.Scrollbar(listbox_frame, orient='vertical', command=self.file_listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill='y')
        self.file_listbox.config(yscrollcommand=scrollbar.set)
        
        # --- Run Button ---
        self.run_button = tk.Button(
            parent,
            text='Run Overlay',
            font=self.button_font,
            bg=self.BUTTON_BG,
            fg=self.BUTTON_FG,
            relief=tk.FLAT,
            activebackground=self.BUTTON_HOVER,
            activeforeground=self.BUTTON_FG,
            command=self.start_processing_thread,
            state=tk.NORMAL,
            disabledforeground="#A0A0A0"
        )
        self.run_button.pack(pady=10, fill='x', ipady=6)
        
        # Manually bind hover events for tk.Button
        self.run_button.bind("<Enter>", self.on_enter_run_button)
        self.run_button.bind("<Leave>", self.on_leave_run_button)
        
        # --- Status Bar ---
        self.status_label = tk.Label(self.root, text="Ready", bg='#EAEAEA', fg=self.TEXT_COLOR, font=self.label_font, relief=tk.SUNKEN, anchor=tk.W, padx=10)
        self.status_label.pack(side=tk.BOTTOM, fill=tk.X, ipady=3)

    def on_enter_run_button(self, event):
        if self.run_button['state'] == tk.NORMAL:
            self.run_button.config(bg=self.BUTTON_HOVER)

    def on_leave_run_button(self, event):
        self.run_button.config(bg=self.BUTTON_BG)

    def select_input(self):
        folder = filedialog.askdirectory()
        if folder:
            self.input_dir = folder
            self.input_label.config(text=folder)
            self.file_listbox.delete(0, tk.END)
            thermal_images = glob.glob(os.path.join(self.input_dir, '*_T.JPG'))
            for img_path in sorted(thermal_images):
                self.file_listbox.insert(tk.END, os.path.basename(img_path))
            self.update_status(f"Found {len(thermal_images)} thermal images.")

    def select_output(self):
        folder = filedialog.askdirectory()
        if folder:
            self.output_dir = folder
            self.output_label.config(text=folder)

    def start_processing_thread(self):
        # Using state config for tk.Button
        self.run_button.config(state=tk.DISABLED)
        thread = threading.Thread(target=self.run_overlay)
        thread.start()

    def run_overlay(self):
        if not self.input_dir or not self.output_dir:
            messagebox.showerror('Error', 'Please select both input and output folders.')
            self.run_button.config(state=tk.NORMAL)
            return

        alpha = self.alpha.get()
        
        all_jpgs = glob.glob(os.path.join(self.input_dir, '*.JPG'))
        thermal_map = {}
        rgb_map = {}
        for img_path in all_jpgs:
            basename = os.path.basename(img_path)
            parts = basename.split('_')
            if len(parts) >= 3:
                seq_id = parts[-2]
                if basename.endswith('_T.JPG'):
                    thermal_map[seq_id] = img_path
                elif basename.endswith('_Z.JPG'):
                    rgb_map[seq_id] = img_path
        
        pairs_to_process = []
        for seq_id, thermal_path in sorted(thermal_map.items()):
            rgb_path = rgb_map.get(seq_id)
            if rgb_path:
                pairs_to_process.append((thermal_path, rgb_path))

        if not pairs_to_process:
            messagebox.showinfo("Info", "No valid image pairs found to process.")
            self.run_button.config(state=tk.NORMAL)
            return

        total_files = len(pairs_to_process)
        self.progress['maximum'] = total_files
        self.progress['value'] = 0
        
        processed_count = 0
        for i, (thermal_path, rgb_path) in enumerate(pairs_to_process):
            # Update status and redraw GUI before processing
            self.update_status(f"Processing {i+1}/{total_files}: {os.path.basename(thermal_path)}")
            self.root.update_idletasks()

            thermal_image = cv2.imread(thermal_path)
            rgb_image = cv2.imread(rgb_path)
            if thermal_image is None or rgb_image is None:
                continue
                
            aligned_thermal = align_images(rgb_image, thermal_image)
            if aligned_thermal is None:
                continue
                
            overlay = cv2.addWeighted(rgb_image, 1 - alpha, aligned_thermal, alpha, 0)
            output_filename = os.path.basename(thermal_path).replace('_T.JPG', '_AT.JPG')
            output_path = os.path.join(self.output_dir, output_filename)
            cv2.imwrite(output_path, overlay)
            processed_count += 1
            
            self.progress['value'] = i + 1

        self.update_status("Processing complete!")
        messagebox.showinfo("Done", "All images processed successfully!")
        self.progress['value'] = 0
        self.run_button.config(state=tk.NORMAL)

    def update_status(self, message):
        self.status_label.config(text=message)
        self.root.update_idletasks()

if __name__ == '__main__':
    root = tk.Tk()
    # Add window icon (replace 'logo.ico' with your icon file)
    try:
        root.iconbitmap('logo.ico')
    except tk.TclError:
        print("Icon 'logo.ico' not found. Skipping.")
    app = OverlayApp(root)
    root.mainloop()

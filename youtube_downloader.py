import tkinter as tk
from tkinter import ttk, filedialog
import yt_dlp
import os
import threading
import subprocess
import platform

class ModernYouTubeDownloader:
    def __init__(self, root):
        self.root = root
        self.root.title("YouTube Downloader")
        self.root.geometry("800x650")  # Increased initial size
        self.root.resizable(True, True)
        self.root.minsize(800, 650)    # Increased minimum size
        
        # Set color scheme - Red theme
        self.colors = {
            "primary": "#e63946",      # Red
            "primary_dark": "#c1121f", # Darker red for hover effects
            "secondary": "#f1faee",    # Off-white for contrast
            "accent": "#457b9d",       # Blue accent for secondary buttons
            "text": "#1d3557",         # Dark blue for text
            "light_text": "#6c757d",   # Lighter text for secondary info
            "success": "#2a9d8f",      # Teal for success
            "surface": "#ffffff",      # White for background
            "border": "#d3d3d3",       # Light gray for borders
        }
        
        # Apply system's native theme for better OS integration
        self.detect_and_set_theme()
        
        # Configure styles
        self.configure_styles()
        
        # Variables
        self.url_var = tk.StringVar()
        self.save_path_var = tk.StringVar()
        self.save_path_var.set(os.path.join(os.path.expanduser("~"), "Downloads"))
        self.format_var = tk.StringVar(value="MP4")
        # Add trace to format_var to update button appearance when changed
        self.format_var.trace_add("write", self.on_format_change)
        self.status_var = tk.StringVar(value="Ready to download")
        self.download_path = ""  # Store the download file path for opening later
        
        # Create UI
        self.create_widgets()
        
        # Configure proper window resize behavior
        self.configure_layout()
        
    def detect_and_set_theme(self):
        """Detect system and set appropriate theme base"""
        system = platform.system()
        available_themes = self.root.tk.call('ttk::themes')
        
        if system == "Windows" and 'vista' in available_themes:
            self.base_theme = 'vista'
        elif system == "Darwin" and 'aqua' in available_themes:  # macOS
            self.base_theme = 'aqua'
        elif 'clam' in available_themes:
            self.base_theme = 'clam'
        else:
            self.base_theme = 'default'
        
    def configure_styles(self):
        # Create custom styles for the application
        style = ttk.Style()
        
        # Use the detected base theme
        style.theme_use(self.base_theme)
        
        # Configure the TFrame
        style.configure("Main.TFrame", background=self.colors["surface"])
        style.configure("Header.TFrame", background=self.colors["primary"])
        style.configure("Content.TFrame", background=self.colors["surface"])
        
        # Configure the TLabel
        style.configure("TLabel", 
                       background=self.colors["surface"], 
                       foreground=self.colors["text"], 
                       font=("Segoe UI", 10))
        
        style.configure("Header.TLabel", 
                       background=self.colors["primary"], 
                       foreground="white", 
                       font=("Segoe UI", 22, "bold"))  # Increased font size
                       
        style.configure("Title.TLabel", 
                       background=self.colors["surface"], 
                       foreground=self.colors["primary"], 
                       font=("Segoe UI", 12, "bold"))
                       
        style.configure("Status.TLabel", 
                       background=self.colors["surface"], 
                       foreground=self.colors["light_text"], 
                       font=("Segoe UI", 9))
        
        # Configure the TEntry with rounded appearance (where supported)
        style.configure("TEntry", 
                       fieldbackground=self.colors["secondary"],
                       borderwidth=1,
                       relief="solid",
                       padding=10)  # Increased padding
        
        # Configure the TButton
        style.configure("TButton", 
                       background=self.colors["accent"],
                       foreground=self.colors["text"],
                       borderwidth=0,
                       focusthickness=0,
                       focuscolor="none",
                       padding=10,
                       font=("Segoe UI", 10))
                       
        style.map("TButton",
                background=[("active", self.colors["accent"])],
                relief=[("pressed", "solid")])
        
        # Configure accent buttons (with primary red color)
        style.configure("Accent.TButton", 
                       background=self.colors["primary"],
                       foreground="white",
                       borderwidth=0,
                       focusthickness=0,
                       padding=12,  # Increased padding
                       font=("Segoe UI", 12, "bold"))
                       
        style.map("Accent.TButton",
                background=[("active", self.colors["primary_dark"])],  # Darker red on hover
                relief=[("pressed", "solid")])
                
        # Configure success buttons (green)
        style.configure("Success.TButton", 
                       background=self.colors["success"],
                       foreground="white",
                       borderwidth=0,
                       focusthickness=0,
                       padding=12,
                       font=("Segoe UI", 12, "bold"))
                       
        style.map("Success.TButton",
                background=[("active", "#218777")],  # Darker green on hover
                relief=[("pressed", "solid")])
                
        # Configure the TRadiobutton with custom indicator
        style.configure("TRadiobutton", 
                       background=self.colors["surface"],
                       foreground=self.colors["text"],
                       font=("Segoe UI", 10))
                       
        style.map("TRadiobutton",
                background=[("active", self.colors["surface"])],
                indicatorcolor=[("selected", self.colors["primary"])])
                       
        # Configure the TProgressbar
        style.configure("TProgressbar", 
                       troughcolor=self.colors["secondary"],
                       background=self.colors["primary"],
                       borderwidth=0,
                       thickness=18)  # Thicker progress bar
    
    def configure_layout(self):
        # Make sure content frame expands properly
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(1, weight=1)  # Header is row 0, content is row 1
        
    def create_widgets(self):
        # Main container
        main_frame = ttk.Frame(self.root, style="Main.TFrame")
        main_frame.pack(fill="both", expand=True)
        
        # Header Frame with gradient effect (using Canvas)
        header_height = 80
        header_canvas = tk.Canvas(main_frame, height=header_height, bg=self.colors["primary"], 
                               highlightthickness=0)
        header_canvas.pack(fill="x", pady=0)
        
        # Add subtle gradient effect to header
        for i in range(header_height):
            # Create gradient from primary to slightly darker primary
            r_ratio = (header_height - i) / header_height
            color_val = self.calculate_gradient_color(self.colors["primary"], self.colors["primary_dark"], r_ratio)
            header_canvas.create_line(0, i, 2000, i, fill=color_val)
            
        # Header Label
        header_label = tk.Label(header_canvas, 
                             text="YouTube Downloader", 
                             bg=self.colors["primary"],
                             fg="white",
                             font=("Segoe UI", 22, "bold"))
        header_canvas.create_window(40, header_height//2, anchor="w", window=header_label)
        
        # Add a small logo/icon (substitute with a real icon if available)
        logo_text = tk.Label(header_canvas, 
                          text="▶", 
                          bg=self.colors["primary"],
                          fg="white",
                          font=("Arial", 24, "bold"))
        header_canvas.create_window(20, header_height//2, anchor="w", window=logo_text)
        
        # Content Frame with padding and shadow effect
        content_container = ttk.Frame(main_frame, style="Main.TFrame")
        content_container.pack(fill="both", expand=True)
        
        # Add shadow effect around content panel
        content_frame = tk.Frame(content_container, 
                               bg=self.colors["surface"], 
                               bd=1, 
                               relief="solid",
                               highlightbackground=self.colors["border"],
                               highlightthickness=1)
        content_frame.pack(fill="both", expand=True, padx=40, pady=30)
        
        # URL Section
        url_frame = tk.Frame(content_frame, bg=self.colors["surface"])
        url_frame.pack(fill="x", padx=30, pady=(20, 0))
        
        url_label = tk.Label(url_frame, 
                          text="Video URL", 
                          bg=self.colors["surface"],
                          fg=self.colors["primary"],
                          font=("Segoe UI", 12, "bold"))
        url_label.pack(anchor="w", pady=(0, 8))
        
        url_entry_frame = tk.Frame(url_frame, bg=self.colors["surface"], bd=1, relief="solid")
        url_entry_frame.pack(fill="x", pady=(0, 20))
        
        url_entry = tk.Entry(url_entry_frame, 
                          textvariable=self.url_var,
                          font=("Segoe UI", 11),
                          bg=self.colors["secondary"],
                          relief="flat",
                          bd=0,
                          highlightthickness=0)
        url_entry.pack(fill="x", expand=True, ipady=10, padx=10)
        
        # Save Location Section
        save_frame = tk.Frame(content_frame, bg=self.colors["surface"])
        save_frame.pack(fill="x", padx=30, pady=(0, 0))
        
        save_label = tk.Label(save_frame, 
                           text="Save Location", 
                           bg=self.colors["surface"],
                           fg=self.colors["primary"],
                           font=("Segoe UI", 12, "bold"))
        save_label.pack(anchor="w", pady=(0, 8))
        
        path_frame = tk.Frame(save_frame, bg=self.colors["surface"])
        path_frame.pack(fill="x", pady=(0, 20))
        
        save_entry_frame = tk.Frame(path_frame, bg=self.colors["surface"], bd=1, relief="solid")
        save_entry_frame.pack(side="left", fill="x", expand=True)
        
        save_entry = tk.Entry(save_entry_frame, 
                           textvariable=self.save_path_var,
                           font=("Segoe UI", 11),
                           bg=self.colors["secondary"],
                           relief="flat",
                           bd=0,
                           highlightthickness=0)
        save_entry.pack(fill="x", expand=True, ipady=10, padx=10)
        
        browse_button = tk.Button(path_frame, 
                               text="Browse", 
                               command=self.browse_directory,
                               font=("Segoe UI", 10),
                               bg=self.colors["accent"],
                               fg="white",
                               bd=0,
                               padx=15,
                               pady=8,
                               cursor="hand2")
        browse_button.pack(side="right", padx=(10, 0))
        
        # Format Selection with better visual design
        format_frame = tk.Frame(content_frame, bg=self.colors["surface"])
        format_frame.pack(fill="x", padx=30, pady=(0, 0))
        
        format_label = tk.Label(format_frame, 
                             text="Format", 
                             bg=self.colors["surface"],
                             fg=self.colors["primary"],
                             font=("Segoe UI", 12, "bold"))
        format_label.pack(anchor="w", pady=(0, 8))
        
        # Format selection with card-style options
        format_options_frame = tk.Frame(format_frame, bg=self.colors["surface"])
        format_options_frame.pack(fill="x", pady=(0, 20))

        # MP4 Button (replace the card and radio button)
        mp4_button = tk.Button(
            format_options_frame,
            text="MP4 Video",
            font=("Segoe UI", 11, "bold"),
            bg=self.colors["primary"],
            fg="white",
            activebackground=self.colors["primary_dark"],
            activeforeground="white",
            bd=0,
            padx=25,
            pady=10,
            cursor="hand2",
            command=lambda: self.format_var.set("MP4")
        )
        mp4_button.pack(side="left", padx=(0, 15))

        # MP3 Button (replace the card and radio button)
        mp3_button = tk.Button(
            format_options_frame,
            text="MP3 Audio",
            font=("Segoe UI", 11, "bold"),
            bg=self.colors["primary"],
            fg="white",
            activebackground=self.colors["primary_dark"],
            activeforeground="white",
            bd=0,
            padx=25,
            pady=10,
            cursor="hand2",
            command=lambda: self.format_var.set("MP3")
        )
        mp3_button.pack(side="left")

        # Add hover effects
        mp4_button.bind("<Enter>", lambda e: e.widget.config(bg=self.colors["primary_dark"]))
        mp4_button.bind("<Leave>", lambda e: self.update_format_button_color(e.widget, "MP4"))
        mp3_button.bind("<Enter>", lambda e: e.widget.config(bg=self.colors["primary_dark"]))
        mp3_button.bind("<Leave>", lambda e: self.update_format_button_color(e.widget, "MP3"))

        # Store these buttons as class attributes so we can reference them later
        self.mp4_button = mp4_button
        self.mp3_button = mp3_button

        # Update initial button states based on the default format selection
        self.update_format_button_color(mp4_button, "MP4")
        self.update_format_button_color(mp3_button, "MP3")
        # Progress Section with improved visual design
        progress_frame = tk.Frame(content_frame, bg=self.colors["surface"])
        progress_frame.pack(fill="x", padx=30, pady=(0, 0))
        
        progress_label = tk.Label(progress_frame, 
                               text="Download Progress", 
                               bg=self.colors["surface"],
                               fg=self.colors["primary"],
                               font=("Segoe UI", 12, "bold"))
        progress_label.pack(anchor="w", pady=(0, 8))
        
        # Progress bar with rounded corners effect
        progress_container = tk.Frame(progress_frame, bg=self.colors["surface"], bd=0)
        progress_container.pack(fill="x", pady=(0, 5))
        
        self.progress = ttk.Progressbar(progress_container, 
                                      orient="horizontal", 
                                      mode="determinate", 
                                      style="TProgressbar")
        self.progress.pack(fill="x", ipady=3)  # Increased padding for larger progress bar
        
        # Status Label with icon
        status_frame = tk.Frame(progress_frame, bg=self.colors["surface"])
        status_frame.pack(fill="x", anchor="w", pady=(5, 20))
        
        self.status_icon = tk.Label(status_frame, 
                                 text="ℹ️", 
                                 bg=self.colors["surface"],
                                 font=("Segoe UI", 9))
        self.status_icon.pack(side="left", padx=(0, 5))
        
        self.status_label = tk.Label(status_frame, 
                                  textvariable=self.status_var, 
                                  bg=self.colors["surface"],
                                  fg=self.colors["light_text"],
                                  font=("Segoe UI", 9))
        self.status_label.pack(side="left")
        
        # Download Button - Larger and more prominent
        button_frame = tk.Frame(content_frame, bg=self.colors["surface"])
        button_frame.pack(fill="x", padx=30, pady=(10, 20))
        
        self.download_button = tk.Button(
            button_frame, 
            text="Download", 
            command=self.start_download,
            font=("Segoe UI", 12, "bold"),
            bg=self.colors["primary"],
            fg="white",
            activebackground=self.colors["primary_dark"],
            activeforeground="white",
            bd=0,
            padx=20,
            pady=12,
            cursor="hand2"
        )
        self.download_button.pack(fill="x")
        
        # Add hover effect for download button
        self.download_button.bind("<Enter>", lambda e: e.widget.config(bg=self.colors["primary_dark"]))
        self.download_button.bind("<Leave>", lambda e: e.widget.config(bg=self.colors["primary"]))
    
    def calculate_gradient_color(self, start_color, end_color, ratio):
        """Calculate gradient color between two hex colors"""
        # Convert hex to RGB
        start_r = int(start_color[1:3], 16)
        start_g = int(start_color[3:5], 16)
        start_b = int(start_color[5:7], 16)
        
        end_r = int(end_color[1:3], 16)
        end_g = int(end_color[3:5], 16)
        end_b = int(end_color[5:7], 16)
        
        # Calculate the color at the given ratio
        r = int(start_r * ratio + end_r * (1 - ratio))
        g = int(start_g * ratio + end_g * (1 - ratio))
        b = int(start_b * ratio + end_b * (1 - ratio))
        
        # Convert back to hex
        return f'#{r:02x}{g:02x}{b:02x}'
    
    def browse_directory(self):
        directory = filedialog.askdirectory()
        if directory:
            self.save_path_var.set(directory)
    
    def start_download(self):
        url = self.url_var.get().strip()
        if not url:
            self.show_error("Please enter a YouTube URL")
            return
        
        # Validate YouTube URL
        if not self.is_valid_youtube_url(url):
            self.show_error("Please enter a valid YouTube URL")
            return
            
        # Reset the progress bar
        self.progress["value"] = 0
        
        # Update status icon for download
        self.status_icon.config(text="🔄")
        
        # Disable download button during download
        self.download_button.config(state="disabled")
        
        # Start download in a separate thread to keep UI responsive
        download_thread = threading.Thread(target=self.download_video)
        download_thread.daemon = True
        download_thread.start()
    
    def is_valid_youtube_url(self, url):
        """Basic validation for YouTube URLs"""
        return ("youtube.com" in url or "youtu.be" in url) and "://" in url
    
    def download_progress_hook(self, d):
        if d['status'] == 'downloading':
            # Calculate and update the progress
            if 'total_bytes' in d and d['total_bytes'] > 0:
                percent = (d['downloaded_bytes'] / d['total_bytes']) * 100
                self.root.after(0, self.update_progress, percent)
                
                # Update status with downloaded size and speed
                downloaded = self.format_size(d['downloaded_bytes'])
                total = self.format_size(d['total_bytes'])
                speed = d.get('speed', 0)
                if speed:
                    speed_str = self.format_size(speed) + "/s"
                    status_text = f"Downloading: {downloaded} of {total} ({speed_str})"
                else:
                    status_text = f"Downloading: {downloaded} of {total}"
                
                self.root.after(0, self.update_status, status_text, "🔄")
            else:
                # If total_bytes is not available, show indeterminate progress
                status_text = f"Downloading... {d.get('_percent_str', '')}"
                self.root.after(0, self.update_status, status_text, "🔄")
                
        elif d['status'] == 'finished':
            self.root.after(0, self.update_status, "Download complete, processing file...", "✓")
    
    def format_size(self, bytes_size):
        """Convert bytes to a human-readable format"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if bytes_size < 1024.0:
                return f"{bytes_size:.2f} {unit}"
            bytes_size /= 1024.0
        return f"{bytes_size:.2f} TB"
    
    def update_progress(self, percentage):
        self.progress["value"] = percentage
        self.root.update_idletasks()
    
    def update_status(self, status_text, icon="ℹ️"):
        self.status_var.set(status_text)
        self.status_icon.config(text=icon)
        self.root.update_idletasks()
    
    def download_video(self):
        url = self.url_var.get()
        save_path = self.save_path_var.get()
        format_choice = self.format_var.get()
        
        try:
            self.update_status("Preparing to download...", "🔄")
            
            if format_choice == "MP4":
                ydl_opts = {
                    'format': 'best',  # Best quality that includes video and audio
                    'outtmpl': os.path.join(save_path, '%(title)s.%(ext)s'),
                    'progress_hooks': [self.download_progress_hook],
                }
            else:  # MP3 - but actually just download audio in its native format
                ydl_opts = {
                    'format': 'bestaudio/best',
                    'outtmpl': os.path.join(save_path, '%(title)s.%(ext)s'),
                    'progress_hooks': [self.download_progress_hook],
                }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                
                # Get the downloaded file path
                if 'entries' in info:  # Playlist
                    video = info['entries'][0]
                else:
                    video = info
                    
                # Get the actual filepath where the video was saved
                filename = ydl.prepare_filename(video)
                if format_choice == "MP3":
                    base, _ = os.path.splitext(filename)
                    filename = base + ".mp3"
                
                # Store the downloaded file path for later use
                self.download_path = filename
                
                # Update UI after download complete
                self.root.after(0, self.download_complete, filename)
                
        except Exception as e:
            self.root.after(0, self.show_error, str(e))
        finally:
            # Re-enable download button
            self.root.after(0, self.reset_download_button)

    def update_format_button_color(self, button, format_type):
        """Update the format button colors based on selection"""
        selected = self.format_var.get() == format_type
        if selected:
            button.config(bg=self.colors["primary_dark"])
        else:
            button.config(bg=self.colors["primary"])

    def reset_download_button(self):
        self.download_button.config(state="normal")
    
    def download_complete(self, file_path):
        # Set progress to 100%
        self.progress["value"] = 100
        
        # Update status
        self.update_status("Download completed successfully!", "✓")
        
        # Create a custom dialog with an option to open file location
        self.show_completion_dialog(file_path)
    
    def show_completion_dialog(self, file_path):
        # Create custom dialog
        dialog = tk.Toplevel(self.root)
        dialog.title("Download Complete")
        dialog.geometry("500x400") 
        dialog.resizable(False, False)
        dialog.transient(self.root)  # Set as transient to main window
        dialog.grab_set()  # Make dialog modal
        
        # Configure dialog
        dialog.configure(background=self.colors["surface"])
        
        # Add success icon (unicode checkmark in a circle)
        success_frame = tk.Frame(dialog, bg=self.colors["success"], padx=20, pady=20)
        success_frame.pack(fill="x")
        
        success_label = tk.Label(success_frame, 
                              text="✓", 
                              font=("Segoe UI", 36), 
                              foreground="white",
                              background=self.colors["success"])
        success_label.pack(pady=(10, 10))
        
        # Add content frame
        content_frame = tk.Frame(dialog, bg=self.colors["surface"], padx=30, pady=20)
        content_frame.pack(fill="both", expand=True)
        
        # Add success message
        message_label = tk.Label(content_frame, 
                              text="Your download has completed successfully!", 
                              font=("Segoe UI", 14, "bold"),
                              foreground=self.colors["text"],
                              background=self.colors["surface"])
        message_label.pack(pady=(10, 15))
        
        # Add file path with icon
        file_frame = tk.Frame(content_frame, bg=self.colors["surface"])
        file_frame.pack(fill="x", pady=(0, 15))
        
        file_icon = tk.Label(file_frame,
                          text="📁",
                          font=("Segoe UI", 12),
                          foreground=self.colors["accent"],
                          background=self.colors["surface"])
        file_icon.pack(side=tk.LEFT, padx=(0, 5))
        
        # Add file path (shortened if too long)
        path_display = file_path
        if len(path_display) > 50:
            # Shorten the path for display
            path_parts = path_display.split(os.sep)
            if len(path_parts) > 3:
                path_display = os.path.join(path_parts[0], "...", path_parts[-1])
        
        file_label = tk.Label(file_frame, 
                           text=path_display, 
                           font=("Segoe UI", 10),
                           foreground=self.colors["light_text"],
                           background=self.colors["surface"],
                           anchor="w")
        file_label.pack(side=tk.LEFT, fill="x")
        
        # Create button frame
        button_frame = tk.Frame(content_frame, background=self.colors["surface"])
        button_frame.pack(fill="x", pady=15)
        
        # Add buttons
        open_folder_button = tk.Button(
            button_frame, 
            text="Open File Location", 
            command=lambda: self.open_file_location(file_path),
            font=("Segoe UI", 11),
            background=self.colors["primary"],
            foreground="white",
            activebackground=self.colors["primary_dark"],
            activeforeground="white",
            borderwidth=0,
            padx=15,
            pady=10,
            cursor="hand2"
        )
        open_folder_button.pack(side=tk.LEFT, padx=5, fill="x", expand=True)
        
        ok_button = tk.Button(
            button_frame, 
            text="OK", 
            command=dialog.destroy,
            font=("Segoe UI", 11),
            background=self.colors["secondary"],
            foreground=self.colors["text"],
            activebackground="#e6e6e6",
            activeforeground=self.colors["text"],
            borderwidth=0,
            padx=15,
            pady=10,
            cursor="hand2"
        )
        ok_button.pack(side=tk.RIGHT, padx=5, fill="x", expand=True)
        
        # Add hover effects
        open_folder_button.bind("<Enter>", lambda e: e.widget.config(bg=self.colors["primary_dark"]))
        open_folder_button.bind("<Leave>", lambda e: e.widget.config(bg=self.colors["primary"]))
        
        ok_button.bind("<Enter>", lambda e: e.widget.config(bg="#e6e6e6"))
        ok_button.bind("<Leave>", lambda e: e.widget.config(bg=self.colors["secondary"]))
        
        # Center the dialog on the main window
        self.center_window(dialog, self.root)
        
        # Reset progress bar after dialog is closed
        dialog.protocol("WM_DELETE_WINDOW", lambda: [dialog.destroy(), self.reset_progress()])
    
    def reset_progress(self):
        # Reset progress bar to 0
        self.progress["value"] = 0
    
    def open_file_location(self, file_path):
        """Open the file explorer/finder at the location of the downloaded file"""
        file_dir = os.path.dirname(os.path.abspath(file_path))
        
        try:
            if platform.system() == "Windows":
                # Windows - use explorer to open and select the file
                subprocess.Popen(f'explorer /select,"{file_path}"')
            elif platform.system() == "Darwin":  # macOS
                subprocess.Popen(["open", file_dir])
            else:  # Linux
                subprocess.Popen(["xdg-open", file_dir])
        except Exception as e:
            self.show_error(f"Could not open file location: {str(e)}")

    def on_format_change(self, *args):
        """Handle format selection change"""
        # Update button colors when format changes
        if hasattr(self, 'mp4_button') and hasattr(self, 'mp3_button'):
            self.update_format_button_color(self.mp4_button, "MP4")
            self.update_format_button_color(self.mp3_button, "MP3")

    def center_window(self, window, parent):
        """Center a window relative to its parent"""
        parent.update_idletasks()
        window.update_idletasks()
        
        # Calculate position
        parent_width = parent.winfo_width()
        parent_height = parent.winfo_height()
        parent_x = parent.winfo_rootx()
        parent_y = parent.winfo_rooty()
        
        window_width = window.winfo_width()
        window_height = window.winfo_height()
        
        x = parent_x + (parent_width - window_width) // 2
        y = parent_y + (parent_height - window_height) // 2
        
        # Set position
        window.geometry(f"+{x}+{y}")
    
    def show_error(self, error_msg):
        """Show an error message with improved styling"""
        self.update_status("Error occurred", "❌")
        dialog = tk.Toplevel(self.root)
        dialog.title("Error")
        dialog.geometry("500x250")
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.configure(background=self.colors["surface"])
        
        # Error header
        error_frame = tk.Frame(dialog, bg=self.colors["accent"], padx=20, pady=15)
        error_frame.pack(fill="x")
        
        error_label = tk.Label(error_frame, 
                             text="❌", 
                             font=("Segoe UI", 28), 
                             foreground="white",
                             background=self.colors["accent"])
        error_label.pack(pady=(5, 5))
        
        # Error content
        content_frame = tk.Frame(dialog, bg=self.colors["surface"], padx=30, pady=20)
        content_frame.pack(fill="both", expand=True)
        
        # Error message
        message_label = tk.Label(content_frame, 
                               text="An error occurred", 
                               font=("Segoe UI", 14, "bold"),
                               foreground=self.colors["text"],
                               background=self.colors["surface"])
        message_label.pack(pady=(10, 15))
        
        # Error details
        details_frame = tk.Frame(content_frame, bg=self.colors["secondary"], bd=1, relief="solid", padx=15, pady=15)
        details_frame.pack(fill="x", padx=5, pady=(0, 15))
        
        details_label = tk.Label(details_frame, 
                              text=error_msg, 
                              font=("Segoe UI", 10),
                              foreground=self.colors["text"],
                              background=self.colors["secondary"],
                              wraplength=400,
                              justify="left")
        details_label.pack(pady=0)
        
        # OK Button
        ok_button = tk.Button(
            content_frame, 
            text="OK", 
            command=dialog.destroy,
            font=("Segoe UI", 11),
            background=self.colors["primary"],
            foreground="white",
            activebackground=self.colors["primary_dark"],
            activeforeground="white",
            borderwidth=0,
            padx=20,
            pady=8,
            cursor="hand2"
        )
        ok_button.pack(pady=5)
        
        # Add hover effect
        ok_button.bind("<Enter>", lambda e: e.widget.config(bg=self.colors["primary_dark"]))
        ok_button.bind("<Leave>", lambda e: e.widget.config(bg=self.colors["primary"]))
        
        # Center the dialog
        self.center_window(dialog, self.root)
        
        # Re-enable download button if disabled
        self.reset_download_button()

if __name__ == "__main__":
    root = tk.Tk()
    app = ModernYouTubeDownloader(root)
    
    # Center on screen
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = (screen_width - 800) // 2
    y = (screen_height - 650) // 2
    root.geometry(f"800x650+{x}+{y}")
    
    root.mainloop()
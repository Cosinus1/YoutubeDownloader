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
        self.root.geometry("750x500")
        self.root.resizable(True, True)
        self.root.minsize(750, 500)
        
        # Set color scheme
        self.colors = {
            "primary": "#4a6fd4",       # Blue
            "secondary": "#f3f6fb",     # Light gray-blue
            "accent": "#ff5c5c",        # Coral red for buttons
            "text": "#333333",          # Dark gray for text
            "light_text": "#6c757d",    # Lighter text for secondary info
            "success": "#28a745",       # Green for success
            "surface": "#ffffff",       # White for background
        }
        
        # Configure styles
        self.configure_styles()
        
        # Variables
        self.url_var = tk.StringVar()
        self.save_path_var = tk.StringVar()
        self.save_path_var.set(os.path.join(os.path.expanduser("~"), "Downloads"))
        self.format_var = tk.StringVar(value="MP4")
        self.status_var = tk.StringVar(value="Ready to download")
        self.download_path = ""  # Store the download file path for opening later
        
        # Create UI
        self.create_widgets()
        
    def configure_styles(self):
        # Create custom styles for the application
        style = ttk.Style()
        
        # Configure the main theme
        style.theme_use("clam")  # Use clam as base theme (works well for customization)
        
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
                       font=("Segoe UI", 18, "bold"))
                       
        style.configure("Title.TLabel", 
                       background=self.colors["surface"], 
                       foreground=self.colors["primary"], 
                       font=("Segoe UI", 12, "bold"))
                       
        style.configure("Status.TLabel", 
                       background=self.colors["surface"], 
                       foreground=self.colors["light_text"], 
                       font=("Segoe UI", 9))
        
        # Configure the TEntry
        style.configure("TEntry", 
                       fieldbackground=self.colors["secondary"],
                       borderwidth=1,
                       relief="solid",
                       padding=8)
        
        # Configure the TButton
        style.configure("TButton", 
                       background=self.colors["secondary"],
                       foreground=self.colors["text"],
                       borderwidth=0,
                       focusthickness=0,
                       focuscolor="none",
                       padding=8,
                       font=("Segoe UI", 10))
                       
        style.map("TButton",
                background=[("active", self.colors["secondary"])],
                relief=[("pressed", "solid")])
        
        # Configure accent buttons
        style.configure("Accent.TButton", 
                       background=self.colors["accent"],
                       foreground="white",
                       borderwidth=0,
                       focusthickness=0,
                       padding=10,
                       font=("Segoe UI", 12, "bold"))
                       
        style.map("Accent.TButton",
                background=[("active", "#ff7a7a")],  # Lighter red on hover
                relief=[("pressed", "solid")])
                
        # Configure the TRadiobutton
        style.configure("TRadiobutton", 
                       background=self.colors["surface"],
                       foreground=self.colors["text"],
                       font=("Segoe UI", 10))
                       
        # Configure the TProgressbar
        style.configure("TProgressbar", 
                       troughcolor=self.colors["secondary"],
                       background=self.colors["primary"],
                       borderwidth=0,
                       thickness=16)
    
    def create_widgets(self):
        # Main container
        main_frame = ttk.Frame(self.root, style="Main.TFrame")
        main_frame.pack(fill="both", expand=True)
        
        # Header Frame
        header_frame = ttk.Frame(main_frame, style="Header.TFrame")
        header_frame.pack(fill="x", pady=0)
        
        # Header Label
        header_label = ttk.Label(header_frame, 
                                text="YouTube Downloader", 
                                style="Header.TLabel")
        header_label.pack(pady=20, padx=30, anchor="w")
        
        # Content Frame with padding
        content_frame = ttk.Frame(main_frame, style="Content.TFrame")
        content_frame.pack(fill="both", expand=True, padx=40, pady=30)
        
        # URL Section
        url_label = ttk.Label(content_frame, text="Video URL", style="Title.TLabel")
        url_label.pack(anchor="w", pady=(0, 8))
        
        url_entry = ttk.Entry(content_frame, textvariable=self.url_var, style="TEntry")
        url_entry.pack(fill="x", pady=(0, 20))
        
        # Save Location Section
        save_label = ttk.Label(content_frame, text="Save Location", style="Title.TLabel")
        save_label.pack(anchor="w", pady=(0, 8))
        
        path_frame = ttk.Frame(content_frame, style="Content.TFrame")
        path_frame.pack(fill="x", pady=(0, 20))
        
        save_entry = ttk.Entry(path_frame, textvariable=self.save_path_var, style="TEntry")
        save_entry.pack(side="left", fill="x", expand=True)
        
        browse_button = ttk.Button(path_frame, text="Browse", command=self.browse_directory)
        browse_button.pack(side="right", padx=(10, 0))
        
        # Format Selection
        format_label = ttk.Label(content_frame, text="Format", style="Title.TLabel")
        format_label.pack(anchor="w", pady=(0, 8))
        
        format_frame = ttk.Frame(content_frame, style="Content.TFrame")
        format_frame.pack(fill="x", pady=(0, 20))
        
        mp4_radio = ttk.Radiobutton(format_frame, 
                                   text="MP4 Video", 
                                   value="MP4", 
                                   variable=self.format_var)
        mp4_radio.pack(side="left", padx=(0, 30))
        
        mp3_radio = ttk.Radiobutton(format_frame, 
                                   text="MP3 Audio", 
                                   value="MP3", 
                                   variable=self.format_var)
        mp3_radio.pack(side="left")
        
        # Progress Section
        progress_label = ttk.Label(content_frame, text="Download Progress", style="Title.TLabel")
        progress_label.pack(anchor="w", pady=(0, 8))
        
        self.progress = ttk.Progressbar(content_frame, orient="horizontal", mode="determinate", style="TProgressbar")
        self.progress.pack(fill="x", pady=(0, 5))
        
        # Status Label
        self.status_label = ttk.Label(content_frame, textvariable=self.status_var, style="Status.TLabel")
        self.status_label.pack(anchor="w", pady=(0, 20))
        
        # Download Button
        button_frame = ttk.Frame(content_frame, style="Content.TFrame")
        button_frame.pack(fill="x", pady=(10, 0))
        
        self.download_button = ttk.Button(button_frame, 
                                       text="Download", 
                                       command=self.start_download, 
                                       style="Accent.TButton")
        self.download_button.pack(pady=10)
        
        # Make content_frame's columns expandable
        content_frame.columnconfigure(0, weight=1)
    
    def browse_directory(self):
        directory = filedialog.askdirectory()
        if directory:
            self.save_path_var.set(directory)
    
    def start_download(self):
        url = self.url_var.get().strip()
        if not url:
            self.show_error("Please enter a YouTube URL")
            return
        
        # Reset the progress bar
        self.progress["value"] = 0
        
        # Disable download button during download
        self.download_button.config(state="disabled")
        
        # Start download in a separate thread to keep UI responsive
        download_thread = threading.Thread(target=self.download_video)
        download_thread.daemon = True
        download_thread.start()
    
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
                
                self.root.after(0, self.update_status, status_text)
            else:
                # If total_bytes is not available, show indeterminate progress
                status_text = f"Downloading... {d.get('_percent_str', '')}"
                self.root.after(0, self.update_status, status_text)
                
        elif d['status'] == 'finished':
            self.root.after(0, self.update_status, "Download complete, processing file...")
    
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
    
    def update_status(self, status_text):
        self.status_var.set(status_text)
        self.root.update_idletasks()
    
    def download_video(self):
        url = self.url_var.get()
        save_path = self.save_path_var.get()
        format_choice = self.format_var.get()
        
        try:
            self.update_status("Preparing to download...")
            
            if format_choice == "MP4":
                ydl_opts = {
                    'format': 'best',  # Best quality that includes video and audio
                    'outtmpl': os.path.join(save_path, '%(title)s.%(ext)s'),
                    'progress_hooks': [self.download_progress_hook],
                }
            else:  # MP3 - audio format
                ydl_opts = {
                    'format': 'bestaudio/best',
                    'outtmpl': os.path.join(save_path, '%(title)s.%(ext)s'),
                    'progress_hooks': [self.download_progress_hook],
                    # If ffmpeg is available, you can uncomment below:
                    # 'postprocessors': [{
                    #     'key': 'FFmpegExtractAudio',
                    #     'preferredcodec': 'mp3',
                    #     'preferredquality': '192',
                    # }],
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
                
                # Store the downloaded file path for later use
                self.download_path = filename
                
                # Update UI after download complete
                self.root.after(0, self.download_complete, filename)
                
        except Exception as e:
            self.root.after(0, self.show_error, str(e))
        finally:
            # Re-enable download button
            self.root.after(0, self.reset_download_button)
    
    def reset_download_button(self):
        self.download_button.config(state="normal")
    
    def download_complete(self, file_path):
        # Set progress to 100%
        self.progress["value"] = 100
        
        # Update status
        self.status_var.set("Download completed successfully!")
        
        # Create a custom dialog with an option to open file location
        self.show_completion_dialog(file_path)
    
    def show_completion_dialog(self, file_path):
        # Create custom dialog
        dialog = tk.Toplevel(self.root)
        dialog.title("Download Complete")
        dialog.geometry("450x200")
        dialog.resizable(False, False)
        dialog.transient(self.root)  # Set as transient to main window
        dialog.grab_set()  # Make dialog modal
        
        # Configure dialog
        dialog.configure(background=self.colors["surface"])
        
        # Add success icon (unicode checkmark in a circle)
        success_label = tk.Label(dialog, 
                              text="✓", 
                              font=("Segoe UI", 36), 
                              foreground=self.colors["success"],
                              background=self.colors["surface"])
        success_label.pack(pady=(20, 10))
        
        # Add success message
        message_label = tk.Label(dialog, 
                              text="Your download has completed successfully!", 
                              font=("Segoe UI", 12, "bold"),
                              foreground=self.colors["text"],
                              background=self.colors["surface"])
        message_label.pack(pady=(0, 5))
        
        # Add file path (shortened if too long)
        path_display = file_path
        if len(path_display) > 50:
            # Shorten the path for display
            path_parts = path_display.split(os.sep)
            if len(path_parts) > 3:
                path_display = os.path.join(path_parts[0], "...", path_parts[-1])
        
        file_label = tk.Label(dialog, 
                           text=path_display, 
                           font=("Segoe UI", 9),
                           foreground=self.colors["light_text"],
                           background=self.colors["surface"])
        file_label.pack(pady=(0, 15))
        
        # Create button frame
        button_frame = tk.Frame(dialog, background=self.colors["surface"])
        button_frame.pack(fill="x", padx=20, pady=10)
        
        # Add buttons
        open_folder_button = tk.Button(
            button_frame, 
            text="Open File Location", 
            command=lambda: self.open_file_location(file_path),
            font=("Segoe UI", 10),
            background=self.colors["primary"],
            foreground="white",
            borderwidth=0,
            padx=15,
            pady=8,
            cursor="hand2"
        )
        open_folder_button.pack(side=tk.LEFT, padx=5)
        
        ok_button = tk.Button(
            button_frame, 
            text="OK", 
            command=dialog.destroy,
            font=("Segoe UI", 10),
            background=self.colors["secondary"],
            foreground=self.colors["text"],
            borderwidth=0,
            padx=15,
            pady=8,
            cursor="hand2"
        )
        ok_button.pack(side=tk.RIGHT, padx=5)
        
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
        """Show an error message"""
        self.status_var.set("Error occurred")
        dialog = tk.Toplevel(self.root)
        dialog.title("Error")
        dialog.geometry("400x200")
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.configure(background=self.colors["surface"])
        
        # Error icon
        error_label = tk.Label(dialog, 
                             text="✗", 
                             font=("Segoe UI", 36), 
                             foreground=self.colors["accent"],
                             background=self.colors["surface"])
        error_label.pack(pady=(20, 10))
        
        # Error message
        message_label = tk.Label(dialog, 
                               text="An error occurred", 
                               font=("Segoe UI", 12, "bold"),
                               foreground=self.colors["text"],
                               background=self.colors["surface"])
        message_label.pack(pady=(0, 5))
        
        # Error details
        details_label = tk.Label(dialog, 
                              text=error_msg, 
                              font=("Segoe UI", 9),
                              foreground=self.colors["light_text"],
                              background=self.colors["surface"],
                              wraplength=350)
        details_label.pack(pady=(0, 15))
        
        # OK Button
        ok_button = tk.Button(
            dialog, 
            text="OK", 
            command=dialog.destroy,
            font=("Segoe UI", 10),
            background=self.colors["secondary"],
            foreground=self.colors["text"],
            borderwidth=0,
            padx=15,
            pady=8
        )
        ok_button.pack(pady=(0, 20))
        
        # Center the dialog
        self.center_window(dialog, self.root)
        
        # Re-enable download button if disabled
        self.reset_download_button()

if __name__ == "__main__":
    root = tk.Tk()
    app = ModernYouTubeDownloader(root)
    root.mainloop()
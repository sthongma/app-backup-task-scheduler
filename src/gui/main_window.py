"""
Main GUI for Backup Application (CustomTkinter)
- Select Input/Output folders
- Backup Now button
- Real-time Log display
"""

import customtkinter as ctk
from tkinter import filedialog, messagebox
import sys
import os
from pathlib import Path
import threading

# Add path for importing modules
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.utils.logger import get_logger
from src.utils.log_manager import LogManager, format_bytes
from src.core.config_manager import ConfigManager
from src.core.backup_engine import BackupEngine


class BackupApp(ctk.CTk):
    """Backup Application GUI"""

    def __init__(self):
        super().__init__()

        # Window settings
        self.title("File Backup Application")
        self.geometry("850x650")

        # Set defaults
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # Create instances
        self.logger = get_logger()
        self.log_manager = LogManager()
        self.config_manager = ConfigManager()
        self.backup_engine = BackupEngine(self.logger)

        # Variables
        self.input_path = ctk.StringVar(value=self.config_manager.get('backup.input_path', ''))
        self.output_path = ctk.StringVar(value=self.config_manager.get('backup.output_path', ''))
        self.is_backing_up = False

        # Create UI
        self.create_ui()

        # Load settings
        self.load_settings()

        # Run log maintenance
        self.run_log_maintenance()

        # Protocol for window closing
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def create_ui(self):
        """Create UI"""

        # ========== Main Content Container ==========
        main_container = ctk.CTkFrame(self, corner_radius=10)
        main_container.pack(fill="both", expand=True, padx=18, pady=18)

        # ========== Top Bar (Theme, Clear Log, Exit) ==========
        top_bar_frame = ctk.CTkFrame(main_container, fg_color="transparent")
        top_bar_frame.pack(fill="x", padx=12, pady=(12, 8))

        # Theme Toggle
        theme_btn = ctk.CTkButton(
            top_bar_frame,
            text="🌓 Theme",
            width=100,
            height=28,
            font=ctk.CTkFont(size=12),
            fg_color=("#3b8ed0", "#1f6aa5"),
            hover_color=("#2d6da8", "#144870"),
            command=self.toggle_theme
        )
        theme_btn.pack(side="left", padx=3)

        # Clear Log
        clear_log_btn = ctk.CTkButton(
            top_bar_frame,
            text="🗑️ Clear",
            width=100,
            height=28,
            font=ctk.CTkFont(size=12),
            fg_color=("gray70", "gray30"),
            hover_color=("gray60", "gray25"),
            command=self.clear_log
        )
        clear_log_btn.pack(side="left", padx=3)

        # Exit
        exit_btn = ctk.CTkButton(
            top_bar_frame,
            text="✖ Exit",
            width=80,
            height=28,
            font=ctk.CTkFont(size=12),
            fg_color=("gray60", "gray20"),
            hover_color=("gray50", "gray15"),
            command=self.on_closing
        )
        exit_btn.pack(side="right", padx=3)

        # ========== Folder Selection ==========
        folder_frame = ctk.CTkFrame(main_container, corner_radius=8)
        folder_frame.pack(fill="x", padx=15, pady=8)

        # Input Folder
        input_label = ctk.CTkLabel(folder_frame, text="Source:", font=ctk.CTkFont(size=13, weight="bold"))
        input_label.grid(row=0, column=0, sticky="w", padx=12, pady=(12, 4))

        input_entry = ctk.CTkEntry(folder_frame, textvariable=self.input_path, height=32, font=ctk.CTkFont(size=12))
        input_entry.grid(row=1, column=0, padx=12, pady=(0, 8), sticky="ew")

        input_btn = ctk.CTkButton(
            folder_frame,
            text="📁 Browse",
            width=110,
            height=32,
            font=ctk.CTkFont(size=12),
            fg_color=("#3b8ed0", "#1f6aa5"),
            hover_color=("#2d6da8", "#144870"),
            command=self.select_input_folder
        )
        input_btn.grid(row=1, column=1, padx=(8, 12), pady=(0, 8))

        # Output Folder
        output_label = ctk.CTkLabel(folder_frame, text="Destination:", font=ctk.CTkFont(size=13, weight="bold"))
        output_label.grid(row=2, column=0, sticky="w", padx=12, pady=(8, 4))

        output_entry = ctk.CTkEntry(folder_frame, textvariable=self.output_path, height=32, font=ctk.CTkFont(size=12))
        output_entry.grid(row=3, column=0, padx=12, pady=(0, 12), sticky="ew")

        output_btn = ctk.CTkButton(
            folder_frame,
            text="📁 Browse",
            width=110,
            height=32,
            font=ctk.CTkFont(size=12),
            fg_color=("#3b8ed0", "#1f6aa5"),
            hover_color=("#2d6da8", "#144870"),
            command=self.select_output_folder
        )
        output_btn.grid(row=3, column=1, padx=(8, 12), pady=(0, 12))

        folder_frame.columnconfigure(0, weight=1)

        # ========== Backup Now Button ==========
        backup_btn_frame = ctk.CTkFrame(main_container, corner_radius=8)
        backup_btn_frame.pack(fill="x", padx=15, pady=8)

        self.backup_now_btn = ctk.CTkButton(
            backup_btn_frame,
            text="⚡ Backup Now",
            font=ctk.CTkFont(size=16, weight="bold"),
            height=45,
            corner_radius=6,
            fg_color=("#3b8ed0", "#1f6aa5"),
            hover_color=("#2d6da8", "#144870"),
            command=self.backup_now
        )
        self.backup_now_btn.pack(fill="x", padx=12, pady=12)

        # ========== Log Display ==========
        log_frame = ctk.CTkFrame(main_container, corner_radius=8)
        log_frame.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        log_label = ctk.CTkLabel(log_frame, text="📋 Log:", font=ctk.CTkFont(size=13, weight="bold"))
        log_label.pack(anchor="w", padx=12, pady=(12, 5))

        self.log_textbox = ctk.CTkTextbox(log_frame, height=180, wrap="word", corner_radius=6, font=ctk.CTkFont(size=11))
        self.log_textbox.pack(fill="both", expand=True, padx=12, pady=(0, 12))

    def select_input_folder(self):
        """Select source folder"""
        folder = filedialog.askdirectory(title="Select Source Folder")
        if folder:
            self.input_path.set(folder)
            self.log(f"Selected source folder: {folder}")

    def select_output_folder(self):
        """Select destination folder"""
        folder = filedialog.askdirectory(title="Select Destination Folder")
        if folder:
            self.output_path.set(folder)
            self.log(f"Selected destination folder: {folder}")

    def backup_now(self):
        """Backup now"""
        if self.is_backing_up:
            messagebox.showwarning("Warning", "Backup is already in progress")
            return

        input_path = self.input_path.get()
        output_path = self.output_path.get()

        if not input_path or not output_path:
            messagebox.showerror("Error", "Please select both source and destination folders")
            return

        # Run in separate thread
        self.is_backing_up = True
        self.backup_now_btn.configure(state="disabled", text="Backing up...")
        thread = threading.Thread(target=self._run_backup, args=(input_path, output_path), daemon=True)
        thread.start()

    def _run_backup(self, input_path, output_path):
        """Run backup (called from thread)"""
        try:
            # Set callback
            self.backup_engine.set_progress_callback(self.update_progress)

            # Run backup
            result = self.backup_engine.backup(input_path, output_path)

            # Show result
            if result['success']:
                self.after(0, lambda: messagebox.showinfo(
                    "Success",
                    f"Backup completed successfully\n\n"
                    f"Files copied: {result['copied_files']:,}\n"
                    f"Time elapsed: {result['elapsed_time']:.2f} seconds"
                ))

                # Update last backup time
                self.config_manager.update_last_backup()
                # Save paths
                self.config_manager.set_backup_settings(input_path, output_path)
                self.config_manager.save_config()

            else:
                self.after(0, lambda: messagebox.showerror(
                    "Error",
                    f"Error occurred: {result.get('error', 'Unknown error')}"
                ))

        finally:
            self.is_backing_up = False
            self.after(0, lambda: self.backup_now_btn.configure(state="normal", text="⚡ Backup Now"))

    def update_progress(self, current, total, message):
        """Update progress (called from backup engine)"""
        self.after(0, lambda: self.log(message))

    def load_settings(self):
        """Load settings"""
        self.log("Settings loaded successfully")

    def run_log_maintenance(self):
        """Run log maintenance"""
        try:
            retention_days = self.config_manager.get('logs.retention_days', 30)
            self.log_manager.retention_days = retention_days

            result = self.log_manager.run_maintenance()

            if result['deleted_logs'] > 0:
                self.log(f"Deleted old log files: {result['deleted_logs']} files ({format_bytes(result['deleted_bytes'])})")

        except Exception as e:
            self.log(f"Error in log maintenance: {e}")

    def log(self, message):
        """Display log in textbox"""
        self.log_textbox.insert("end", f"{message}\n")
        self.log_textbox.see("end")

    def clear_log(self):
        """Clear log textbox"""
        self.log_textbox.delete("0.0", "end")

    def toggle_theme(self):
        """Toggle theme"""
        current_mode = ctk.get_appearance_mode()
        new_mode = "Light" if current_mode == "Dark" else "Dark"
        ctk.set_appearance_mode(new_mode)
        self.config_manager.set_ui_theme(new_mode.lower())
        self.config_manager.save_config()

    def on_closing(self):
        """Close application"""
        self.destroy()


def main():
    """Start application"""
    app = BackupApp()
    app.mainloop()


if __name__ == "__main__":
    main()

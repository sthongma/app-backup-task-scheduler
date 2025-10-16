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
        self.geometry("800x700")

        # Set defaults
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # Create instances
        self.logger = get_logger()
        self.log_manager = LogManager()
        self.config_manager = ConfigManager()
        self.backup_engine = BackupEngine(self.logger)

        # Variables
        self.input_paths = self.config_manager.get('backup.input_paths', [])
        self.output_path = ctk.StringVar(value=self.config_manager.get('backup.output_path', ''))
        self.is_backing_up = False
        self.folder_items = []  # Track folder UI items for removal

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

        # ========== Folder Selection ==========
        folder_frame = ctk.CTkFrame(main_container, corner_radius=8)
        folder_frame.pack(fill="both", expand=True, padx=15, pady=8)

        # ===== Source Folders Section =====
        source_header = ctk.CTkFrame(folder_frame, fg_color="transparent")
        source_header.pack(fill="x", padx=12, pady=(10, 6))

        source_label = ctk.CTkLabel(source_header, text="Source Folders:", font=ctk.CTkFont(size=13, weight="bold"))
        source_label.pack(side="left")

        # Add Folder Button
        add_btn = ctk.CTkButton(
            source_header,
            text="➕ Add",
            width=80,
            height=26,
            font=ctk.CTkFont(size=11),
            fg_color=("#3b8ed0", "#1f6aa5"),
            hover_color=("#2d6da8", "#144870"),
            command=self.add_input_folder
        )
        add_btn.pack(side="right", padx=3)

        # Clear All Button
        clear_all_btn = ctk.CTkButton(
            source_header,
            text="🗑️ Clear",
            width=80,
            height=26,
            font=ctk.CTkFont(size=11),
            fg_color=("gray70", "gray30"),
            hover_color=("gray60", "gray25"),
            command=self.clear_all_folders
        )
        clear_all_btn.pack(side="right", padx=3)

        # Scrollable Frame for Folder List
        self.folders_scroll = ctk.CTkScrollableFrame(folder_frame, height=60, corner_radius=6)
        self.folders_scroll.pack(fill="both", expand=True, padx=12, pady=(0, 8))

        # Load existing folders
        self.refresh_folder_list()

        # ===== Destination Folder Section =====
        dest_separator = ctk.CTkFrame(folder_frame, height=2, fg_color=("gray70", "gray30"))
        dest_separator.pack(fill="x", padx=12, pady=6)

        output_label = ctk.CTkLabel(folder_frame, text="Destination:", font=ctk.CTkFont(size=13, weight="bold"))
        output_label.pack(anchor="w", padx=12, pady=(6, 4))

        dest_frame = ctk.CTkFrame(folder_frame, fg_color="transparent")
        dest_frame.pack(fill="x", padx=12, pady=(0, 10))

        output_entry = ctk.CTkEntry(dest_frame, textvariable=self.output_path, height=32, font=ctk.CTkFont(size=12))
        output_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))

        output_btn = ctk.CTkButton(
            dest_frame,
            text="📁 Browse",
            width=110,
            height=30,
            font=ctk.CTkFont(size=12),
            fg_color=("#3b8ed0", "#1f6aa5"),
            hover_color=("#2d6da8", "#144870"),
            command=self.select_output_folder
        )
        output_btn.pack(side="right")

        # ========== Backup Now Button ==========
        backup_btn_frame = ctk.CTkFrame(main_container, corner_radius=8)
        backup_btn_frame.pack(fill="x", padx=15, pady=8)

        self.backup_now_btn = ctk.CTkButton(
            backup_btn_frame,
            text="⚡ Backup Now",
            font=ctk.CTkFont(size=16, weight="bold"),
            height=35,
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

    def add_input_folder(self):
        """Add source folder"""
        folder = filedialog.askdirectory(title="Select Source Folder to Add")
        if folder:
            if folder not in self.input_paths:
                self.input_paths.append(folder)
                self.config_manager.add_input_path(folder)
                self.config_manager.save_config()
                self.refresh_folder_list()
                self.log(f"Added source folder: {folder}")
            else:
                messagebox.showinfo("Info", "This folder is already in the list")

    def remove_input_folder(self, folder_path):
        """Remove source folder"""
        if folder_path in self.input_paths:
            # Show confirmation dialog
            folder_name = Path(folder_path).name
            if messagebox.askyesno(
                "Confirm Removal",
                f"Remove this folder from the list?\n\n📁 {folder_name}\n\nPath: {folder_path}"
            ):
                self.input_paths.remove(folder_path)
                self.config_manager.remove_input_path(folder_path)
                self.config_manager.save_config()
                self.refresh_folder_list()
                self.log(f"Removed source folder: {folder_path}")

    def clear_all_folders(self):
        """Clear all source folders"""
        if len(self.input_paths) == 0:
            messagebox.showinfo("Info", "No folders to clear")
            return

        if messagebox.askyesno("Confirm", f"Remove all {len(self.input_paths)} source folder(s)?"):
            self.input_paths.clear()
            self.config_manager.clear_input_paths()
            self.config_manager.save_config()
            self.refresh_folder_list()
            self.log("Cleared all source folders")

    def refresh_folder_list(self):
        """Refresh the folder list display"""
        # Clear existing items
        for widget in self.folders_scroll.winfo_children():
            widget.destroy()
        self.folder_items.clear()

        # Add folders
        if len(self.input_paths) == 0:
            empty_label = ctk.CTkLabel(
                self.folders_scroll,
                text="No folders added yet. Click '➕ Add' to add folders.",
                font=ctk.CTkFont(size=11),
                text_color="gray"
            )
            empty_label.pack(pady=10)
        else:
            for folder_path in self.input_paths:
                self.add_folder_item(folder_path)

    def add_folder_item(self, folder_path):
        """Add a folder item to the list"""
        item_frame = ctk.CTkFrame(self.folders_scroll, corner_radius=6, height=32)
        item_frame.pack(fill="x", padx=5, pady=2)

        # Folder icon and path
        path_label = ctk.CTkLabel(
            item_frame,
            text=f"📁 {folder_path}",
            font=ctk.CTkFont(size=11),
            anchor="w"
        )
        path_label.pack(side="left", fill="x", expand=True, padx=10, pady=6)

        # Remove button
        remove_btn = ctk.CTkButton(
            item_frame,
            text="✖",
            width=28,
            height=28,
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color=("gray70", "gray30"),
            hover_color=("#e74c3c", "#c0392b"),
            command=lambda: self.remove_input_folder(folder_path)
        )
        remove_btn.pack(side="right", padx=6, pady=4)

        self.folder_items.append(item_frame)

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

        output_path = self.output_path.get()

        if len(self.input_paths) == 0:
            messagebox.showerror("Error", "Please add at least one source folder")
            return

        if not output_path:
            messagebox.showerror("Error", "Please select destination folder")
            return

        # Run in separate thread
        self.is_backing_up = True
        self.backup_now_btn.configure(state="disabled", text="Backing up...")
        thread = threading.Thread(target=self._run_backup, args=(self.input_paths, output_path), daemon=True)
        thread.start()

    def _run_backup(self, input_paths, output_path):
        """Run backup (called from thread)"""
        try:
            # Set callback
            self.backup_engine.set_progress_callback(self.update_progress)

            # Run multi-folder backup
            result = self.backup_engine.backup_multiple(input_paths, output_path)

            # Show result
            if result['success']:
                self.after(0, lambda: messagebox.showinfo(
                    "Success",
                    f"Backup completed successfully\n\n"
                    f"Total folders: {result['total_folders']}\n"
                    f"Successful: {result['successful']}\n"
                    f"Time elapsed: {result['elapsed_time']:.2f} seconds"
                ))

                # Update last backup time
                self.config_manager.update_last_backup()
                # Save paths
                self.config_manager.set_backup_settings(input_paths, output_path)
                self.config_manager.save_config()

            else:
                failed_count = result['failed']
                self.after(0, lambda: messagebox.showerror(
                    "Error",
                    f"Backup completed with errors\n\n"
                    f"Total folders: {result['total_folders']}\n"
                    f"Successful: {result['successful']}\n"
                    f"Failed: {failed_count}\n\n"
                    f"Check logs for details"
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

    def on_closing(self):
        """Close application"""
        self.destroy()


def main():
    """Start application"""
    app = BackupApp()
    app.mainloop()


if __name__ == "__main__":
    main()

"""
GUI หลักสำหรับแอพพลิเคชัน Backup (CustomTkinter)
- เลือก Input/Output folders
- ปุ่มคัดลอกทันที
- ตั้งค่า Auto Backup Schedule
- แสดง Log real-time
"""

import customtkinter as ctk
from tkinter import filedialog, messagebox
import sys
import os
from pathlib import Path
import threading

# เพิ่ม path สำหรับ import modules
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.utils.logger import get_logger
from src.utils.log_manager import LogManager, format_bytes
from src.core.config_manager import ConfigManager
from src.core.backup_engine import BackupEngine
from src.core.scheduler import BackupScheduler


class BackupApp(ctk.CTk):
    """แอพพลิเคชัน Backup GUI"""

    def __init__(self):
        super().__init__()

        # Window settings
        self.title("File Backup Scheduler - Automatic Backup System")
        self.geometry("900x700")

        # กำหนดค่าเริ่มต้น
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # สร้าง instances
        self.logger = get_logger()
        self.log_manager = LogManager()
        self.config_manager = ConfigManager()
        self.backup_engine = BackupEngine(self.logger)
        self.scheduler = BackupScheduler(self.logger)

        # ตัวแปร
        self.input_path = ctk.StringVar(value=self.config_manager.get('backup.input_path', ''))
        self.output_path = ctk.StringVar(value=self.config_manager.get('backup.output_path', ''))
        self.schedule_mode = ctk.StringVar(value=self.config_manager.get('schedule.mode', 'off'))
        self.custom_interval = ctk.IntVar(value=self.config_manager.get('schedule.custom_interval_minutes', 60))
        self.is_backing_up = False

        # สร้าง UI
        self.create_ui()

        # โหลดการตั้งค่า
        self.load_settings()

        # รัน log maintenance
        self.run_log_maintenance()

        # ตั้งค่า backup function สำหรับ scheduler
        self.scheduler.set_backup_function(self.run_scheduled_backup)

        # Protocol สำหรับปิดหน้าต่าง
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def create_ui(self):
        """สร้าง UI"""

        # ========== Header ==========
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=(20, 10))

        title_label = ctk.CTkLabel(
            header_frame,
            text="Automatic Backup System",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack()

        # ========== Folder Selection ==========
        folder_frame = ctk.CTkFrame(self)
        folder_frame.pack(fill="x", padx=20, pady=10)

        # Input Folder
        input_label = ctk.CTkLabel(folder_frame, text="Source Folder:", font=ctk.CTkFont(size=14, weight="bold"))
        input_label.grid(row=0, column=0, sticky="w", padx=10, pady=(10, 5))

        input_entry = ctk.CTkEntry(folder_frame, textvariable=self.input_path, width=500)
        input_entry.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="ew")

        input_btn = ctk.CTkButton(
            folder_frame,
            text="Browse",
            width=150,
            command=self.select_input_folder
        )
        input_btn.grid(row=1, column=1, padx=10, pady=(0, 10))

        # Output Folder
        output_label = ctk.CTkLabel(folder_frame, text="Destination Folder:", font=ctk.CTkFont(size=14, weight="bold"))
        output_label.grid(row=2, column=0, sticky="w", padx=10, pady=(10, 5))

        output_entry = ctk.CTkEntry(folder_frame, textvariable=self.output_path, width=500)
        output_entry.grid(row=3, column=0, padx=10, pady=(0, 10), sticky="ew")

        output_btn = ctk.CTkButton(
            folder_frame,
            text="Browse",
            width=150,
            command=self.select_output_folder
        )
        output_btn.grid(row=3, column=1, padx=10, pady=(0, 10))

        folder_frame.columnconfigure(0, weight=1)

        # ========== Backup Now Button ==========
        backup_now_frame = ctk.CTkFrame(self, fg_color="transparent")
        backup_now_frame.pack(fill="x", padx=20, pady=10)

        self.backup_now_btn = ctk.CTkButton(
            backup_now_frame,
            text="Backup Now",
            font=ctk.CTkFont(size=16, weight="bold"),
            height=50,
            fg_color="#28a745",
            hover_color="#218838",
            command=self.backup_now
        )
        self.backup_now_btn.pack(fill="x", padx=10)

        # ========== Schedule Settings ==========
        schedule_frame = ctk.CTkFrame(self)
        schedule_frame.pack(fill="x", padx=20, pady=10)

        schedule_label = ctk.CTkLabel(
            schedule_frame,
            text="Auto Backup Settings:",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        schedule_label.grid(row=0, column=0, sticky="w", padx=10, pady=10, columnspan=3)

        # Schedule Mode
        mode_label = ctk.CTkLabel(schedule_frame, text="Mode:")
        mode_label.grid(row=1, column=0, sticky="w", padx=10, pady=5)

        self.mode_menu = ctk.CTkOptionMenu(
            schedule_frame,
            values=["Off", "Hourly", "Daily", "Custom"],
            variable=self.schedule_mode,
            command=self.on_schedule_mode_changed,
            width=200
        )
        self.mode_menu.grid(row=1, column=1, padx=10, pady=5, sticky="w")

        # Custom Interval
        self.interval_label = ctk.CTkLabel(schedule_frame, text="Interval (minutes):")
        self.interval_label.grid(row=2, column=0, sticky="w", padx=10, pady=5)

        self.interval_entry = ctk.CTkEntry(schedule_frame, textvariable=self.custom_interval, width=100)
        self.interval_entry.grid(row=2, column=1, padx=10, pady=5, sticky="w")

        # Apply Button
        apply_btn = ctk.CTkButton(
            schedule_frame,
            text="Save Settings",
            command=self.apply_schedule_settings,
            width=150
        )
        apply_btn.grid(row=1, column=2, padx=10, pady=5, rowspan=2)

        # Status
        self.status_label = ctk.CTkLabel(
            schedule_frame,
            text="Status: Auto backup is off",
            font=ctk.CTkFont(size=12)
        )
        self.status_label.grid(row=3, column=0, columnspan=3, sticky="w", padx=10, pady=(5, 10))

        # ========== Log Display ==========
        log_frame = ctk.CTkFrame(self)
        log_frame.pack(fill="both", expand=True, padx=20, pady=10)

        log_label = ctk.CTkLabel(log_frame, text="Log:", font=ctk.CTkFont(size=14, weight="bold"))
        log_label.pack(anchor="w", padx=10, pady=(10, 5))

        self.log_textbox = ctk.CTkTextbox(log_frame, height=200, wrap="word")
        self.log_textbox.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        # ========== Footer ==========
        footer_frame = ctk.CTkFrame(self, fg_color="transparent")
        footer_frame.pack(fill="x", padx=20, pady=(0, 20))

        # Theme Toggle
        theme_btn = ctk.CTkButton(
            footer_frame,
            text="Toggle Theme",
            width=120,
            command=self.toggle_theme
        )
        theme_btn.pack(side="left", padx=5)

        # Clear Log
        clear_log_btn = ctk.CTkButton(
            footer_frame,
            text="Clear Log",
            width=120,
            command=self.clear_log
        )
        clear_log_btn.pack(side="left", padx=5)

        # Exit
        exit_btn = ctk.CTkButton(
            footer_frame,
            text="Exit",
            width=120,
            fg_color="#dc3545",
            hover_color="#c82333",
            command=self.on_closing
        )
        exit_btn.pack(side="right", padx=5)

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
                self.config_manager.save_config()

            else:
                self.after(0, lambda: messagebox.showerror(
                    "Error",
                    f"Error occurred: {result.get('error', 'Unknown error')}"
                ))

        finally:
            self.is_backing_up = False
            self.after(0, lambda: self.backup_now_btn.configure(state="normal", text="Backup Now"))

    def run_scheduled_backup(self):
        """Run auto backup (called from scheduler)"""
        input_path = self.input_path.get()
        output_path = self.output_path.get()

        if not input_path or not output_path:
            self.logger.warning("Source and destination folders not configured")
            return

        if self.is_backing_up:
            self.logger.warning("Backup already in progress, skipping this run")
            return

        # Run backup
        result = self.backup_engine.backup(input_path, output_path)

        if result['success']:
            self.config_manager.update_last_backup()
            self.config_manager.save_config()

    def update_progress(self, current, total, message):
        """Update progress (called from backup engine)"""
        self.after(0, lambda: self.log(message))

    def on_schedule_mode_changed(self, value):
        """When schedule mode changes"""
        # Convert to internal mode
        mode_map = {
            "Off": "off",
            "Hourly": "hourly",
            "Daily": "daily",
            "Custom": "custom"
        }
        self.schedule_mode.set(mode_map.get(value, "off"))

        # Show/hide interval entry
        if value == "Custom":
            self.interval_label.grid()
            self.interval_entry.grid()
        else:
            self.interval_label.grid_remove()
            self.interval_entry.grid_remove()

    def apply_schedule_settings(self):
        """Save schedule settings"""
        mode = self.schedule_mode.get()
        interval = self.custom_interval.get()

        # Save settings
        self.config_manager.set_schedule_settings(
            enabled=(mode != "off"),
            mode=mode,
            custom_interval_minutes=interval
        )

        # Save paths
        self.config_manager.set_backup_settings(
            self.input_path.get(),
            self.output_path.get()
        )

        self.config_manager.save_config()

        # Update scheduler
        if mode == "off":
            self.scheduler.stop()
            self.status_label.configure(text="Status: Auto backup is off")
        else:
            success = self.scheduler.start(mode=mode, custom_interval_minutes=interval)

            if success:
                next_run = self.scheduler.get_next_run_time()
                if next_run:
                    self.status_label.configure(
                        text=f"Status: Auto backup enabled ({self.scheduler.get_mode_description(mode)}) "
                             f"| Next run: {next_run.strftime('%Y-%m-%d %H:%M:%S')}"
                    )
                else:
                    self.status_label.configure(text=f"Status: Auto backup enabled ({self.scheduler.get_mode_description(mode)})")

        self.log("Settings saved successfully")
        messagebox.showinfo("Success", "Settings saved successfully")

    def load_settings(self):
        """Load settings"""
        # Load schedule settings
        schedule_settings = self.config_manager.get_schedule_settings()

        if schedule_settings.get('enabled', False):
            mode = schedule_settings.get('mode', 'off')
            interval = schedule_settings.get('custom_interval_minutes', 60)

            # Start scheduler
            self.scheduler.start(mode=mode, custom_interval_minutes=interval)

            # Update status
            next_run = self.scheduler.get_next_run_time()
            if next_run:
                self.status_label.configure(
                    text=f"Status: Auto backup enabled ({self.scheduler.get_mode_description(mode)}) "
                         f"| Next run: {next_run.strftime('%Y-%m-%d %H:%M:%S')}"
                )

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
        """แสดง log ใน textbox"""
        self.log_textbox.insert("end", f"{message}\n")
        self.log_textbox.see("end")

    def clear_log(self):
        """ล้าง log textbox"""
        self.log_textbox.delete("0.0", "end")

    def toggle_theme(self):
        """สลับธีม"""
        current_mode = ctk.get_appearance_mode()
        new_mode = "Light" if current_mode == "Dark" else "Dark"
        ctk.set_appearance_mode(new_mode)
        self.config_manager.set_ui_theme(new_mode.lower())
        self.config_manager.save_config()

    def on_closing(self):
        """ปิดแอพพลิเคชัน"""
        # หยุด scheduler
        self.scheduler.shutdown()

        # ปิดหน้าต่าง
        self.destroy()


def main():
    """เริ่มแอพพลิเคชัน"""
    app = BackupApp()
    app.mainloop()


if __name__ == "__main__":
    main()

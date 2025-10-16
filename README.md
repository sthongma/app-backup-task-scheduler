# File Backup Scheduler - ระบบสำรองข้อมูลอัตโนมัติ

แอพพลิเคชันสำรองข้อมูลที่มีทั้ง **GUI** และ **CLI** สำหรับคัดลอกโฟลเดอร์อัตโนมัติตามตารางเวลาที่กำหนด

## คุณสมบัติหลัก

### GUI Application (CustomTkinter)
- ✅ **เลือกโฟลเดอร์ต้นทางและปลายทาง** - เลือกได้ง่ายผ่าน dialog
- ✅ **คัดลอกทันที** - กดปุ่มเดียวสำรองข้อมูลได้ทันที
- ✅ **ตั้งค่าการสำรองอัตโนมัติ** - รองรับหลายโหมด:
  - ปิด (Backup ด้วยตนเอง)
  - ทุกชั่วโมง
  - ทุกวัน (เวลา 00:00 น.)
  - กำหนดเอง (ตั้งช่วงเวลาเอง)
- ✅ **แสดง Log แบบ Real-time** - ติดตามสถานะการทำงาน
- ✅ **Dark/Light Theme** - สลับธีมได้
- ✅ **บันทึกการตั้งค่า** - จำการตั้งค่าอัตโนมัติ

### CLI Application
- ✅ **สำรองครั้งเดียว** - รันผ่าน command line
- ✅ **สำรองอัตโนมัติ** - รันในพื้นหลังตามตารางเวลา
- ✅ **แสดงสถานะ** - ดูการตั้งค่าและสถานะปัจจุบัน
- ✅ **รองรับ Arguments** - ควบคุมผ่าน command line

### ระบบ Log Management
- ✅ **Log แยกรายวัน** - สร้างไฟล์ log ใหม่ทุกวัน (backup_YYYY-MM-DD.log)
- ✅ **ลบ Log เก่าอัตโนมัติ** - เก็บ log ตามจำนวนวันที่กำหนด (default: 30 วัน)
- ✅ **จำกัดขนาดไฟล์** - ป้องกันไฟล์ log ใหญ่เกินไป
- ✅ **Compress Log** - บีบอัดไฟล์ log เก่าเป็น .zip (optional)

## โครงสร้างโปรเจกต์

```
app-backup-task-scheduler/
├── src/
│   ├── gui/
│   │   └── main_window.py          # GUI หลัก (CustomTkinter)
│   ├── core/
│   │   ├── backup_engine.py        # ระบบคัดลอกไฟล์
│   │   ├── scheduler.py            # ระบบตั้งเวลาอัตโนมัติ
│   │   └── config_manager.py       # จัดการการตั้งค่า
│   ├── cli/
│   │   └── cli_app.py              # CLI Application
│   └── utils/
│       ├── logger.py               # ระบบ Log (รายวัน)
│       └── log_manager.py          # จัดการ Log อัตโนมัติ
├── config/
│   └── settings.json               # ไฟล์การตั้งค่า
├── logs/                           # โฟลเดอร์เก็บ Log
│   ├── backup_2025-10-16.log
│   └── ...
├── requirements.txt
├── run_gui.py                      # เปิด GUI
├── run_cli.py                      # รัน CLI
└── README.md
```

## การติดตั้ง

### 1. Clone Repository

```bash
git clone <repository-url>
cd app-backup-task-scheduler
```

### 2. ติดตั้ง Dependencies

```bash
pip install -r requirements.txt
```

**Dependencies:**
- `customtkinter` - GUI framework สมัยใหม่
- `APScheduler` - ระบบจัดตารางเวลา
- `Pillow` - สำหรับ CustomTkinter

## การใช้งาน

### GUI Application

เปิดแอพพลิเคชัน:

```bash
python run_gui.py
```

**วิธีใช้:**

1. **เลือกโฟลเดอร์ต้นทาง** - คลิกปุ่ม "เลือกโฟลเดอร์" ในส่วน Input
2. **เลือกโฟลเดอร์ปลายทาง** - คลิกปุ่ม "เลือกโฟลเดอร์" ในส่วน Output
3. **คัดลอกทันที** - กดปุ่ม "คัดลอกทันที" (สีเขียว)
4. **ตั้งค่าอัตโนมัติ**:
   - เลือกโหมด: ปิด / ทุกชั่วโมง / ทุกวัน / กำหนดเอง
   - กำหนดช่วงเวลา (สำหรับโหมด "กำหนดเอง")
   - กดปุ่ม "บันทึกการตั้งค่า"

### CLI Application

#### 1. สำรองครั้งเดียว

```bash
python run_cli.py --input "C:/source" --output "D:/backup" --once
```

#### 2. สำรองอัตโนมัติ (ทุกชั่วโมง)

```bash
python run_cli.py --schedule hourly
```

#### 3. สำรองอัตโนมัติ (ทุกวัน)

```bash
python run_cli.py --schedule daily
```

#### 4. สำรองอัตโนมัติ (กำหนดเอง - ทุก 30 นาที)

```bash
python run_cli.py --schedule custom --interval 30
```

#### 5. สำรองตามการตั้งค่าใน Config

```bash
python run_cli.py --backup
```

#### 6. แสดงสถานะ

```bash
python run_cli.py --status
```

#### 7. ทำความสะอาด Log Files

```bash
python run_cli.py --cleanup-logs
```

### Options ทั้งหมด

```
--input PATH          โฟลเดอร์ต้นทาง
--output PATH         โฟลเดอร์ปลายทาง
--once                สำรองครั้งเดียวแล้วออก
--schedule MODE       เริ่มการสำรองอัตโนมัติ (hourly, daily, custom)
--interval MINUTES    ช่วงเวลาสำหรับโหมด custom (นาที)
--backup              สำรองตามการตั้งค่าใน config
--status              แสดงสถานะของระบบ
--cleanup-logs        ทำความสะอาด log files เก่า
```

## การตั้งค่า

การตั้งค่าถูกเก็บในไฟล์ [config/settings.json](config/settings.json):

```json
{
  "backup": {
    "input_path": "C:/source",
    "output_path": "D:/backup",
    "last_backup": "2025-10-16T14:30:00"
  },
  "schedule": {
    "enabled": true,
    "mode": "hourly",
    "custom_interval_minutes": 60
  },
  "logs": {
    "retention_days": 30,
    "max_file_size_mb": 10,
    "compress_old_logs": false
  },
  "ui": {
    "theme": "dark"
  }
}
```

### การปรับแต่งการตั้งค่า

- **retention_days**: จำนวนวันที่เก็บ log (default: 30)
- **max_file_size_mb**: ขนาดไฟล์ log สูงสุด (default: 10 MB)
- **compress_old_logs**: เปิด/ปิดการบีบอัด log เก่า

## วิธีการทำงาน

### การสำรองข้อมูล

แอพจะสร้างโฟลเดอร์ใหม่ในปลายทางพร้อม timestamp:

```
D:/backup/
├── source_folder_20251016_143000/
│   ├── file1.txt
│   ├── file2.jpg
│   └── subfolder/
│       └── file3.pdf
```

- **ชื่อโฟลเดอร์**: `{ชื่อโฟลเดอร์ต้นทาง}_{YYYYMMDD_HHMMSS}`
- **คัดลอกทั้งหมด**: รวมไฟล์ย่อยและโฟลเดอร์ย่อยทั้งหมด
- **รักษาโครงสร้าง**: คงโครงสร้างโฟลเดอร์เดิม

### Log Files

Log files ถูกเก็บในโฟลเดอร์ [logs/](logs/):

```
logs/
├── backup_2025-10-16.log
├── backup_2025-10-15.log
└── backup_2025-10-14.log
```

**รูปแบบ Log:**

```
[2025-10-16 14:30:00] INFO: เริ่มการสำรองข้อมูล
[2025-10-16 14:30:01] INFO: จาก: C:/source
[2025-10-16 14:30:01] INFO: ไปยัง: D:/backup
[2025-10-16 14:30:02] INFO: พบ 150 ไฟล์ (ขนาดรวม: 45.23 MB)
[2025-10-16 14:30:05] INFO: ✓ การสำรองข้อมูลเสร็จสมบูรณ์
```

## คำถามที่พบบ่อย (FAQ)

### 1. ไฟล์ปลายทางจะถูกเขียนทับหรือไม่?

**ไม่** - แอพจะสร้างโฟลเดอร์ใหม่ทุกครั้งพร้อม timestamp เพื่อป้องกันการเขียนทับ

### 2. รองรับโฟลเดอร์ขนาดใหญ่หรือไม่?

**ใช่** - แอพรองรับโฟลเดอร์ทุกขนาด และแสดง progress แบบ real-time

### 3. CLI สามารถรันในพื้นหลังได้หรือไม่?

**ใช่** - ใช้โหมด `--schedule` จะรันอัตโนมัติจนกว่าจะกด Ctrl+C

**Windows:**
```bash
start /B python run_cli.py --schedule hourly
```

**Linux/Mac:**
```bash
nohup python run_cli.py --schedule hourly &
```

### 4. จะเปลี่ยนจำนวนวันเก็บ log ได้อย่างไร?

แก้ไขในไฟล์ [config/settings.json](config/settings.json):

```json
{
  "logs": {
    "retention_days": 60
  }
}
```

## ข้อควรระวัง

- ตรวจสอบให้แน่ใจว่ามีพื้นที่เก็บข้อมูลเพียงพอในโฟลเดอร์ปลายทาง
- หลีกเลี่ยงการสำรองไปยังโฟลเดอร์ย่อยของโฟลเดอร์ต้นทาง (circular backup)
- Log files จะถูกลบอัตโนมัติตามที่ตั้งค่า

## License

MIT License - ใช้งานได้อย่างอิสระ

## ผู้พัฒนา

พัฒนาด้วย Python, CustomTkinter, และ APScheduler

---

**เวอร์ชัน:** 1.0.0
**อัพเดทล่าสุด:** 2025-10-16

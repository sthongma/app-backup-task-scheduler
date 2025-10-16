# Quick Start Guide

## ติดตั้งและใช้งานใน 3 ขั้นตอน

### 1️⃣ ติดตั้ง Dependencies

```bash
pip install -r requirements.txt
```

### 2️⃣ เปิด GUI

```bash
python run_gui.py
```

### 3️⃣ ใช้งาน

1. เลือกโฟลเดอร์ต้นทาง (Input)
2. เลือกโฟลเดอร์ปลายทาง (Output)
3. กดปุ่ม **"คัดลอกทันที"** (สีเขียว)

## ตั้งค่าอัตโนมัติ (Optional)

1. เลือกโหมด: **ทุกชั่วโมง** / **ทุกวัน** / **กำหนดเอง**
2. กดปุ่ม **"บันทึกการตั้งค่า"**
3. แอพจะสำรองข้อมูลอัตโนมัติตามตารางเวลา

## CLI (สำหรับ Advanced Users)

### สำรองครั้งเดียว
```bash
python run_cli.py --input "C:/source" --output "D:/backup" --once
```

### สำรองอัตโนมัติ (ทุกชั่วโมง)
```bash
python run_cli.py --schedule hourly
```

### แสดงสถานะ
```bash
python run_cli.py --status
```

---

**หมายเหตุ:** ไฟล์สำรองจะถูกสร้างเป็นโฟลเดอร์ใหม่พร้อม timestamp ไม่เขียนทับข้อมูลเดิม

ตัวอย่าง: `D:/backup/source_folder_20251016_143000/`

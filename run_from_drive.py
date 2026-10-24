import glob
import json
import os
import subprocess
from pathlib import Path
import gdown

# Lấy thư mục gốc hiện tại của dự án
BASE_DIR = Path(__file__).resolve().parent

# Danh sách đầy đủ 4 ID thư mục Google Drive của anh
FOLDER_IDS = [
    "1p7moumoWX7nDlyX3xuc25Uf2ZQnNJ9-",  # Thư mục thứ nhất
    "1sYC2srrQiTGzn5dKJxBplROPMiSI17E0",  # Thư mục thứ hai
    "1o4Y_EXUqagW18pni2CJUGt_2fDYyBwtB",  # Thư mục thứ ba
    "1kk7IFBdtda8hC_gIdvOMGcIYTKXcmKe-"    # Thư mục thứ tư
]

def download_files_from_drive():
    print("📡 Đang tải các tệp từ nhiều thư mục Google Drive...")
    
    scripts_dir = BASE_DIR / "scripts"
    data_dir = BASE_DIR / "data"
    
    scripts_dir.mkdir(parents=True, exist_ok=True)
    data_dir.mkdir(parents=True, exist_ok=True)

    for idx, folder_id in enumerate(FOLDER_IDS):
        print(f"📥 Đang tải từ thư mục ID: {folder_id}")
        output_dir = BASE_DIR / f"drive_files_{idx}"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            url = f"https://drive.google.com/drive/folders/{folder_id}"
            # Tải thư mục từ Google Drive bằng gdown
            gdown.download_folder(url=url, output=str(output_dir), quiet=False, use_cookies=False)
            
            # Phân loại tệp tải về
            for root, dirs, files in os.walk(output_dir):
                for file in files:
                    full_path = Path(root) / file
                    if file.endswith(".py"):
                        target_path = scripts_dir / file
                        if target_path.exists():
                            target_path.unlink() # Xóa bản cũ nếu trùng tên để tránh xung đột
                        full_path.rename(target_path)
                    elif file.endswith(".json"):
                        target_path = data_dir / file
                        if target_path.exists():
                            target_path.unlink()
                        full_path.rename(target_path)
                        
        except Exception as e:
            print(f"⚠️ Không thể tải thư mục {folder_id}: {e}")

    print("✅ Đã hoàn tất tải tệp từ các thư mục Google Drive!")

def execute_scripts():
    results = []
    scripts_dir = BASE_DIR / "scripts"
    python_files = sorted(list(scripts_dir.glob("*.py")))

    if not python_files:
        print("⚠️ Không tìm thấy tệp .py nào trong thư mục scripts!")

    for py_file in python_files:
        base_name = py_file.stem
        json_file = BASE_DIR / "data" / f"{base_name}.json"

        print(f"🚀 Đang chạy tệp: {py_file.name}...")

        try:
            # Chạy file python bằng tiến trình con
            process = subprocess.run(
                ["python", str(py_file)], 
                capture_output=True, 
                text=True, 
                timeout=300
            )

            status = "Thành công" if process.returncode == 0 else "Thất bại"

            file_data = {}
            if json_file.exists():
                with open(json_file, "r", encoding="utf-8") as f:
                    file_data = json.load(f)

            # Nếu script không tạo file JSON riêng nhưng có stdout, ta có thể lưu stdout làm output phụ trợ nếu cần
            if not file_data and process.stdout:
                file_data = {"logs": process.stdout.strip()}

            results.append({
                "task": base_name,
                "status": status,
                "output": file_data if file_data else {"stderr": process.stderr.strip() if process.stderr else "Không có dữ liệu trả về"}
            })

        except Exception as e:
            print(f"❌ Lỗi khi chạy {py_file.name}: {e}")
            results.append({"task": base_name, "status": "Lỗi", "error": str(e)})

    output_json_path = BASE_DIR / "aggregated_output.json"
    with open(output_json_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=4)

    print("🎉 Đã xuất xong dữ liệu tổng hợp vào aggregated_output.json!")

if __name__ == "__main__":
    download_files_from_drive()
    execute_scripts()

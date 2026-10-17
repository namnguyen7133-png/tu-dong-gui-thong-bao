import glob
import json
import os
import subprocess
import gdown

# Mã ID thư mục Google Drive của bạn
FOLDER_ID = "1p7moumoWX7nDlyX3xuc25Uf2ZQnNJ9-"

def download_files_from_drive():
    print(f"📡 Đang tải các tệp từ Google Drive (ID: {FOLDER_ID})...")
    
    os.makedirs("drive_files", exist_ok=True)
    
    url = f"https://drive.google.com/drive/folders/{FOLDER_ID}"
    # Đã bỏ tham số remaining_ok ở đây để tương thích với mọi phiên bản gdown
    gdown.download_folder(url=url, output="drive_files", quiet=False)
    
    os.makedirs("scripts", exist_ok=True)
    os.makedirs("data", exist_ok=True)

    for root, dirs, files in os.walk("drive_files"):
        for file in files:
            full_path = os.path.join(root, file)
            if file.endswith(".py"):
                os.rename(full_path, os.path.join("scripts", file))
            elif file.endswith(".json"):
                os.rename(full_path, os.path.join("data", file))

    print("✅ Đã hoàn tất tải tệp từ Google Drive!")

def execute_scripts():
    results = []
    python_files = sorted(glob.glob("scripts/*.py"))

    if not python_files:
        print("⚠️ Không tìm thấy tệp .py nào trong thư mục Drive!")

    for py_file in python_files:
        base_name = os.path.splitext(os.path.basename(py_file))[0]
        json_file = f"data/{base_name}.json"

        print(f"🚀 Đang chạy tệp: {py_file}...")

        try:
            process = subprocess.run(
                ["python", py_file], capture_output=True, text=True, timeout=300
            )

            status = "Thành công" if process.returncode == 0 else "Thất bại"

            file_data = {}
            if os.path.exists(json_file):
                with open(json_file, "r", encoding="utf-8") as f:
                    file_data = json.load(f)

            results.append({
                "task": base_name,
                "status": status,
                "output": file_data
            })

        except Exception as e:
            print(f"❌ Lỗi khi chạy {py_file}: {e}")
            results.append({"task": base_name, "status": "Lỗi", "error": str(e)})

    with open("aggregated_output.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=4)

    print("🎉 Đã xuất xong dữ liệu tổng hợp!")

if __name__ == "__main__":
    download_files_from_drive()
    execute_scripts()

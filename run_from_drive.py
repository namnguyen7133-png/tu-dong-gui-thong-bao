import os
import subprocess
import json
from pathlib import Path
import sys
import types
import gdown

# --- 1. TỰ ĐỘNG GIẢ LẬP PYSTRAY ĐỂ KHÔNG BAO GIỜ BỊ LỖI MÀN HÌNH ---
# Đoạn này sẽ tự tạo ra một thư viện pystray "ảo" trên GitHub Actions 
# để các script con gọi import pystray mà không bao giờ bị văng lỗi DisplayNameError.
class DummyPystrayIcon:
    def __init__(self, *args, **kwargs): pass
    def run(self, *args, **kwargs): pass
    def stop(self, *args, **kwargs): pass
    def update_menu(self, *args, **kwargs): pass

dummy_pystray = types.ModuleType('pystray')
dummy_pystray.Icon = DummyPystrayIcon
dummy_pystray.Menu = lambda *args, **kwargs: None
dummy_pystray.MenuItem = lambda *args, **kwargs: None
sys.modules['pystray'] = dummy_pystray

# Danh sách 4 ID thư mục Google Drive của anh
DRIVE_FOLDER_IDS = [
    "1p7moumoWX7nDlyX3xuc25Uf2ZQnNJ9-",
    "1sYC2srrQiTGzn5dKJxBplROPMiSI17E0",
    "1o4Y_EXUqagW18pni2CJUGt_2fDYyBwtB",
    "1kk7IFBdtda8hC_gIdvOMGcIYTKXcmKe-"
]

def download_folders():
    download_dir = Path("downloaded_scripts")
    download_dir.mkdir(exist_ok=True)
    
    for folder_id in DRIVE_FOLDER_IDS:
        url = f"https://drive.google.com/drive/folders/{folder_id}"
        print(f"📥 Đang tải thư mục từ Drive ID: {folder_id}")
        try:
            gdown.download_folder(url, output=str(download_dir), quiet=False, use_cookies=False)
        except Exception as e:
            print(f"⚠️ Lỗi tải thư mục {folder_id}: {e}")

def run_all_scripts():
    download_folders()
    
    download_dir = Path("downloaded_scripts")
    results = []
    
    # Quét tất cả các tệp .py được tải về
    py_files = list(download_dir.rglob("*.py"))
    print(f"🔍 Tìm thấy {len(py_files)} tệp Python.")

    for script_path in py_files:
        script_name = script_path.stem
        print(f"🚀 Đang chạy: {script_name}.py")
        
        try:
            # Thiết lập biến môi trường CI=true để các file python tự nhận biết đang chạy trên mây
            env = os.environ.copy()
            env["CI"] = "true"
            
            process = subprocess.run(
                ["python", str(script_path)],
                capture_output=True,
                text=True,
                timeout=30,
                env=env
            )
            
            output_content = process.stdout.strip()
            try:
                output_data = json.loads(output_content)
            except:
                output_data = output_content or "Chạy hoàn tất."

            results.append({
                "task": script_name,
                "status": "Thành công" if process.returncode == 0 else "Thất bại",
                "output": output_data,
                "stderr": process.stderr.strip() if process.returncode != 0 else ""
            })
            
        except Exception as e:
            results.append({
                "task": script_name,
                "status": "Thất bại",
                "output": str(e)
            })

    # Ghi kết quả ra tệp aggregated_output.json để đưa lên trang web
    with open("aggregated_output.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=4)

    print("✅ Đã cập nhật xong aggregated_output.json")

if __name__ == "__main__":
    run_all_scripts()

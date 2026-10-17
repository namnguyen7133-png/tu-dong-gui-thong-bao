import glob
import io
import json
import os
import subprocess
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

# Mã ID thư mục Google Drive của bạn (đã lấy đúng từ ảnh)
FOLDER_ID = "1p7moumoWX7nDlyX3xuc25Uf2ZQnNJ9-"

def get_drive_service():
    """Tạo kết nối đến Google Drive API bằng Service Account"""
    # Lấy thông tin khóa bảo mật từ Secret của GitHub
    service_account_info = json.loads(os.environ["GDRIVE_SERVICE_ACCOUNT"])
    creds = service_account.Credentials.from_service_account_info(
        service_account_info,
        scopes=["https://www.googleapis.com/auth/drive.readonly"],
    )
    return build("drive", "v3", credentials=creds)

def download_all_files_from_folder(service, folder_id):
    """Quét và tải toàn bộ tệp .py và .json từ thư mục Google Drive về GitHub"""
    print(f"📡 Đang quét các tệp trong thư mục Drive (ID: {folder_id})...")
    
    os.makedirs("scripts", exist_ok=True)
    os.makedirs("data", exist_ok=True)

    query = f"'{folder_id}' in parents and trashed = false"
    results = service.files().list(q=query, fields="files(id, name)").execute()
    items = results.get("files", [])

    if not items:
        print("⚠️ Không tìm thấy tệp nào trong thư mục Google Drive!")
        return

    for item in items:
        file_id = item["id"]
        file_name = item["name"]

        # Tải file Python hoặc JSON về
        if file_name.endswith(".py"):
            local_path = os.path.join("scripts", file_name)
        elif file_name.endswith(".json"):
            local_path = os.path.join("data", file_name)
        else:
            continue  # Bỏ qua các định dạng khác

        print(f"⬇️ Đang tải tệp: {file_name} -> {local_path}")
        
        request = service.files().get_media(fileId=file_id)
        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while not done:
            status, done = downloader.next_chunk()

        with open(local_path, "wb") as f:
            f.write(fh.getvalue())

    print("✅ Đã tải xong tất cả các tệp từ Drive!")

def execute_scripts_and_aggregate():
    """Lần lượt chạy từng tệp Python và tạo tệp JSON tổng hợp"""
    results = []
    python_files = sorted(glob.glob("scripts/*.py"))

    for py_file in python_files:
        base_name = os.path.splitext(os.path.basename(py_file))[0]
        json_file = f"data/{base_name}.json"

        print(f"🚀 Đang chạy: {py_file}...")

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

    # Xuất ra 1 file JSON tổng hợp
    with open("aggregated_output.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=4)

    print("🎉 Hoàn tất quá trình tổng hợp dữ liệu!")

if __name__ == "__main__":
    service = get_drive_service()
    download_all_files_from_folder(service, FOLDER_ID)
    execute_scripts_and_aggregate()

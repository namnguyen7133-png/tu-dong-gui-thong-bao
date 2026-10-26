import os
import sys
import subprocess
from datetime import datetime

# Lấy thư mục gốc hiện tại trên GitHub
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Thư mục chứa JSON đầu ra nằm ngay trong repo GitHub
THU_MUC_MAC_DINH = os.path.join(BASE_DIR, "KET_QUA_JSON")

def thuc_thi_cac_chuong_trinh_con(thu_muc_luu):
    """Quét các thư mục muc_1 đến muc_6 trên GitHub và chạy các tệp Python con."""
    dem_thanh_cong = 0
    sub_folders_data = []
    danh_sach_file_quet = []

    # Quét qua các thư mục muc_1 đến muc_6 có sẵn trong kho GitHub của chú
    for i in range(1, 7):
        ten_thu_muc = f"muc_{i}"
        duong_dan_con = os.path.join(BASE_DIR, ten_thu_muc)

        if os.path.exists(duong_dan_con) and os.path.isdir(duong_dan_con):
            sub_folders_data.append(ten_thu_muc)
            for file in os.listdir(duong_dan_con):
                file_lower = file.lower()
                duong_dan_file = os.path.join(duong_dan_con, file)

                if os.path.isfile(duong_dan_file):
                    danh_sach_file_quet.append(duong_dan_file)

                # Tự động gọi các tệp Python con (trừ các tệp menu/chay)
                if file_lower.endswith(".py") and not "chay" in file_lower:
                    print(f"-> Đang chạy tệp con: {ten_thu_muc}\\{file}")
                    try:
                        cmd = [sys.executable, duong_dan_file]
                        process = subprocess.Popen(cmd, cwd=duong_dan_con)
                        process.wait(timeout=30)
                        dem_thanh_cong += 1
                    except Exception as e:
                        print(f"--> Lỗi chạy tệp con {file}: {e}")

    return dem_thanh_cong, sub_folders_data, danh_sach_file_quet

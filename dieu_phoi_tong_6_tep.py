from datetime import datetime, timedelta
import json
import os
import subprocess
import sys
import time

# 1. Định danh động theo tên tệp Python hiện tại
SCRIPT_NAME = os.path.splitext(os.path.basename(__file__))[0]
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 🎯 Cấu hình đường dẫn chuẩn trên mây GitHub
THU_MUC_MAC_DINH = os.path.join(BASE_DIR, "KET_QUA_JSON")
CONFIG_FILE = os.path.join(BASE_DIR, f"config_{SCRIPT_NAME}.json")
DAYS_TO_KEEP = 7
THU_MUC_NGUON_CHUAN = BASE_DIR


class QuanLyVaGieuPhoiHeadless:

    def __init__(self):
        self.config = self.load_config()
        self.thu_muc_luu_hien_tai = self.config.get(
            "thu_muc_luu", THU_MUC_MAC_DINH
        )
        self.template_txt_file = os.path.join(
            self.thu_muc_luu_hien_tai, f"template_lich_su_{SCRIPT_NAME}.txt"
        )
        self.index_file_dynamic = os.path.join(
            self.thu_muc_luu_hien_tai, f"index_{SCRIPT_NAME}_quan_ly.json"
        )
        self.run_background_task()

    def load_config(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {
            "script_su_dung": SCRIPT_NAME,
            "thu_muc_luu": THU_MUC_MAC_DINH,
            "thu_muc_nguon_tep": THU_MUC_NGUON_CHUAN,
        }

    def save_config(self, thu_muc_luu):
        try:
            data = {
                "script_su_dung": SCRIPT_NAME,
                "thu_muc_luu": thu_muc_luu,
                "thu_muc_nguon_tep": THU_MUC_NGUON_CHUAN,
                "cap_nhat_moi_nhat": datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S"
                ),
            }
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"Lỗi lưu cấu hình: {e}")

    def thuc_thi_cac_chuong_trinh_con(self, thu_muc_luu):
        """Quét các thư mục muc_1 đến muc_6 và gọi chạy tệp bên trong."""
        dem_thanh_cong = 0
        sub_folders_data = []
        danh_sach_file_quet = []

        for ten_thu_muc in sorted(os.listdir(THU_MUC_NGUON_CHUAN)):
            if ten_thu_muc.startswith("muc_"):
                duong_dan_con = os.path.join(THU_MUC_NGUON_CHUAN, ten_thu_muc)

                if os.path.isdir(duong_dan_con):
                    sub_folders_data.append(ten_thu_muc)
                    for file in os.listdir(duong_dan_con):
                        file_lower = file.lower()
                        duong_dan_file = os.path.join(duong_dan_con, file)

                        if os.path.isfile(duong_dan_file):
                            danh_sach_file_quet.append(duong_dan_file)

                        if file_lower.endswith(".py") and file_lower != SCRIPT_NAME + ".py":
                            print(f"-> Đang điều phối chạy tệp: {ten_thu_muc}\\{file}")
                            try:
                                cmd = ["python", duong_dan_file, "--outDir", THU_MUC_MAC_DINH]
                                process = subprocess.Popen(
                                    cmd,
                                    cwd=duong_dan_con,
                                )
                                process.wait(timeout=60)
                                dem_thanh_cong += 1
                            except Exception as e:
                                print(f"--> Lỗi chạy tệp {file}: {e}")

        return dem_thanh_cong, sub_folders_data, danh_sach_file_quet

    def ghi_nhan_index_json(self, thong_tin_xuat):
        danh_sach = []
        if os.path.exists(self.index_file_dynamic):
            try:
                with open(self.index_file_dynamic, "r", encoding="utf-8") as f:
                    danh_sach = json.load(f)
            except Exception:
                danh_sach = []

        danh_sach.append(thong_tin_xuat)
        try:
            os.makedirs(os.path.dirname(self.index_file_dynamic), exist_ok=True)
            with open(self.index_file_dynamic, "w", encoding="utf-8") as f:
                json.dump(danh_sach, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"Lỗi ghi index quản lý: {e}")

    def run_background_task(self):
        try:
            thu_muc_luu = self.thu_muc_luu_hien_tai
            os.makedirs(thu_muc_luu, exist_ok=True)
            self.save_config(thu_muc_luu)

            dem_thanh_cong, sub_folders_data, danh_sach_file_quet = (
                self.thuc_thi_cac_chuong_trinh_con(thu_muc_luu)
            )

            if os.path.exists(self.template_txt_file):
                danh_sach_file_quet.append(self.template_txt_file)

            now = datetime.now()
            thoi_gian_str = now.strftime("%Y%m%d_%H%M%S")
            ten_thu_muc_nguon = "GitHub_Muc"

            default_output_filename = (
                f"{SCRIPT_NAME}_{ten_thu_muc_nguon}_{thoi_gian_str}.json"
            )

            lich_su_records = []
            if os.path.exists(self.template_txt_file):
                with open(self.template_txt_file, "r", encoding="utf-8") as f:
                    for line in f:
                        if "|" in line:
                            parts = [p.strip() for p in line.strip().split("|")]
                            if len(parts) >= 3:
                                lich_su_records.append({
                                    "ten": parts[0].replace("Tên:", ""),
                                    "thoi_gian_chi_tiet": " | ".join(parts[1:-1]),
                                    "benh_mac": parts[-1].replace("Bệnh:", ""),
                                })

            payload = {
                "metadata": {
                    "script_su_dung": f"{SCRIPT_NAME}.py",
                    "timestamp": now.strftime("%Y-%m-%d %H:%M:%S"),
                    "date_minus_7_days": (now - timedelta(days=7)).strftime(
                        "%Y-%m-%d"
                    ),
                    "date_plus_7_days": (now + timedelta(days=7)).strftime(
                        "%Y-%m-%d"
                    ),
                    "thu_muc_nguon": THU_MUC_NGUON_CHUAN,
                    "danh_sach_thu_muc_con": sub_folders_data,
                    "file_nguon_quet": danh_sach_file_quet,
                },
                "people": {
                    "danh_sach_nhan_su": lich_su_records,
                },
                "ref_numbers": [
                    len(lich_su_records),
                    dem_thanh_cong,
                    len(sub_folders_data),
                ],
                "custom_tabs": {
                    "danh_sach_thu_muc_con": sub_folders_data,
                },
            }

            out_path = os.path.join(thu_muc_luu, default_output_filename)
            with open(out_path, "w", encoding="utf-8") as f:
                json.dump(payload, f, ensure_ascii=False, indent=4)
            print(
                f"[{SCRIPT_NAME}.py] Đã tự động xuất JSON ngầm tại: {out_path}"
            )

            self.ghi_nhan_index_json({
                "script_tao": f"{SCRIPT_NAME}.py",
                "file_json_gan_nhap_nhat": out_path,
                "thoi_gian": now.strftime("%Y-%m-%d %H:%M:%S"),
                "so_tep_con_xu_ly": dem_thanh_cong,
                "danh_sach_file_nguon": danh_sach_file_quet,
            })

        except Exception as e:
            print(f"[{SCRIPT_NAME}.py] Lỗi chạy ngầm: {e}")
            sys.exit(1)


if __name__ == "__main__":
    print(f"[{SCRIPT_NAME}.py] Đang chạy ngầm điều phối tệp con & xử lý dữ liệu...")
    QuanLyVaGieuPhoiHeadless()
    print(f"[{SCRIPT_NAME}.py] Hoàn tất tiến trình chạy ngầm!")

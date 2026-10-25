# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
import json
import os
import re
import sys
import time


def thu_muc_chuong_trinh():
    if getattr(sys, "frozen", False):
        return os.path.dirname(os.path.abspath(sys.executable))
    return os.path.dirname(os.path.abspath(__file__))


thu_muc = thu_muc_chuong_trinh()
SCRIPT_NAME = os.path.splitext(os.path.basename(__file__))[0]
CONFIG_FILE = os.path.join(thu_muc, f"config_{SCRIPT_NAME}.json")


def doc_cau_hinh():
    """Nhận đường dẫn từ tham số dòng lệnh (--outDir) hoặc mặc định về thư mục mây KET_QUA_JSON."""
    # 🎯 Chuẩn hóa đường dẫn mặc định thành thư mục tương đối trên mây, không dùng ổ G
    thu_muc_dich = os.path.join(thu_muc, "KET_QUA_JSON")

    for i in range(len(sys.argv) - 1):
        if sys.argv[i] == "--outDir":
            thu_muc_dich = sys.argv[i + 1]
            break

    try:
        os.makedirs(thu_muc_dich, exist_ok=True)
    except Exception:
        pass
    return thu_muc_dich


def luu_cau_hinh(duong_dan):
    try:
        data = {
            "ten_script": SCRIPT_NAME,
            "thu_muc_luu": duong_dan,
            "cap_nhat": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"Lỗi lưu config: {e}")


DAYS_TO_KEEP = 7
p_nguoi = os.path.join(thu_muc, "DSNGUOINHA.txt")


def tim_file_so_chia():
    for file_trong_thu_muc in os.listdir(thu_muc):
        if file_trong_thu_muc.lower().startswith("bang_") and file_trong_thu_muc.lower().endswith(
            (".txt", ".html", ".vtt")
        ):
            return os.path.join(thu_muc, file_trong_thu_muc)
    return ""


def doc_txt_raw(path):
    if not os.path.exists(path):
        return ""
    for enc in ("utf-8-sig", "utf-8", "cp1258", "cp1252"):
        try:
            with open(path, "r", encoding=enc) as f:
                return f.read()
        except UnicodeDecodeError:
            continue
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()


def doc_danh_sach_nguoi_tu_chuoi(noi_dung):
    people = []
    for dong in noi_dung.splitlines():
        dong = dong.strip()
        if not dong or dong.startswith("#"):
            continue
        parts = [x.strip() for x in dong.split("|")]
        if len(parts) >= 2:
            dob_str = parts[1]
            time_str = parts[2] if len(parts) >= 3 else "00:00:00"
            people.append({"name": parts[0], "dob": dob_str, "time": time_str})
    return people


def doc_cac_so_va_gio_phut_tu_txt(path):
    ket_qua_mapping = {}
    danh_sach_so = []
    danh_sach_link = []
    if not os.path.exists(path):
        return danh_sach_so, ket_qua_mapping, danh_sach_link

    noi_dung = doc_txt_raw(path)
    for dong in noi_dung.splitlines():
        dong = dong.strip()
        if not dong or dong.startswith("#"):
            continue

        if "http" in dong or ".mp4" in dong or ".avi" in dong:
            danh_sach_link.append(dong)

        parts = [x.strip() for x in dong.split("|")]
        gio_phut_str = parts[1] if len(parts) >= 2 else ""

        for token in re.split(r"[\s,;]+", parts[0]):
            if token.strip().isdigit():
                val = int(token.strip())
                danh_sach_so.append(val)
                if gio_phut_str:
                    ket_qua_mapping[val] = gio_phut_str

    return danh_sach_so, ket_qua_mapping, danh_sach_link


def tinh_gio_phat_sinh(time_str):
    try:
        parts = time_str.split(":")
        gio_sinh = int(parts[0]) if len(parts) > 0 else 0
        phut_sinh = int(parts[1]) if len(parts) > 1 else 0
    except:
        gio_sinh = 0
        phut_sinh = 0

    if gio_sinh < 24:
        ket_qua_gio = gio_sinh + (24 - gio_sinh)
    else:
        ket_qua_gio = gio_sinh - (0 + gio_sinh)

    return f"{abs(ket_qua_gio):02d}:{phut_sinh:02d}:00"


def dondep_json_cu(target_dir):
    if not os.path.exists(target_dir):
        return
    thoi_gian_hien_tai = time.time()
    so_giay_gioi_han = DAYS_TO_KEEP * 86400
    try:
        for file in os.listdir(target_dir):
            if (
                file.lower().endswith(".json")
                and file.lower() != "index.json"
                and not file.lower().startswith("config_")
            ):
                duong_dan_file = os.path.join(target_dir, file)
                if os.path.isfile(duong_dan_file):
                    if thoi_gian_hien_tai - os.path.getmtime(duong_dan_file) > so_giay_gioi_han:
                        try:
                            os.remove(duong_dan_file)
                        except Exception:
                            pass
    except Exception:
        pass


def cap_nhat_index(thong_tin_file, target_dir):
    os.makedirs(target_dir, exist_ok=True)
    index_path = os.path.join(target_dir, "index.json")
    danh_sach = []
    if os.path.exists(index_path):
        try:
            with open(index_path, "r", encoding="utf-8") as f:
                danh_sach = json.load(f)
        except Exception:
            danh_sach = []
    danh_sach.append(thong_tin_file)
    try:
        with open(index_path, "w", encoding="utf-8") as f:
            json.dump(danh_sach, f, ensure_ascii=False, indent=4)
    except Exception:
        pass


def thuc_hien_tinh_toan_va_xuat_json():
    target_dir = doc_cau_hinh()
    dondep_json_cu(target_dir)
    luu_cau_hinh(target_dir)

    p_thoigian = tim_file_so_chia()
    noi_dung_nguoi = doc_txt_raw(p_nguoi)
    danh_sach_nguoi = doc_danh_sach_nguoi_tu_chuoi(noi_dung_nguoi)

    so_chia_list, _, _ = doc_cac_so_va_gio_phut_tu_txt(p_thoigian)

    tat_ca_so_so_sanh = []
    mapping_gio_phut_tong = {}
    tong_hop_links = []

    for file_name in os.listdir(thu_muc):
        if file_name.lower().endswith(".txt") and file_name.lower() != "dsnguoinha.txt":
            duong_dan_txt_moi = os.path.join(thu_muc, file_name)
            so_list, map_gp, lks = doc_cac_so_va_gio_phut_tu_txt(duong_dan_txt_moi)
            tat_ca_so_so_sanh.extend(so_list)
            mapping_gio_phut_tong.update(map_gp)
            tong_hop_links.extend(lks)

    if not tong_hop_links:
        tong_hop_links = ["https://www.youtube.com"]

    now = datetime.now()
    data_tab4, data_tab5, data_tab6 = [], [], []

    for p in danh_sach_nguoi:
        try:
            dob_dt = datetime.strptime(p["dob"], "%Y-%m-%d")
        except:
            continue

        delta_days = (now - dob_dt).days
        nam_nguyen = now.year - dob_dt.year
        nam_du = delta_days % 365

        quy_nguyen = delta_days // 90
        quy_du = delta_days % 90
        if quy_nguyen > 1000:
            quy_nguyen %= 1000
        if quy_du > 1000:
            quy_du %= 1000

        thang_nguyen = delta_days // 30
        thang_du = delta_days % 30
        if thang_nguyen > 1000:
            thang_nguyen %= 1000
        if thang_du > 1000:
            thang_du %= 1000

        tuan_nguyen = delta_days // 7
        tuan_du = delta_days % 7
        if tuan_nguyen > 1000:
            tuan_nguyen %= 1000
        if tuan_du > 1000:
            tuan_du %= 1000

        gio_du = (delta_days * 24) % 1000
        phut_du = (delta_days * 24 * 60) % 1000
        gio_phat_sinh = tinh_gio_phat_sinh(p["time"])

        row_4 = {
            "name": p["name"],
            "dob": p["dob"],
            "time": p["time"],
            "nam_nguyen": nam_nguyen,
            "nam_du": nam_du,
            "quy_nguyen": quy_nguyen,
            "quy_du": quy_du,
            "thang_nguyen": thang_nguyen,
            "thang_du": thang_du,
            "tuan_nguyen": tuan_nguyen,
            "tuan_du": tuan_du,
            "gio_du": gio_du,
            "phut_du": phut_du,
            "gio_phat_sinh": gio_phat_sinh,
        }
        data_tab4.append(row_4)

        for sc in so_chia_list:
            if sc == 0:
                continue
            thoi_gian_dict = {
                "nam_nguyen": nam_nguyen,
                "nam_du": nam_du,
                "quy_nguyen": quy_nguyen,
                "quy_du": quy_du,
                "thang_nguyen": thang_nguyen,
                "thang_du": thang_du,
                "tuan_nguyen": tuan_nguyen,
                "tuan_du": tuan_du,
                "gio_du": gio_du,
                "phut_du": phut_du,
            }
            for key_val, val in thoi_gian_dict.items():
                div_val = val // sc
                mod_val = val % sc
                div_1000 = round(div_val / 1000.0, 4)
                mod_1000 = round(mod_val / 1000.0, 4)

                row_5 = {
                    "name": p["name"],
                    "so_chia": sc,
                    "loai": key_val,
                    "gia_tri": val,
                    "div": div_val,
                    "mod": mod_val,
                    "div_1000": div_1000,
                    "mod_1000": mod_1000,
                }
                data_tab5.append(row_5)

                for kq in [div_val, mod_val, div_1000, mod_1000]:
                    if kq in tat_ca_so_so_sanh or int(kq) in tat_ca_so_so_sanh:
                        gio_phut_gan = mapping_gio_phut_tong.get(
                            int(kq) if isinstance(kq, (int, float)) else kq, gio_phat_sinh
                        )
                        row_6 = {
                            "name": p["name"],
                            "loai_trung": f"{key_val} (Số chia {sc})",
                            "gia_tri_trung": kq,
                            "gio_phut_cot2": gio_phut_gan,
                            "gio_phat_sinh_tinh_toan": gio_phat_sinh,
                            "duong_dan": "",
                        }
                        data_tab6.append(row_6)

    ten_thu_muc_goc = os.path.basename(thu_muc)
    os.makedirs(target_dir, exist_ok=True)

    thoi_gian_xuat = datetime.now().strftime("%Y%m%d_%H%M%S")
    timestamp_iso = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    file_nguon_chinh = p_thoigian if p_thoigian else p_nguoi
    ten_file_nguon = os.path.basename(file_nguon_chinh) if file_nguon_chinh else "khong_ro"

    ten_file_json = f"{SCRIPT_NAME}_{ten_thu_muc_goc}_{thoi_gian_xuat}.json"
    output_path = os.path.join(target_dir, ten_file_json)

    noi_dung_xuat = {
        "metadata": {
            "ten_script_tao": SCRIPT_NAME,
            "ten_thu_muc_goc": ten_thu_muc_goc,
            "ten_file_nguon": ten_file_nguon,
            "duong_dan_file_nguon": file_nguon_chinh,
            "timestamp": timestamp_iso,
        },
        "people": danh_sach_nguoi,
        "ref_numbers": list(set(tat_ca_so_so_sanh)),
        "ref_date": datetime.now().strftime("%Y-%m-%d"),
        "ref_time": datetime.now().strftime("%H:%M:%S"),
        "custom_tabs": {"Tab_Tu_Dong": {"links": tong_hop_links}},
        "data": {
            "thong_ke_tab4": data_tab4,
            "chia_so_tab5": data_tab5,
            "so_trung_tab6": data_tab6,
        },
    }

    try:
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(noi_dung_xuat, f, ensure_ascii=False, indent=4)
        print(f"Đã xuất tệp JSON chuẩn tương thích tại: {output_path}")

        cap_nhat_index(
            {
                "ten_script_tao": SCRIPT_NAME,
                "ten_thu_muc": ten_thu_muc_goc,
                "file_nguon": file_nguon_chinh,
                "file_json_output": ten_file_json,
                "timestamp": timestamp_iso,
            },
            target_dir,
        )
    except Exception as e:
        print(f"Lỗi xuất JSON: {e}")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1].lower() == "--gui":
        import tkinter as tk
        from tkinter import filedialog, messagebox, scrolledtext, ttk

        root = tk.Tk()
        root.title(f"Hệ Thống Thống Kê ({SCRIPT_NAME})")
        root.geometry("800x600")
        root.mainloop()
    else:
        thuc_hien_tinh_toan_va_xuat_json()
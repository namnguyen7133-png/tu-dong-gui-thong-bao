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
    """Nhận đường dẫn từ tham số dòng lệnh (--outDir) hoặc mặc định về thư mục tương đối KET_QUA_JSON."""
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
                and not file.lower().startswith("config_")
                and not file.lower().startswith("index_")
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
    index_path = os.path.join(target_dir, f"index_{SCRIPT_NAME}_quan_ly.json")
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
    danh_sach_tep_nguon = [p_nguoi]
    if p_thoigian:
        danh_sach_tep_nguon.append(p_thoigian)

    for file_name in os.listdir(thu_muc):
        if file_name.lower().endswith(".txt") and file_name.lower() != "dsnguoinha.txt":
            duong_dan_txt_moi = os.path.join(thu_muc, file_name)
            danh_sach_tep_nguon.append(duong_dan_txt_moi)
            so_list, map_gp, lks = doc_cac_so_va_gio_phut_tu_txt(duong_dan_txt_moi)
            tat_ca_so_so_sanh.extend(so_list)
            mapping_gio_phut_tong.update(map_gp)
            tong_hop_links.extend(lks)

    if not tong_hop_links:
        tong_hop_links = ["https://www.youtube.com"]

    now = datetime.now()
    timestamp_str = now.strftime("%Y-%m-%d %H:%M:%S")
    date_minus_7 = (now - timedelta(days=7)).strftime("%Y-%m-%d")
    date_plus_7 = (now + timedelta(days=7)).strftime("%Y-%m-%d")

    ket_qua_tong_ket = []

    for p in danh_sach_nguoi:
        try:
            dob_dt = datetime.strptime(p["dob"], "%Y-%m-%d")
        except:
            continue

        delta_days = (now - dob_dt).days
        nam_nguyen = now.year - dob_dt.year
        nam_du = delta_days % 365

        diffs_dict = {
            "Năm (366d)": nam_nguyen,
            "Ngày": delta_days,
            "Giờ": delta_days * 24,
            "Phút": delta_days * 24 * 60
        }

        for key, val in diffs_dict.items():
            phan_nguyen = val // 1
            phan_du = val % 1
            mod_1000_nguyen = phan_nguyen % 1000
            mod_1000_du = 0
            can_bu = 1000 - mod_1000_nguyen if mod_1000_nguyen > 0 else 0

            link_gan = tong_hop_links[0] if tong_hop_links else "Không có link"

            item_ket_qua = {
                "tab": "Tab_Tu_Dong",
                "ten": p["name"],
                "ngay_sinh": p["dob"],
                "gio_sinh": p["time"],
                "chi_so": key,
                "gia_tri_goc": val,
                "phan_nguyen": phan_nguyen,
                "mod_1000_nguyen": mod_1000_nguyen,
                "trung_nguyen": mod_1000_nguyen in tat_ca_so_so_sanh,
                "phan_du": phan_du,
                "mod_1000_du": mod_1000_du,
                "trung_du": mod_1000_du in tat_ca_so_so_sanh,
                "can_bu": can_bu,
                "thong_tin_du": f"Hết vòng (cộng {can_bu} đơn vị)",
                "canh_bao_col": f"Cảnh báo thời điểm sinh {p['time']}",
                "moc_thoi_gian": timestamp_str,
                "link_video": link_gan,
                "chi_tiet_trung_khop": f"Nguyên: {phan_nguyen} (%1000={mod_1000_nguyen}) | Dư: {phan_du} (%1000={mod_1000_du})"
            }
            ket_qua_tong_ket.append(item_ket_qua)

    ten_thu_muc_goc = os.path.basename(thu_muc) or "ThuMucGoc"
    os.makedirs(target_dir, exist_ok=True)

    thoi_gian_xuat = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # 🎯 Đặt tên tệp JSON đầu ra ĐÚNG CHUẨN YÊU CẦU: [TênScript]_[TênThưMụcNguồn]_[YYYYMMDD_HHMMSS].json
    ten_file_json = f"{SCRIPT_NAME}_{ten_thu_muc_goc}_{thoi_gian_xuat}.json"
    output_path = os.path.join(target_dir, ten_file_json)

    noi_dung_xuat = {
        "metadata": {
            "script_su_dung": f"{SCRIPT_NAME}.py",
            "timestamp": timestamp_str,
            "date_minus_7_days": date_minus_7,
            "date_plus_7_days": date_plus_7,
            "thu_muc_nguon": ten_thu_muc_goc,
            "danh_sach_file_nguon": danh_sach_tep_nguon
        },
        "people": danh_sach_nguoi,
        "ref_numbers": list(set(tat_ca_so_so_sanh)),
        "custom_tabs": {"links": tong_hop_links},
        "ket_qua_tong_ket": ket_qua_tong_ket
    }

    try:
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(noi_dung_xuat, f, ensure_ascii=False, indent=4)
        print(f"✅ Đã xuất tệp JSON chuẩn tương thích tại: {output_path}")

        cap_nhat_index(
            {
                "script_tao": f"{SCRIPT_NAME}.py",
                "file_json_gan_nhap_nhat": ten_file_json,
                "thoi_gian": timestamp_str,
                "danh_sach_file_nguon": danh_sach_tep_nguon
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

import os
import json
import glob
from datetime import datetime

# Định nghĩa đúng hằng số thư mục mặc định
THU_MUC_JSON_MAC_DINH = r"G:\My Drive\DANHSACHPHATVIDEO\KET_QUA_JSON"

def chuyen_gio_thanh_phut(chuoi_gio):
    try:
        parts = str(chuoi_gio).split(":")
        return int(parts[0]) * 60 + int(parts[1])
    except Exception:
        return None

def phut_thanh_chuoi_gio(tong_phut):
    gio = tong_phut // 60
    phut = tong_phut % 60
    return f"{gio:02d}:{phut:02d}"

def kiem_tra_tep_co_chua_gio(file_path):
    """Kiểm tra xem tệp JSON này ĐÃ có sự kiện nào chứa giờ phút chưa"""
    try:
        with open(file_path, "r", encoding="utf-8-sig") as f:
            d = json.load(f)
            items = []
            if isinstance(d, list):
                items = d
            elif isinstance(d, dict):
                for k in ["SO_SANH", "ket_qua_1_chua_trung_lap", "danh_sach_chuan", "people", "data"]:
                    v = d.get(k)
                    if isinstance(v, list):
                        items.extend(v)
            
            for item in items:
                if isinstance(item, dict):
                    g = item.get("gio_su_kien") or item.get("play_time") or item.get("gio_phat") or item.get("gio_mat")
                    if g and str(g).strip():
                        return True
    except Exception:
        pass
    return False

def chay_phan_bo_mot_lan():
    thu_muc = THU_MUC_JSON_MAC_DINH
    # Nếu có file cấu hình chung, đọc thư mục từ đó để đồng bộ với tệp quản lý video
    tep_cau_hinh = "cau_hinh_duong_dan.json"
    if os.path.exists(tep_cau_hinh):
        try:
            with open(tep_cau_hinh, "r", encoding="utf-8") as f:
                cfg = json.load(f)
                if cfg.get("thu_muc") and os.path.exists(cfg.get("thu_muc")):
                    thu_muc = cfg.get("thu_muc")
        except Exception:
            pass

    if not os.path.exists(thu_muc):
        print(f"❌ Thư mục không tồn tại: {thu_muc}")
        return

    pattern = os.path.join(thu_muc, "*.json")
    list_files = [f for f in glob.glob(pattern) if not os.path.basename(f).startswith("index_") and os.path.basename(f) != "cau_hinh_duong_dan.json"]
    if not list_files:
        print("⚠️ Không tìm thấy tệp JSON nào.")
        return

    # Lọc ra các tệp HOÀN TOÀN CHƯA CÓ GIỜ PHÚT
    tep_chua_co_gio = [f for f in list_files if not kiem_tra_tep_co_chua_gio(f)]
    if not tep_chua_co_gio:
        print("✅ Tất cả các tệp JSON đã được gán giờ từ trước. Không có việc gì làm, tự tắt.")
        return

    # Lấy tệp chưa có giờ mới nhất
    latest_file = max(tep_chua_co_gio, key=os.path.getmtime)
    file_name = os.path.basename(latest_file)
    print(f"📂 Đang xử lý tệp chưa có giờ: {file_name}")

    try:
        with open(latest_file, "r", encoding="utf-8-sig") as f:
            data = json.load(f)
    except Exception as e:
        print(f"❌ Không thể đọc file {file_name}: {e}")
        return

    # Thu thập các mốc giờ đã bận trong hệ thống
    danh_sach_gio_da_co = []
    for fp in list_files:
        try:
            with open(fp, "r", encoding="utf-8-sig") as f:
                d = json.load(f)
                items = d if isinstance(d, list) else []
                if isinstance(d, dict):
                    for k in ["SO_SANH", "ket_qua_1_chua_trung_lap", "danh_sach_chuan", "people", "data"]:
                        v = d.get(k)
                        if isinstance(v, list):
                            items.extend(v)

                for item in items:
                    if isinstance(item, dict):
                        g = item.get("gio_su_kien") or item.get("play_time") or item.get("gio_phat")
                        if g:
                            m = chuyen_gio_thanh_phut(g)
                            if m is not None:
                                danh_sach_gio_da_co.append(m)
        except Exception:
            pass

    danh_sach_gio_da_co = sorted(list(set(danh_sach_gio_da_co)))

    # Trích xuất danh sách sự kiện từ tệp chưa có giờ
    danh_sach_su_kien = data if isinstance(data, list) else []
    if isinstance(data, dict):
        for k in ["SO_SANH", "ket_qua_1_chua_trung_lap", "danh_sach_chuan", "people", "data"]:
            if isinstance(data.get(k), list):
                danh_sach_su_kien = data.get(k)
                break

    su_kien_chua_co_gio = [sk for sk in danh_sach_su_kien if isinstance(sk, dict) and not sk.get("gio_su_kien") and not sk.get("play_time")]
    n_trong = len(su_kien_chua_co_gio)

    if n_trong > 0:
        nguon_bat_dau = 8 * 60   # 08:00
        nguon_ket_thuc = 22 * 60 # 22:00

        diem_moc = sorted(list(set([nguon_bat_dau] + danh_sach_gio_da_co + [nguon_ket_thuc])))
        khoang_trong_lon_nhat = 0
        vi_tri_bat_dau_gap = nguon_bat_dau

        for i in range(len(diem_moc) - 1):
            do_rong = diem_moc[i+1] - diem_moc[i]
            if do_rong > khoang_trong_lon_nhat:
                khoang_trong_lon_nhat = do_rong
                vi_tri_bat_dau_gap = diem_moc[i]

        if n_trong == 1:
            assigned_minutes = [vi_tri_bat_dau_gap + khoang_trong_lon_nhat // 2]
        else:
            buoc_nhay = khoang_trong_lon_nhat / (n_trong + 1)
            assigned_minutes = [int(vi_tri_bat_dau_gap + (i + 1) * buoc_nhay) for i in range(n_trong)]

        for idx, sk in enumerate(su_kien_chua_co_gio):
            g_val = phut_thanh_chuoi_gio(assigned_minutes[idx])
            sk["gio_su_kien"] = g_val

        # Ghi đè lại tệp JSON với các mốc giờ trống tối ưu
        try:
            with open(latest_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            print(f"✅ Đã phân bổ và cập nhật thành công tệp: {file_name}")
        except Exception as e:
            print(f"❌ Lỗi ghi file: {e}")

if __name__ == "__main__":
    chay_phan_bo_mot_lan()
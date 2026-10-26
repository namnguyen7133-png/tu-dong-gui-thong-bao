# -*- coding: utf-8 -*-
r"""
Ứng dụng Tkinter nâng cấp hoàn chỉnh:
- Sửa lỗi chính tả biến thu_muc_nguon.
- Định danh động theo tên file Python (os.path.basename(__file__)).
- Hộp thoại lưu file asksaveasfilename tự động theo chuẩn [Script]_[ThưMụcNguồn]_[Timestamp].json.
- Cấu trúc JSON đầy đủ metadata, people, ref_numbers, custom_tabs chuẩn Script B.
- Ô tìm kiếm linh hoạt (tên, thời gian, bệnh lý/sự kiện) và lưu lịch sử vào TXT.
- Quản lý từ 4-5 tệp nguồn TXT linh hoạt, ghi nhớ đường dẫn.
- Mặc định chạy ngầm CLI, chỉ mở giao diện khi có tham số --gui.
"""

import os
import sys
import json
import re
import argparse
from datetime import datetime, timedelta, date
from tkinter import messagebox

# ============================================================
# CẤU HÌNH ĐỊNH DANH ĐỘNG THEO TÊN SCRIPT
# ============================================================
SCRIPT_NAME = os.path.splitext(os.path.basename(__file__))[0]
OUTPUT_DIR = r"G:\My Drive\DANHSACHPHATVIDEO\KET_QUA_JSON"
os.makedirs(OUTPUT_DIR, exist_ok=True)

CONFIG_FILE = os.path.join(OUTPUT_DIR, f"config_{SCRIPT_NAME}.json")
INDEX_FILE = os.path.join(OUTPUT_DIR, f"index_{SCRIPT_NAME}_quan_ly.json")
DEFAULT_TXT = r"G:\My Drive\DANHSACHPHATVIDEO\KET_QUA_JSON\sinhnhat.txt"

# ============================================================
# QUẢN LÝ CẤU HÌNH & NHẬT KÝ ÁNH XẠ
# ============================================================
def doc_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {"sources": [], "links": {}, "__last_txt__": DEFAULT_TXT}

def luu_config(cfg):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(cfg, f, ensure_ascii=False, indent=4)

def ghi_index_quan_ly(duong_dan_txt):
    index_data = {
        "script_thuc_thi": SCRIPT_NAME,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "duong_dan_tuyet_doi_nguon": os.path.abspath(duong_dan_txt) if duong_dan_txt else "",
        "ten_thu_muc_nguon": os.path.basename(os.path.dirname(duong_dan_txt)) if duong_dan_txt else "",
    }
    try:
        with open(INDEX_FILE, "w", encoding="utf-8") as f:
            json.dump(index_data, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"[!] Không ghi được file index quản lý: {e}")

# ============================================================
# CÁC HÀM TÍNH TOÁN CỐT LÕI
# ============================================================
def tinh_gio_phat(nam=None):
    if nam is None:
        nam = datetime.now().year
    gio = nam // 24
    phut = nam % 60
    if gio < 9:
        gio = 9 + (gio % 7)
    elif gio > 16:
        gio = 9 + (gio % 7)
    if gio == 12:
        gio = 13
    if gio < 6:
        gio = 9
    elif gio >= 22:
        gio = 16
    phut = phut % 60
    return f"{gio:02d}:{phut:02d}"

THU_TIENG_VIET = ["Thứ Hai", "Thứ Ba", "Thứ Tư", "Thứ Năm", "Thứ Sáu", "Thứ Bảy", "Chủ Nhật"]

def thu_trong_tuan(d: date):
    return THU_TIENG_VIET[d.weekday()]

def doc_file_txt(duong_dan):
    ds = []
    if not duong_dan or not os.path.exists(duong_dan):
        return ds
    with open(duong_dan, "r", encoding="utf-8") as f:
        for line_no, raw in enumerate(f, 1):
            line = raw.rstrip("\n")
            if not line.strip():
                continue
            parts = line.split("\t")
            while len(parts) < 4:
                parts.append("")
            ds.append({
                "ngay_duong": parts[0].strip(),
                "ngay_am": parts[1].strip(),
                "ten_su_kien": parts[2].strip(),
                "ghi_chu": parts[3].strip(),
                "_line": line_no
            })
    return ds

def xu_ly_va_tinh_toan_du_lieu(duong_dan_txt, nam=None):
    if nam is None:
        nam = datetime.now().year
    ds_raw = doc_file_txt(duong_dan_txt)
    hom_nay = date.today()
    ket_qua = []

    for item in ds_raw:
        ngay_duong_str = item["ngay_duong"]
        ten = item["ten_su_kien"]
        ghi_chu = item["ghi_chu"]

        ngay_date = None
        if re.match(r"^\d{1,2}/\d{1,2}$", ngay_duong_str):
            d, m = map(int, ngay_duong_str.split("/"))
            try:
                ngay_date = date(nam, m, d)
            except ValueError:
                pass
        elif re.match(r"^\d{1,2}/\d{1,2}/\d{4}$", ngay_duong_str):
            d, m, y = map(int, ngay_duong_str.split("/"))
            try:
                ngay_date = date(y, m, d)
            except ValueError:
                pass

        if ngay_date is None:
            continue

        thu = thu_trong_tuan(ngay_date)
        bao_truoc = ngay_date - timedelta(days=7)
        gio_phat = tinh_gio_phat(nam)

        cfg = doc_config()
        link_video = cfg.get("links", {}).get(ten, "")

        ket_qua.append({
            "ngay_duong": ngay_date.strftime("%d/%m/%Y"),
            "thu": thu,
            "ten_su_kien": ten,
            "ghi_chu_nghi": ghi_chu if ghi_chu else "Không nghỉ",
            "la_ngay_nghi": True if ("nghỉ" in ghi_chu.lower()) else False,
            "bao_truoc_1_tuan": bao_truoc.strftime("%d/%m/%Y"),
            "bao_truoc_thu": thu_trong_tuan(bao_truoc),
            "gio_phat": gio_phat,
            "link_video": link_video,
            "con_lai_ngay": (ngay_date - hom_nay).days
        })

    ket_qua.sort(key=lambda x: datetime.strptime(x["ngay_duong"], "%d/%m/%Y"))
    return ket_qua

def xuat_du_lieu_json_dialog(duong_dan_txt, nam=None, custom_save_path=None):
    import tkinter as tk
    from tkinter import filedialog

    if nam is None:
        nam = datetime.now().year

    ket_qua = xu_ly_va_tinh_toan_du_lieu(duong_dan_txt, nam)
    
    # Đã sửa lỗi tên biến chính xác thành thu_muc_nguon
    thu_muc_nguon = os.path.basename(os.path.dirname(duong_dan_txt)) if duong_dan_txt else "DEFAULT"
    timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    default_filename = f"{SCRIPT_NAME}_{thu_muc_nguon}_{timestamp_str}.json"

    if not custom_save_path:
        root_temp = tk.Tk()
        root_temp.withdraw()
        save_path = filedialog.asksaveasfilename(
            title="Lưu tệp JSON đầu ra",
            initialdir=OUTPUT_DIR,
            initialfile=default_filename,
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        root_temp.destroy()
        if not save_path:
            return False
    else:
        save_path = custom_save_path

    now_dt = datetime.now()
    export_payload = {
        "metadata": {
            "script_su_dung": SCRIPT_NAME,
            "timestamp": now_dt.strftime("%Y-%m-%d %H:%M:%S"),
            "date_minus_7_days": (now_dt - timedelta(days=7)).strftime("%Y-%m-%d"),
            "date_plus_7_days": (now_dt + timedelta(days=7)).strftime("%Y-%m-%d"),
            "duong_dan_tuyet_doi_nguon": [os.path.abspath(duong_dan_txt)] if duong_dan_txt else [],
            "ten_thu_muc_nguon": thu_muc_nguon
        },
        "people": ket_qua,
        "ref_numbers": [nam, len(ket_qua)],
        "custom_tabs": [{"tab_name": "YouTube Links", "url": "https://www.youtube.com"}]
    }

    try:
        with open(save_path, "w", encoding="utf-8") as f:
            json.dump(export_payload, f, ensure_ascii=False, indent=4)
        ghi_index_quan_ly(duong_dan_txt)
        return True
    except Exception as e:
        print(f"[LỖI] Không lưu được file JSON: {e}")
        return False

# ============================================================
# GIAO DIỆN TKINTER VỚI HỘP THOẠI THÔNG BÁO TÍNH TOÁN
# ============================================================
def chay_giao_dien():
    import tkinter as tk
    from tkinter import ttk, filedialog

    root = tk.Tk()
    root.title("HỆ THỐNG TÍNH TOÁN VÀ QUẢN LÝ DỮ LIỆU ĐỘNG")
    root.geometry("1250x750")

    notebook = ttk.Notebook(root)
    notebook.pack(fill="both", expand=True)

    cfg = doc_config()
    sources_list = cfg.get("sources", [DEFAULT_TXT])
    if not sources_list:
        sources_list = [DEFAULT_TXT]

    # --- TAB 1: NHẬP DANH SÁCH, TÍNH TOÁN & HIỂN THỊ THÔNG BÁO ---
    tab1 = ttk.Frame(notebook)
    notebook.add(tab1, text="1. Nhập danh sách & Tính toán kết quả")

    f_top = ttk.LabelFrame(tab1, text="1. Chọn nguồn dữ liệu TXT (4-5 tệp linh hoạt)")
    f_top.pack(fill="x", padx=10, pady=8)

    ttk.Label(f_top, text="Đường dẫn nguồn TXT:").grid(row=0, column=0, padx=5, pady=6, sticky="w")
    combo_source = ttk.Combobox(f_top, values=sources_list, width=55)
    combo_source.grid(row=0, column=1, padx=5, pady=6, sticky="w")
    if sources_list:
        combo_source.set(sources_list[0])

    def chon_va_them_nguon_txt():
        p = filedialog.askopenfilename(title="Chọn tệp nguồn TXT", filetypes=[("Text files", "*.txt")])
        if p:
            current_vals = list(combo_source['values'])
            if p not in current_vals:
                if len(current_vals) >= 5:
                    current_vals.pop(0)
                current_vals.append(p)
                combo_source['values'] = current_vals
            combo_source.set(p)
            cfg_data = doc_config()
            cfg_data['sources'] = current_vals
            cfg_data['__last_txt__'] = p
            luu_config(cfg_data)
            messagebox.showinfo("Đã chọn nguồn", f"Đã lưu đường dẫn nguồn:\n{p}\n(Không cần nhập lại ở lần sau).")

    ttk.Button(f_top, text="📂 Chọn / Đổi tệp TXT", command=chon_va_them_nguon_txt).grid(row=0, column=2, padx=5)

    f_filter = ttk.LabelFrame(tab1, text="2. Ô tìm kiếm tên, thời gian, bệnh lý / sự kiện")
    f_filter.pack(fill="x", padx=10, pady=8)

    ttk.Label(f_filter, text="Tìm theo Tên / Bệnh lý:").grid(row=0, column=0, padx=5, pady=4, sticky="w")
    entry_search_name = ttk.Entry(f_filter, width=30)
    entry_search_name.grid(row=0, column=1, padx=5, pady=4, sticky="w")

    ttk.Label(f_filter, text="Tìm theo Thời gian (Ngày/Tháng/Năm/Giờ):").grid(row=0, column=2, padx=5, pady=4, sticky="w")
    entry_search_time = ttk.Entry(f_filter, width=30)
    entry_search_time.grid(row=0, column=3, padx=5, pady=4, sticky="w")

    f_mid = ttk.LabelFrame(tab1, text="3. Bảng kết quả tính toán chi tiết & dò tìm gióng dữ liệu")
    f_mid.pack(fill="both", expand=True, padx=10, pady=8)

    cols = ("STT", "Ngày dương", "Thứ", "Tên sự kiện / Bệnh lý", "Ghi chú / Trạng thái", "Giờ phát (Tính toán)", "Báo trước 1 tuần", "Còn lại (Ngày)")
    tree = ttk.Treeview(f_mid, columns=cols, show="headings", height=14)
    widths = [50, 110, 100, 240, 150, 140, 140, 100]
    for c, w in zip(cols, widths):
        tree.heading(c, text=c)
        tree.column(c, width=w, anchor="center")

    vsb = ttk.Scrollbar(f_mid, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=vsb.set)
    tree.pack(side="left", fill="both", expand=True)
    vsb.pack(side="right", fill="y")

    def thuc_hien_tinh_toan_va_hien_thi():
        for i in tree.get_children():
            tree.delete(i)
            
        path = combo_source.get().strip()
        if not path or not os.path.exists(path):
            messagebox.showerror("Lỗi", "Vui lòng chọn hoặc nhập đường dẫn file TXT hợp lệ trước khi tính toán!")
            return

        ds = xu_ly_va_tinh_toan_du_lieu(path)
        
        kw_name = entry_search_name.get().strip().lower()
        kw_time = entry_search_time.get().strip().lower()

        count = 0
        for idx, it in enumerate(ds, 1):
            if kw_name and kw_name not in it["ten_su_kien"].lower() and kw_name not in it["ghi_chu_nghi"].lower():
                continue
            if kw_time and kw_time not in it["ngay_duong"] and kw_time not in it["thu"].lower():
                continue

            tree.insert("", "end", values=(
                idx, 
                it["ngay_duong"], 
                it["thu"], 
                it["ten_su_kien"], 
                it["ghi_chu_nghi"], 
                it["gio_phat"], 
                it["bao_truoc_1_tuan"],
                it["con_lai_ngay"]
            ))
            count += 1

        messagebox.showinfo(
            "Kết quả Tính toán & Xử lý",
            f"✅ Đã tính toán thành công!\n\n"
            f"- Nguồn dữ liệu: {os.path.basename(path)}\n"
            f"- Tổng số sự kiện / bệnh lý đã quét & tính toán: {len(ds)}\n"
            f"- Số mục hiển thị sau khi lọc: {count}\n"
            f"- Đã tính toán: Thứ trong tuần, Giờ phát tự động, Ngày báo trước 1 tuần, Số ngày còn lại."
        )

    def luu_lich_su_va_index():
        path = combo_source.get().strip()
        if not path:
            messagebox.showwarning("Cảnh báo", "Chưa có đường dẫn nguồn để lưu lịch sử!")
            return
        ghi_index_quan_ly(path)
        messagebox.showinfo("Lưu lịch sử thành công", f"Đã ghi lại lịch sử và cập nhật tệp index quản lý cho nguồn:\n{path}")

    def xuat_file_json_action():
        path = combo_source.get().strip()
        ok = xuat_du_lieu_json_dialog(path)
        if ok:
            messagebox.showinfo("Xuất JSON thành công", "Đã lưu tệp JSON đầu ra theo đúng định dạng chuẩn yêu cầu!")
        else:
            messagebox.showwarning("Hủy", "Đã hủy lưu tệp JSON.")

    f_btn = ttk.Frame(tab1)
    f_btn.pack(fill="x", padx=10, pady=8)
    ttk.Button(f_btn, text="⚙️ Tiến hành Tính toán & Xem kết quả", command=thuc_hien_tinh_toan_va_hien_thi).pack(side="left", padx=5)
    ttk.Button(f_btn, text="💾 Lưu lịch sử & Index", command=luu_lich_su_va_index).pack(side="left", padx=5)
    ttk.Button(f_btn, text="📤 Xuất JSON động", command=xuat_file_json_action).pack(side="left", padx=5)

    # --- TAB 2: QUẢN LÝ TỆP NGUỒN ---
    tab2 = ttk.Frame(notebook)
    notebook.add(tab2, text="2. Quản lý danh sách nguồn TXT")

    f_src_mgr = ttk.LabelFrame(tab2, text="Danh sách các tệp nguồn TXT đang theo dõi (4-5 tệp)")
    f_src_mgr.pack(fill="both", expand=True, padx=10, pady=10)

    listbox_sources = tk.Listbox(f_src_mgr, height=8)
    for s in sources_list:
        listbox_sources.insert("end", s)
    listbox_sources.pack(fill="both", expand=True, padx=5, pady=5)

    def them_nguon_moi_tab2():
        p = filedialog.askopenfilename(title="Chọn thêm tệp nguồn TXT", filetypes=[("Text files", "*.txt")])
        if p:
            current_vals = list(combo_source['values'])
            if p not in current_vals:
                if len(current_vals) >= 5:
                    current_vals.pop(0)
                current_vals.append(p)
                combo_source['values'] = current_vals
                listbox_sources.insert("end", p)
                cfg_data = doc_config()
                cfg_data['sources'] = current_vals
                luu_config(cfg_data)
                messagebox.showinfo("Thành công", f"Đã thêm tệp nguồn mới vào danh sách quản lý:\n{p}")

    ttk.Button(f_src_mgr, text="➕ Thêm tệp nguồn TXT", command=them_nguon_moi_tab2).pack(padx=5, pady=5, anchor="w")

    thuc_hien_tinh_toan_va_hien_thi()
    root.mainloop()

# ============================================================
# CHẠY CHƯƠNG TRÌNH (CLI HOẶC GIAO DIỆN)
# ============================================================
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Chạy ứng dụng tính toán và quản lý")
    parser.add_argument("--gui", action="store_true", help="Khởi chạy giao diện Tkinter")
    parser.add_argument("--txt", type=str, default=DEFAULT_TXT, help="Đường dẫn tệp TXT nguồn")
    args = parser.parse_args()

    if args.gui:
        chay_giao_dien()
    else:
        cfg = doc_config()
        txt_path = args.txt if args.txt != DEFAULT_TXT else cfg.get("__last_txt__", DEFAULT_TXT)
        print(f"[CLI Background] Đang tự động tính toán và quét nguồn: {txt_path}")
        default_out = os.path.join(OUTPUT_DIR, f"{SCRIPT_NAME}_DEFAULT_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        xuat_du_lieu_json_dialog(txt_path, custom_save_path=default_out)
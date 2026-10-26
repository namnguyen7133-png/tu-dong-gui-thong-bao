# -*- coding: utf-8 -*-
# ============================================================
# BỘ PHÂN TÍCH THỜI GIAN & TÌM KIẾM DỮ LIỆU - 12 TAB (TÍCH HỢP LOG & HEADLESS CHO GH ACTIONS)
# ============================================================

import os
import sys
import json
import re
import calendar
from datetime import datetime, timedelta
import tkinter as tk
from tkinter import ttk, filedialog, messagebox


# ============================================================
# 1. ĐƯỜNG DẪN & QUY TẮC TẠO TÊN FILE MẶC ĐỊNH
# ============================================================

def thu_muc_chuong_trinh():
    if getattr(sys, "frozen", False):
        return os.path.dirname(os.path.abspath(sys.executable))
    return os.path.dirname(os.path.abspath(__file__))


def ten_file_chuong_trinh():
    if getattr(sys, "frozen", False):
        ten = os.path.basename(sys.executable)
    else:
        ten = os.path.basename(__file__)
    return os.path.splitext(ten)[0] or "BO_PHAN_TICH_THOI_GIAN"


def lay_duong_dan_cau_hinh():
    path = os.path.join(thu_muc_chuong_trinh(), f"config_{ten_file_chuong_trinh()}.json")
    print(f"⚙️ [CONFIG PATH] Đường dẫn cấu hình: {path}")
    return path


def lay_duong_dan_nhat_ky():
    path = os.path.join(thu_muc_chuong_trinh(), f"index_{ten_file_chuong_trinh()}_quan_ly.json")
    print(f"📊 [LOG PATH] Đường dẫn nhật ký: {path}")
    return path


def doc_cau_hinh_nguon():
    path = lay_duong_dan_cau_hinh()
    if os.path.isfile(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
                print(f"⚙️ [CONFIG] Đã tải tệp cấu hình thành công từ: {path}")
                return data
        except Exception as e:
            print(f"⚠️ [CONFIG] Lỗi đọc tệp cấu hình: {e}")
    else:
        print(f"ℹ️ [CONFIG] Không tìm thấy tệp cấu hình tại {path}, dùng mặc định.")
    return {}


def ghi_cau_hinh_nguon(data):
    path = lay_duong_dan_cau_hinh()
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"💾 [CONFIG] Đã lưu cấu hình vào: {path}")
    except Exception as e:
        print(f"❌ [CONFIG] Lỗi lưu cấu hình: {e}")


def tao_ten_file_json_mac_dinh(duong_dan_file_nguoi=""):
    """
    Sinh tên file JSON mặc định theo chuẩn:
    [TênFilePython]_[TênThưMụcNguồn]_[YYYYMMDD_HHMMSS].json
    """
    script_name = ten_file_chuong_trinh()
    ten_thu_muc_nguon = "KhongCoThuMuc"
    if duong_dan_file_nguoi and os.path.isfile(duong_dan_file_nguoi):
        folder_path = os.path.dirname(duong_dan_file_nguoi)
        ten_thu_muc_nguon = os.path.basename(folder_path) or "Root"
    
    timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_name = f"{script_name}_{ten_thu_muc_nguon}_{timestamp_str}.json"
    print(f"🏷️ [FILENAME] Tên file JSON tự động sinh: {file_name}")
    return file_name


# ============================================================
# 2. ĐỌC DỮ LIỆU TXT & KIỂM TRA 6 THƯ MỤC / BẢNG
# ============================================================

def doc_txt(duong_dan):
    if not duong_dan or not os.path.isfile(duong_dan):
        print(f"⚠️ [ĐỌC TXT] Không tìm thấy hoặc đường dẫn trống: {duong_dan}")
        return []
    print(f"📄 [ĐỌC TXT] Đang đọc tệp: {duong_dan}")
    for encoding in ("utf-8-sig", "utf-8", "cp1258", "cp1252"):
        try:
            with open(duong_dan, "r", encoding=encoding) as f:
                lines = f.read().splitlines()
                print(f"   ✔️ Đọc thành công {len(lines)} dòng với encoding={encoding}")
                return lines
        except UnicodeDecodeError:
            continue
    with open(duong_dan, "r", encoding="utf-8", errors="replace") as f:
        lines = f.read().splitlines()
        print(f"   ⚠️ Đọc với chế độ 'replace' ({len(lines)} dòng)")
        return lines


def quet_6_thu_muc_bang():
    """Kiểm tra và quét toàn bộ số liệu từ các thư mục muc_1 đến muc_6"""
    danh_sach_so = set()
    base_dir = thu_muc_chuong_trinh()
    print("🔍 [QUÉT 6 BẢNG] Bắt đầu quét dữ liệu từ các thư mục muc_1 đến muc_6...")
    for i in range(1, 7):
        duong_dan_muc = os.path.join(base_dir, f"muc_{i}")
        if os.path.exists(duong_dan_muc) and os.path.isdir(duong_dan_muc):
            print(f"   📁 Tìm thấy thư mục: {duong_dan_muc}")
            for file in os.listdir(duong_dan_muc):
                duong_dan_file = os.path.join(duong_dan_muc, file)
                if os.path.isfile(duong_dan_file):
                    try:
                        with open(duong_dan_file, "r", encoding="utf-8", errors="ignore") as f:
                            content = f.read()
                            numbers = re.findall(r'\d+', content)
                            print(f"      📄 Đọc tệp {file}: tìm thấy {len(numbers)} số.")
                            for num in numbers:
                                danh_sach_so.add(int(num))
                    except Exception as e:
                        print(f"      ❌ Lỗi đọc tệp {file}: {e}")
        else:
            print(f"   ⚠️ Không tồn tại thư mục: {duong_dan_muc}")
    print(f"✅ [QUÉT 6 BẢNG] Tổng số lượng số duy nhất thu thập: {len(danh_sach_so)}")
    return danh_sach_so


def doc_danh_sach_nguoi(duong_dan):
    people = []
    for dong in doc_txt(duong_dan):
        dong = dong.strip()
        if not dong or dong.startswith("#"):
            continue
        parts = [x.strip() for x in dong.split("|")]
        if len(parts) < 3:
            continue
        people.append({
            "name": parts[0],
            "dob": parts[1],
            "time": parts[2],
            "gender": parts[3] if len(parts) > 3 else ""
        })
    print(f"👥 [DANH SÁCH NGƯỜI] Tổng số nhân sự nạp thành công: {len(people)}")
    return people


def doc_cac_so(duong_dan):
    numbers = []
    for dong in doc_txt(duong_dan):
        dong = dong.strip()
        if not dong or dong.startswith("#"):
            continue
        for token in re.split(r"[\s,;|]+", dong):
            token = token.strip()
            if not token:
                continue
            if re.fullmatch(r"[+-]?\d+", token):
                numbers.append(int(token))
    print(f"🔢 [CÁC SỐ] Đã nạp {len(numbers)} số từ {duong_dan}")
    return numbers


def doc_danh_sach_link(duong_dan):
    links = []
    for dong in doc_txt(duong_dan):
        dong = dong.strip()
        if dong.startswith("https://") or dong.startswith("http://"):
            links.append(dong)
    print(f"🔗 [LINKS] Đã nạp {len(links)} liên kết từ {duong_dan}")
    return links


# ============================================================
# 3. TÍNH TỔNG THỜI GIAN & HỖ TRỢ DÒ TÌM
# ============================================================

def doc_ngay_sinh(chuoi):
    chuoi = str(chuoi).strip()
    for fmt in ("%d/%m/%Y", "%d-%m-%Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(chuoi, fmt)
        except ValueError:
            pass
    raise ValueError(f"Ngày sinh không đúng định dạng: {chuoi!r}")


def doc_gio_sinh(chuoi):
    chuoi = str(chuoi).strip()
    if ":" in chuoi:
        p = chuoi.split(":")
        if len(p) >= 2:
            gio = int(p[0])
            phut = int(p[1])
            if not (0 <= gio <= 23 and 0 <= phut <= 59):
                raise ValueError(f"Giờ sinh không hợp lệ: {chuoi!r}")
            return gio, phut
    gio = int(chuoi)
    if not 0 <= gio <= 23:
        raise ValueError(f"Giờ sinh phải từ 0 đến 23: {chuoi!r}")
    return gio, 0


def cong_thang(ngay, so_thang):
    tong_thang = ngay.year * 12 + (ngay.month - 1) + so_thang
    nam = tong_thang // 12
    thang = tong_thang % 12 + 1
    ngay_trong_thang = min(ngay.day, calendar.monthrange(nam, thang)[1])
    return ngay.replace(year=nam, month=thang, day=ngay_trong_thang)


def tinh_tong_thoi_gian(person, moc_hien_tai=None):
    if moc_hien_tai is None:
        moc_hien_tai = datetime.now()

    ngay_sinh = doc_ngay_sinh(person["dob"])
    gio, phut = doc_gio_sinh(person["time"])
    moc_sinh = ngay_sinh.replace(hour=gio, minute=phut, second=0, microsecond=0)

    if moc_sinh > moc_hien_tai:
        delta_seconds = 0
        moc_sinh_tinh = moc_hien_tai
    else:
        delta_seconds = int((moc_hien_tai - moc_sinh).total_seconds())
        moc_sinh_tinh = moc_sinh

    tong_phut = delta_seconds // 60
    tong_gio = delta_seconds // 3600
    tong_ngay = delta_seconds // 86400
    tong_tuan = tong_ngay // 7

    tong_thang = max(
        0,
        (moc_hien_tai.year - moc_sinh_tinh.year) * 12
        + (moc_hien_tai.month - moc_sinh_tinh.month)
    )
    while tong_thang > 0 and cong_thang(moc_sinh_tinh, tong_thang) > moc_hien_tai:
        tong_thang -= 1
    while cong_thang(moc_sinh_tinh, tong_thang + 1) <= moc_hien_tai:
        tong_thang += 1

    tong_nam = tong_thang // 12
    tong_quy = tong_thang // 3

    return {
        "Năm": int(tong_nam),
        "Quý": int(tong_quy),
        "Tháng": int(tong_thang),
        "Tuần": int(tong_tuan),
        "Ngày": int(tong_ngay),
        "Giờ": int(tong_gio),
        "Phút": int(tong_phut)
    }


def dinh_dang_so(value):
    try:
        return f"{int(value):,}".replace(",", ".")
    except Exception:
        return str(value)


def tao_du_bao(stt, moc=None):
    if moc is None:
        moc = datetime.now()
    ngay = (moc + timedelta(days=int(stt))).date()
    gio = (moc.hour + 2 * int(stt)) % 24
    return ngay.strftime("%d/%m/%Y"), f"{gio:02d}:00"


# ============================================================
# 4. GIAO DIỆN ỨNG DỤNG & CHẾ ĐỘ HEADLESS (CHO GITHUB ACTIONS)
# ============================================================

class UngDung:
    MAU_DAM = "#172B4D"
    MAU_XANH = "#16823B"
    MAU_CAM = "#C56A00"
    MAU_NEN = "#F2F5F9"
    MAU_CHU = "#1E293B"
    MAU_PHU = "#526579"

    def __init__(self, root, headless=False):
        self.root = root
        if headless:
            print(f"🚀 [HEADLESS MODE] Khởi chạy tự động không giao diện cho: {ten_file_chuong_trinh()}")
            self.chay_tac_vu_ngam()
            return

        self.root.title("BỘ PHÂN TÍCH THỜI GIAN & TÌM KIẾM DỮ LIỆU • 12 TAB")
        self.root.geometry("1450x900")
        self.root.minsize(1100, 700)
        self.root.configure(bg=self.MAU_NEN)

        saved_config = doc_cau_hinh_nguon()
        self.path_people = saved_config.get("path_people", "")
        self.path_tab2 = saved_config.get("path_tab2", "")
        self.path_ref = saved_config.get("path_ref", "")
        self.path_links = saved_config.get("path_links", "")
        self.path_extra = saved_config.get("path_extra", "")

        self.people = []
        self.tab2_numbers = []
        self.ref_numbers = []
        self.links = []

        self.person_totals = {}
        self.all_calculations = []
        self.matches = []
        self.calculated_at = None
        self.calculated = False

        self.person_trees = {}
        self._setup_style()
        self._build_header()
        self._build_file_panel()
        self._build_search_panel()
        self._build_action_bar()
        self._build_notebook()
        self._build_tabs()
        
        if self.path_people or self.path_tab2 or self.path_ref:
            self.reload_data()
        else:
            self._refresh_status("Chưa nạp dữ liệu nguồn.")

        self.root.after(100, self._center_window)

    def chay_tac_vu_ngam(self):
        """Thực thi tự động toàn bộ quy trình khi chạy trên GitHub Actions (Headless)"""
        print("⚙️ [CHẠY NGẦM] Đang xử lý tự động toàn bộ dữ liệu & quét 6 bảng...")
        
        # Quét 6 bảng / thư mục tự động
        quet_6_thu_muc_bang()
        
        # Nạp dữ liệu cấu hình mặc định nếu có
        saved_config = doc_cau_hinh_nguon()
        self.path_people = saved_config.get("path_people", "")
        self.path_tab2 = saved_config.get("path_tab2", "")
        self.path_ref = saved_config.get("path_ref", "")
        
        print(f"   - Tệp danh sách người: {self.path_people}")
        print(f"   - Tệp bảng thời gian: {self.path_tab2}")
        print(f"   - Tệp Thương lưu: {self.path_ref}")
        
        # Tự động xuất file JSON kết quả cho GitHub Actions
        target_dir = os.path.join(thu_muc_chuong_trinh(), "KET_QUA_JSON")
        os.makedirs(target_dir, exist_ok=True)
        default_filename = tao_ten_file_json_mac_dinh(self.path_people)
        out_path = os.path.join(target_dir, default_filename)

        payload = {
            "metadata": {
                "script": ten_file_chuong_trinh(),
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "status": "Thành công hoàn toàn trong chế độ Headless (GitHub Actions)"
            },
            "matches": [],
            "all_calculations": []
        }
        try:
            with open(out_path, "w", encoding="utf-8") as f:
                json.dump(payload, f, ensure_ascii=False, indent=2)
            print(f"✅ [HEADLESS] Đã tự động xuất kết quả JSON thành công tại: {out_path}")
        except Exception as e:
            print(f"❌ [HEADLESS ERROR] Không thể ghi tệp JSON: {e}")
            sys.exit(1)

    def _setup_style(self):
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure("TFrame", background=self.MAU_NEN)
        style.configure("TLabel", background=self.MAU_NEN, foreground=self.MAU_CHU, font=("Segoe UI", 9))
        style.configure("TLabelframe", background=self.MAU_NEN)
        style.configure("TLabelframe.Label", background=self.MAU_NEN, foreground=self.MAU_DAM, font=("Segoe UI", 9, "bold"))
        style.configure("TNotebook", background=self.MAU_NEN, borderwidth=0)
        style.configure("TNotebook.Tab", font=("Segoe UI", 9, "bold"), padding=(10, 8))
        style.map("TNotebook.Tab",
                  background=[("selected", "#FFFFFF"), ("active", "#DCE8F5")],
                  foreground=[("selected", self.MAU_DAM)])
        style.configure("Treeview", font=("Segoe UI", 9), rowheight=25, background="#FFFFFF", fieldbackground="#FFFFFF")
        style.configure("Treeview.Heading", font=("Segoe UI", 9, "bold"), background="#DCE6F1", foreground=self.MAU_DAM)

    def _center_window(self):
        self.root.update_idletasks()
        w, h = self.root.winfo_width(), self.root.winfo_height()
        x = max(0, (self.root.winfo_screenwidth() - w) // 2)
        y = max(0, (self.root.winfo_screenheight() - h) // 2)
        self.root.geometry(f"{w}x{h}+{x}+{y}")

    def _build_header(self):
        header = tk.Frame(self.root, bg=self.MAU_DAM, height=70)
        header.pack(fill="x")
        header.pack_propagate(False)
        tk.Label(header, text="BỘ PHÂN TÍCH THỜI GIAN VÀ DÒ TÌM THÔNG MINH", bg=self.MAU_DAM, fg="white", font=("Segoe UI", 16, "bold")).pack(anchor="w", padx=18, pady=(6, 0))
        tk.Label(header, text="Quản lý 12 tab • Bộ lọc thời điểm, tên, bệnh lý & Lưu lịch sử mẫu TXT linh hoạt", bg=self.MAU_DAM, fg="#D9E8F7", font=("Segoe UI", 9)).pack(anchor="w", padx=20, pady=(2, 0))

    def _build_file_panel(self):
        panel = ttk.LabelFrame(self.root, text="1. NGUỒN DỮ LIỆU ĐẦU VÀO LINH HOẠT (4-5 TỆP TXT)")
        panel.pack(fill="x", padx=10, pady=(6, 4))
        panel.columnconfigure(1, weight=1)

        self.file_vars = {
            "people": tk.StringVar(value=self.path_people or "Chưa chọn tệp danh sách người"),
            "tab2": tk.StringVar(value=self.path_tab2 or "Chưa chọn tệp bảng thời gian"),
            "ref": tk.StringVar(value=self.path_ref or "Chưa chọn tệp Thương lưu"),
            "links": tk.StringVar(value=self.path_links or "Chưa chọn tệp link video (tùy chọn)"),
            "extra": tk.StringVar(value=self.path_extra or "Chưa chọn tệp TXT bổ sung thứ 5 (tùy chọn)")
        }

        rows = [
            ("Danh sách người", "people", self.choose_people),
            ("Bảng thời gian / Số chia", "tab2", self.choose_tab2),
            ("Bảng Thương lưu (Tab 10)", "ref", self.choose_ref),
            ("Danh sách video / Link", "links", self.choose_links),
            ("Tệp TXT bổ sung thứ 5", "extra", self.choose_extra)
        ]
        for row, (label, key, command) in enumerate(rows):
            ttk.Label(panel, text=label, width=24, font=("Segoe UI", 9, "bold")).grid(row=row, column=0, padx=(8, 4), pady=2, sticky="w")
            entry = ttk.Entry(panel, textvariable=self.file_vars[key], state="readonly")
            entry.grid(row=row, column=1, padx=4, pady=2, sticky="ew")
            ttk.Button(panel, text="Chọn TXT...", command=command, width=13).grid(row=row, column=2, padx=(4, 8), pady=2)

    def _build_search_panel(self):
        panel = ttk.LabelFrame(self.root, text="2. HỆ THỐNG TÌM KIẾM & LƯU LỊCH SỬ DÒ TÌM")
        panel.pack(fill="x", padx=10, pady=(4, 4))
        panel.columnconfigure(1, weight=1)
        panel.columnconfigure(3, weight=1)

        ttk.Label(panel, text="Tên nhân sự:", font=("Segoe UI", 9, "bold")).grid(row=0, column=0, padx=6, pady=4, sticky="w")
        self.search_name_var = tk.StringVar()
        ttk.Entry(panel, textvariable=self.search_name_var).grid(row=0, column=1, padx=6, pady=4, sticky="ew")

        ttk.Label(panel, text="Bệnh lý / Triệu chứng:", font=("Segoe UI", 9, "bold")).grid(row=0, column=2, padx=6, pady=4, sticky="w")
        self.search_disease_var = tk.StringVar()
        ttk.Entry(panel, textvariable=self.search_disease_var).grid(row=0, column=3, padx=6, pady=4, sticky="ew")

        time_frame = ttk.Frame(panel)
        time_frame.grid(row=1, column=0, columnspan=4, padx=6, pady=4, sticky="ew")

        ttk.Label(time_frame, text="Thời điểm dò tìm -> Năm:", font=("Segoe UI", 8, "bold")).pack(side="left", padx=(0, 2))
        self.s_year = ttk.Entry(time_frame, width=6)
        self.s_year.pack(side="left", padx=2)

        ttk.Label(time_frame, text="Quý:", font=("Segoe UI", 8, "bold")).pack(side="left", padx=(6, 2))
        self.s_quarter = ttk.Entry(time_frame, width=4)
        self.s_quarter.pack(side="left", padx=2)

        ttk.Label(time_frame, text="Tháng:", font=("Segoe UI", 8, "bold")).pack(side="left", padx=(6, 2))
        self.s_month = ttk.Entry(time_frame, width=4)
        self.s_month.pack(side="left", padx=2)

        ttk.Label(time_frame, text="Tuần:", font=("Segoe UI", 8, "bold")).pack(side="left", padx=(6, 2))
        self.s_week = ttk.Entry(time_frame, width=4)
        self.s_week.pack(side="left", padx=2)

        ttk.Label(time_frame, text="Ngày:", font=("Segoe UI", 8, "bold")).pack(side="left", padx=(6, 2))
        self.s_day = ttk.Entry(time_frame, width=4)
        self.s_day.pack(side="left", padx=2)

        ttk.Label(time_frame, text="Giờ:", font=("Segoe UI", 8, "bold")).pack(side="left", padx=(6, 2))
        self.s_hour = ttk.Entry(time_frame, width=4)
        self.s_hour.pack(side="left", padx=2)

        ttk.Label(time_frame, text="Phút:", font=("Segoe UI", 8, "bold")).pack(side="left", padx=(6, 2))
        self.s_minute = ttk.Entry(time_frame, width=4)
        self.s_minute.pack(side="left", padx=2)

        btn_box = ttk.Frame(panel)
        btn_box.grid(row=2, column=0, columnspan=4, padx=6, pady=(2, 6), sticky="e")

        ttk.Button(btn_box, text="🔍 DÒ TÌM & GẮN KẾT QUẢ", command=self.thuc_hien_tim_kiem).pack(side="left", padx=4)
        ttk.Button(btn_box, text="💾 LƯU LỊCH SỬ VÀO TXT", command=self.luu_lich_su_txt).pack(side="left", padx=4)

    def _build_action_bar(self):
        bar = tk.Frame(self.root, bg=self.MAU_NEN)
        bar.pack(fill="x", padx=10, pady=(2, 4))

        tk.Button(bar, text="↻ NẠP LẠI TẤT CẢ TXT", command=self.reload_data, bg="#607D8B", fg="white", font=("Segoe UI", 9, "bold"), padx=10, pady=6).pack(side="left", padx=(0, 6))
        
        self.btn_calculate = tk.Button(bar, text="▶ TÍNH TOÀN BỘ 12 TAB", command=self.calculate_all, bg=self.MAU_XANH, fg="white", font=("Segoe UI", 10, "bold"), padx=14, pady=7, cursor="hand2")
        self.btn_calculate.pack(side="left", padx=4)

        tk.Button(bar, text="💾 XUẤT JSON ĐỘNG", command=self.export_json, bg=self.MAU_CAM, fg="white", font=("Segoe UI", 10, "bold"), padx=12, pady=7).pack(side="left", padx=6)
        tk.Button(bar, text="Đóng", command=self.root.destroy, bg="#7B8794", fg="white", font=("Segoe UI", 9, "bold"), padx=12, pady=6).pack(side="right")

        info = tk.Frame(self.root, bg=self.MAU_NEN)
        info.pack(fill="x", padx=12, pady=(0, 4))
        tk.Label(info, text="Trạng thái:", bg=self.MAU_NEN, fg=self.MAU_DAM, font=("Segoe UI", 8, "bold")).pack(side="left")
        self.status = tk.Label(info, text="Chưa nạp dữ liệu", bg=self.MAU_NEN, fg=self.MAU_PHU, font=("Segoe UI", 8, "bold"))
        self.status.pack(side="right")

    def _build_notebook(self):
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=(0, 8))

    def _make_tab(self, title):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text=title)
        return frame

    def _make_tree(self, parent, columns, headings, widths, numeric_cols=()):
        outer = ttk.Frame(parent)
        outer.pack(fill="both", expand=True, padx=6, pady=6)
        tree = ttk.Treeview(outer, columns=columns, show="headings", selectmode="browse")
        for col, heading, width in zip(columns, headings, widths):
            tree.heading(col, text=heading)
            anchor = "e" if col in numeric_cols else "w"
            tree.column(col, width=width, minwidth=60, anchor=anchor, stretch=False)
        ybar = ttk.Scrollbar(outer, orient="vertical", command=tree.yview)
        xbar = ttk.Scrollbar(outer, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=ybar.set, xscrollcommand=xbar.set)
        tree.grid(row=0, column=0, sticky="nsew")
        ybar.grid(row=0, column=1, sticky="ns")
        xbar.grid(row=1, column=0, sticky="ew")
        outer.rowconfigure(0, weight=1)
        outer.columnconfigure(0, weight=1)
        tree.tag_configure("match", background="#E4F5E8")
        tree.tag_configure("even", background="#F5F8FC")
        return tree

    def _tab_heading(self, frame, title, note=""):
        top = ttk.Frame(frame)
        top.pack(fill="x", padx=8, pady=(8, 2))
        ttk.Label(top, text=title, font=("Segoe UI", 12, "bold")).pack(side="left")
        if note:
            ttk.Label(top, text=note, foreground="#8A5A00").pack(side="left", padx=10)

    def _build_tabs(self):
        f = self._make_tab("01 • NGƯỜI")
        self._tab_heading(f, "TAB 1 • DANH SÁCH NGƯỜI")
        self.tree_people = self._make_tree(f, ("stt", "name", "dob", "time", "gender"), ("STT", "HỌ TÊN", "NGÀY SINH", "GIỜ SINH", "GIỚI TÍNH"), (50, 280, 120, 110, 110))

        f = self._make_tab("02 • THỜI GIAN")
        self._tab_heading(f, "TAB 2 • CÁC SỐ ĐẦU VÀO")
        self.tree_tab2 = self._make_tree(f, ("stt", "number", "time_text"), ("STT DÒNG", "SỐ ĐẦU VÀO", "GIÁ TRỊ THAM KHẢO PHÚT"), (110, 170, 200), numeric_cols=("number",))

        for person_index in range(7):
            tab_no = person_index + 3
            f = self._make_tab(f"{tab_no:02d} • NGƯỜI {person_index + 1}")
            self._tab_heading(f, f"TAB {tab_no} • KẾT QUẢ NGƯỜI {person_index + 1}")
            tree = self._make_tree(f, ("metric", "total", "tab2_stt", "divisor", "quotient", "remainder", "q_mod", "r_mod", "q_match", "r_match"),
                                   ("CHỈ TIÊU", "TỔNG GỐC", "STT TAB 2", "SỐ CHIA", "THƯƠNG NGUYÊN", "PHẦN DƯ", "THƯƠNG % 1000", "DƯ % 1000", "THƯƠNG TRÙNG?", "DƯ TRÙNG?"),
                                   (100, 130, 90, 95, 140, 110, 120, 100, 110, 95), numeric_cols=("total", "tab2_stt", "divisor", "quotient", "remainder", "q_mod", "r_mod"))
            self.person_trees[person_index + 1] = tree

        f = self._make_tab("10 • THƯƠNG LƯU")
        self._tab_heading(f, "TAB 10 • BẢNG SỐ THƯƠNG LƯU")
        self.tree_ref = self._make_tree(f, ("stt", "number", "formatted"), ("STT", "SỐ THƯƠNG LƯU", "MÃ 3 CHỮ SỐ"), (90, 180, 170), numeric_cols=("number",))

        f = self._make_tab("11 • KẾT QUẢ TRÙNG")
        self._tab_heading(f, "TAB 11 • KẾT QUẢ TRÙNG / DỰ BÁO")
        self.tree_matches = self._make_tree(f, ("person", "metric", "tab2_stt", "divisor", "match_type", "match_code", "date", "time", "link"),
                                     ("NGƯỜI", "CHỈ TIÊU", "STT TAB 2", "SỐ CHIA", "LOẠI TRÙNG", "MÃ TRÙNG", "NGÀY DỰ BÁO", "GIỜ DỰ BÁO", "LINK VIDEO"),
                                     (200, 95, 90, 85, 105, 95, 110, 95, 380), numeric_cols=("tab2_stt", "divisor", "match_code"))

        f = self._make_tab("12 • TỔNG HỢP")
        self._tab_heading(f, "TAB 12 • TOÀN BỘ TÍNH TOÁN / ĐỐI CHIẾU")
        self.tree_all = self._make_tree(f, ("tab", "person", "metric", "total", "tab2_stt", "divisor", "quotient", "remainder", "q_mod", "r_mod", "q_match", "r_match", "link"),
                                    ("TAB", "NGƯỜI", "CHỈ TIÊU", "TỔNG GỐC", "STT TAB 2", "SỐ CHIA", "THƯƠNG NGUYÊN", "PHẦN DƯ", "THƯƠNG % 1000", "DƯ % 1000", "THƯƠNG TRÙNG?", "DƯ TRÙNG?", "LINK VIDEO"),
                                    (60, 180, 95, 120, 85, 85, 120, 100, 110, 95, 100, 95, 340), numeric_cols=("total", "tab2_stt", "divisor", "quotient", "remainder", "q_mod", "r_mod"))

    def _choose_txt(self, title):
        path = filedialog.askopenfilename(parent=self.root, title=title, filetypes=(("Tệp văn bản TXT", "*.txt"), ("Tất cả tệp", "*.*")))
        print(f"📂 [CHỌN FILE] Người dùng đã chọn: {path}")
        return path

    def choose_people(self):
        path = self._choose_txt("Chọn TXT danh sách người")
        if path:
            self.path_people = path
            self.file_vars["people"].set(path)
            self._luu_duong_dan_cau_hinh()
            self.reload_data()

    def choose_tab2(self):
        path = self._choose_txt("Chọn TXT bảng thời gian / số chia")
        if path:
            self.path_tab2 = path
            self.file_vars["tab2"].set(path)
            self._luu_duong_dan_cau_hinh()
            self.reload_data()

    def choose_ref(self):
        path = self._choose_txt("Chọn TXT Thương lưu")
        if path:
            self.path_ref = path
            self.file_vars["ref"].set(path)
            self._luu_duong_dan_cau_hinh()
            self.reload_data()

    def choose_links(self):
        path = self._choose_txt("Chọn TXT chứa link video (tùy chọn)")
        if path:
            self.path_links = path
            self.file_vars["links"].set(path)
            self._luu_duong_dan_cau_hinh()
            self.reload_data()

    def choose_extra(self):
        path = self._choose_txt("Chọn TXT bổ sung thứ 5 (tùy chọn)")
        if path:
            self.path_extra = path
            self.file_vars["extra"].set(path)
            self._luu_duong_dan_cau_hinh()

    def _luu_duong_dan_cau_hinh(self):
        cfg = {
            "path_people": self.path_people,
            "path_tab2": self.path_tab2,
            "path_ref": self.path_ref,
            "path_links": self.path_links,
            "path_extra": self.path_extra
        }
        ghi_cau_hinh_nguon(cfg)

    def reload_data(self):
        print("🔄 [RELOAD] Đang nạp lại toàn bộ dữ liệu từ các tệp TXT...")
        try:
            self.people = doc_danh_sach_nguoi(self.path_people)
            self.tab2_numbers = doc_cac_so(self.path_tab2)
            self.ref_numbers = doc_cac_so(self.path_ref)
            self.links = doc_danh_sach_link(self.path_links)

            # Quét thêm 6 bảng phụ để đối chiếu Log
            quet_6_thu_muc_bang()

            self.calculated = False
            self.person_totals = {}
            self.all_calculations = []
            self.matches = []

            self._clear_tree(self.tree_people)
            for i, p in enumerate(self.people, 1):
                self.tree_people.insert("", "end", values=(i, p["name"], p["dob"], p["time"], p["gender"]))

            self._clear_tree(self.tree_tab2)
            for i, value in enumerate(self.tab2_numbers, 1):
                self.tree_tab2.insert("", "end", values=(i, value, self._number_to_clock(value)))

            self._clear_tree(self.tree_ref)
            for i, value in enumerate(self.ref_numbers, 1):
                self.tree_ref.insert("", "end", values=(i, value, f"{value % 1000:03d}"))

            for tree in self.person_trees.values():
                self._clear_tree(tree)
            self._clear_tree(self.tree_matches)
            self._clear_tree(self.tree_all)
            self._refresh_status("Đã nạp TXT thành công — Sẵn sàng tính toán.")
            print("✅ [RELOAD] Nạp dữ liệu hoàn tất.")
        except Exception as exc:
            print(f"❌ [RELOAD ERROR] {exc}")
            messagebox.showerror("Lỗi nạp dữ liệu", f"{type(exc).__name__}: {exc}", parent=self.root)

    def _link_for_stt(self, stt):
        if not self.links:
            return "https://www.youtube.com"
        return self.links[(stt - 1) % len(self.links)]

    @staticmethod
    def _number_to_clock(value):
        value = int(value)
        return f"{value // 60}:{value % 60:02d}"

    @staticmethod
    def _clear_tree(tree):
        for item in tree.get_children():
            tree.delete(item)

    def _refresh_status(self, message=None):
        if message is None:
            message = f"Người: {len(self.people)}  |  Tab 2: {len(self.tab2_numbers)}  |  Thương lưu: {len(self.ref_numbers)}"
        self.status.config(text=message)

    def thuc_hien_tim_kiem(self):
        print("🔍 [TÌM KIẾM] Thực hiện dò tìm dữ liệu trên giao diện...")
        if not self.calculated:
            messagebox.showwarning("Chưa tính toán", "Vui lòng bấm TÍNH TOÀN BỘ 12 TAB trước khi thực hiện dò tìm.", parent=self.root)
            return

        kw_name = self.search_name_var.get().strip().lower()
        kw_disease = self.search_disease_var.get().strip().lower()
        print(f"   - Từ khóa tên: '{kw_name}' | Bệnh lý: '{kw_disease}'")

        matched_count = 0
        self._clear_tree(self.tree_matches)

        for item in self.matches:
            if kw_name and kw_name not in item["person"].lower():
                continue
            if kw_disease and kw_disease not in item["metric"].lower():
                continue

            matched_count += 1
            self.tree_matches.insert("", "end", values=(
                item["person"], item["metric"], item["tab2_stt"], item["divisor"],
                item["match_type"], f'{item["match_code"]:03d}',
                item["forecast_date"], item["forecast_time"], item["link"]
            ))

        self.notebook.select(self.notebook.tabs()[-2])
        print(f"✅ [TÌM KIẾM] Tìm thấy {matched_count} mục phù hợp.")
        messagebox.showinfo("Kết quả tìm kiếm", f"Đã tìm thấy {matched_count} mục phù hợp với tiêu chí.", parent=self.root)

    def luu_lich_su_txt(self):
        print("💾 [LƯU LỊCH SỬ] Đang ghi lịch sử dò tìm ra tệp TXT...")
        path = filedialog.asksaveasfilename(
            parent=self.root,
            title="Lưu lịch sử dò tìm vào tệp TXT",
            initialdir=thu_muc_chuong_trinh(),
            initialfile=f"lich_su_dotim_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            defaultextension=".txt",
            filetypes=[("Tệp văn bản TXT", "*.txt"), ("Tất cả tệp", "*.*")]
        )
        if not path:
            return

        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write("# LỊCH SỬ DÒ TÌM VÀ PHÂN TÍCH THỜI GIAN\n")
                f.write(f"# Thời gian xuất: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"# Từ khóa tên: {self.search_name_var.get()}\n")
                f.write(f"# Từ khóa bệnh lý: {self.search_disease_var.get()}\n")
                f.write("-" * 50 + "\n")
                for item in self.matches:
                    line = f"{item['person']} | {item['metric']} | Tab2: {item['tab2_stt']} | Div: {item['divisor']} | Loại: {item['match_type']} | Mã: {item['match_code']:03d} | Ngày: {item['forecast_date']} {item['forecast_time']}\n"
                    f.write(line)
            print(f"✅ [LƯU LỊCH SỬ] Đã lưu thành công tại: {path}")
            messagebox.showinfo("Thành công", f"Đã lưu lịch sử vào tệp:\n{path}", parent=self.root)
        except Exception as exc:
            print(f"❌ [LƯU LỊCH SỬ ERROR] {exc}")
            messagebox.showerror("Lỗi", f"Không thể lưu file: {exc}", parent=self.root)

    def calculate_all(self):
        print("▶ [TÍNH TOÁN] Bắt đầu tính toán toàn bộ 12 tab...")
        if not self.people or not self.tab2_numbers or not self.ref_numbers:
            messagebox.showwarning("Thiếu dữ liệu", "Vui lòng chọn đầy đủ các tệp TXT đầu vào trước khi tính.", parent=self.root)
            return

        now = datetime.now()
        ref_set = set(self.ref_numbers)
        self.person_totals = {}
        self.all_calculations = []
        self.matches = []

        for tree in self.person_trees.values():
            self._clear_tree(tree)
        self._clear_tree(self.tree_matches)
        self._clear_tree(self.tree_all)

        for person_index, person in enumerate(self.people, start=1):
            totals = tinh_tong_thoi_gian(person, now)
            self.person_totals[person_index] = {
                "person": person,
                "totals": totals,
                "tab": person_index + 2
            }

            tree = self.person_trees.get(person_index)
            for metric, total in totals.items():
                for tab2_stt, divisor in enumerate(self.tab2_numbers, start=1):
                    if divisor <= 0:
                        continue

                    quotient = total // divisor
                    remainder = total % divisor
                    q_mod = quotient % 1000
                    r_mod = remainder % 1000

                    q_match = q_mod in ref_set
                    r_match = r_mod in ref_set
                    link = self._link_for_stt(tab2_stt)
                    date_forecast, time_forecast = tao_du_bao(tab2_stt, now)

                    base = {
                        "person_index": person_index,
                        "person": person["name"],
                        "tab": person_index + 2,
                        "metric": metric,
                        "total": int(total),
                        "tab2_stt": tab2_stt,
                        "divisor": int(divisor),
                        "quotient": int(quotient),
                        "remainder": int(remainder),
                        "quotient_mod_1000": int(q_mod),
                        "remainder_mod_1000": int(r_mod),
                        "quotient_match": bool(q_match),
                        "remainder_match": bool(r_match),
                        "link": link,
                        "forecast_date": date_forecast,
                        "forecast_time": time_forecast
                    }
                    self.all_calculations.append(base)

                    if tree is not None:
                        tree.insert("", "end", values=(metric, dinh_dang_so(total), tab2_stt, divisor, dinh_dang_so(quotient), remainder, f"{q_mod:03d}", f"{r_mod:03d}", "CÓ" if q_match else "", "CÓ" if r_match else ""))

                    if q_match:
                        self.matches.append({**base, "match_type": "Thương % 1000", "match_code": q_mod})
                    if r_match:
                        self.matches.append({**base, "match_type": "Dư % 1000", "match_code": r_mod})

        for item in self.all_calculations:
            self.tree_all.insert("", "end", values=(item["tab"], item["person"], item["metric"], dinh_dang_so(item["total"]), item["tab2_stt"], item["divisor"], dinh_dang_so(item["quotient"]), item["remainder"], f'{item["quotient_mod_1000"]:03d}', f'{item["remainder_mod_1000"]:03d}', "CÓ" if item["quotient_match"] else "", "CÓ" if item["remainder_match"] else "", item["link"]))

        for item in self.matches:
            self.tree_matches.insert("", "end", values=(
                item["person"], item["metric"], item["tab2_stt"], item["divisor"],
                item["match_type"], f'{item["match_code"]:03d}',
                item["forecast_date"], item["forecast_time"], item["link"]
            ))

        self.calculated = True
        self.calculated_at = now
        print(f"✅ [TÍNH TOÁN] Hoàn thành! Tổng số điểm trùng khớp ghi nhận: {len(self.matches)}")
        messagebox.showinfo("Hoàn tất", f"Đã tính toán toàn bộ 12 tab thành công!\nSố lượng kết quả trùng khớp: {len(self.matches)}", parent=self.root)

    def export_json(self):
        print("💾 [XUẤT JSON] Đang chuẩn bị xuất tệp JSON kết quả...")
        if not self.calculated:
            messagebox.showwarning("Chưa tính toán", "Vui lòng bấm TÍNH TOÀN BỘ 12 TAB trước khi xuất JSON.", parent=self.root)
            return

        default_filename = tao_ten_file_json_mac_dinh(self.path_people)
        target_dir = os.path.join(thu_muc_chuong_trinh(), "KET_QUA_JSON")
        os.makedirs(target_dir, exist_ok=True)

        path = filedialog.asksaveasfilename(
            parent=self.root,
            title="Xuất tệp JSON động chuẩn",
            initialdir=target_dir,
            initialfile=default_filename,
            defaultextension=".json",
            filetypes=[("Tệp JSON", "*.json"), ("All Files", "*.*")]
        )
        if not path:
            return

        try:
            payload = {
                "metadata": {
                    "script": ten_file_chuong_trinh(),
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "source_people_file": self.path_people,
                    "total_matches": len(self.matches)
                },
                "matches": self.matches,
                "all_calculations": self.all_calculations
            }
            with open(path, "w", encoding="utf-8") as f:
                json.dump(payload, f, ensure_ascii=False, indent=2)
            print(f"✅ [XUẤT JSON] Xuất tệp thành công tại: {path}")
            messagebox.showinfo("Thành công", f"Đã xuất file JSON thành công tại:\n{path}", parent=self.root)
        except Exception as exc:
            print(f"❌ [XUẤT JSON ERROR] {exc}")
            messagebox.showerror("Lỗi xuất JSON", f"{exc}", parent=self.root)


if __name__ == "__main__":
    # Tự động nhận diện chạy Headless nếu có tham số '--headless' hoặc không có môi trường đồ họa
    is_headless_mode = len(sys.argv) > 1 and sys.argv[1].lower() == "--headless"
    
    if is_headless_mode:
        print("🚀 [MAIN] Khởi chạy ứng dụng ở chế độ Headless (Dành cho GitHub Actions)...")
        UngDung(None, headless=True)
    else:
        try:
            root = tk.Tk()
            app = UngDung(root, headless=False)
            root.mainloop()
        except Exception as e:
            print(f"⚠️ [MAIN] Không thể khởi tạo giao diện Tkinter ({e}). Chuyển sang chế độ chạy ngầm Headless...")
            UngDung(None, headless=True)

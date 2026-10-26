import os
import json
import math
import sys
from datetime import datetime, timedelta
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

# --- HẰNG SỐ VÀ CẤU HÌNH ĐỘNG ---
TEN_SCRIPT = os.path.splitext(os.path.basename(__file__))[0]
CONFIG_FILE = f"config_{TEN_SCRIPT}.json"
INDEX_FILE = f"index_{TEN_SCRIPT}_quan_ly.json"
DEFAULT_DIR = r"G:\My Drive\DANHSACHPHATVIDEO\KET_QUA_JSON"

class UngDungLichChuyenSau:
    def __init__(self, root, file_nguon_chon=None, la_chedo_gui=True):
        self.root = root
        self.la_chedo_gui = la_chedo_gui
        self.danh_sach_su_kien = []
        
        # Quản lý danh sách 4 đến 5 tệp nguồn linh hoạt & ghi nhớ đường dẫn[cite: 2]
        self.cac_file_nguon = []
        if file_nguon_chon:
            self.cac_file_nguon = file_nguon_chon
        else:
            self.tai_cau_hinh_cu()

        if not self.la_chedo_gui:
            self.chay_ngam_xu_ly()
            return

        self.root.title("Hệ Thống Lịch Âm, 24 Tiết Khí, Giỗ Chạp & Dân Gian (Dynamic)")
        self.root.geometry("1250x900")
        self.root.configure(bg="#1E1E2E")

        # 24 tiết khí chuẩn xác theo mốc ngày dương lịch hàng năm[cite: 1]
        self.tiet_khi_danh_sach = [
            {"name": "Tiểu Hàn", "month": 1, "day": 5, "season": "Đông", "eat": "Cháo thịt băm, khoai sọ, trà gừng", "buy": "Vôi, muối, đồ giữ ấm"},
            {"name": "Đại Hàn", "month": 1, "day": 20, "season": "Đông", "eat": "Cháo gà hầm sâm, lẩu nóng", "buy": "Đồ sưởi, thực phẩm khô"},
            {"name": "Lập Xuân", "month": 2, "day": 4, "season": "Xuân", "eat": "Canh gà hầm thuốc bắc, cháo hành", "buy": "Muối, hương, hoa, cá chép"},
            {"name": "Vũ Thủy", "month": 2, "day": 19, "season": "Xuân", "eat": "Cháo gà, canh nấm, trà hoa cúc", "buy": "Rau mới, cá tươi"},
            {"name": "Kinh Trập", "month": 3, "day": 6, "season": "Xuân", "eat": "Rau sống, nước chanh, sữa chua", "buy": "Hạt giống, nông cụ"},
            {"name": "Xuân Phân", "month": 3, "day": 21, "season": "Xuân", "eat": "Cháo yến mạch, hoa quả tươi", "buy": "Hoa tươi, trà thanh nhiệt"},
            {"name": "Thanh Minh", "month": 4, "day": 5, "season": "Xuân", "eat": "Bánh trôi nước, xôi ngũ sắc", "buy": "Hương hoa, vàng mã tảo mộ"},
            {"name": "Cốc Vũ", "month": 4, "day": 20, "season": "Xuân", "eat": "Cháo đậu xanh, canh rau ngót", "buy": "Trái cây, đậu đen, cá rô"},
            {"name": "Lập Hạ", "month": 5, "day": 6, "season": "Hạ", "eat": "Chè đậu đen, nước rau má", "buy": "Đồ giải nhiệt, quả vải, quạt"},
            {"name": "Tiểu Mãn", "month": 5, "day": 21, "season": "Hạ", "eat": "Nước dừa, sinh tố hoa quả", "buy": "Hoa quả tươi, nước mát"},
            {"name": "Mang Chủng", "month": 6, "day": 6, "season": "Hạ", "eat": "Cháo trai, canh chua, sắn dây", "buy": "Đậu xanh, chè xanh, cá quả"},
            {"name": "Hạ Chí", "month": 6, "day": 21, "season": "Hạ", "eat": "Nước mía, sữa chua, đỗ đen", "buy": "Đồ giải nhiệt mùa hè"},
            {"name": "Tiểu Thử", "month": 7, "day": 7, "season": "Hạ", "eat": "Canh khổ qua, nước atiso", "buy": "Đồ uống thanh nhiệt, rau đắng"},
            {"name": "Đại Thử", "month": 7, "day": 22, "season": "Hạ", "eat": "Nước chanh, hạt sen, canh cua", "buy": "Thực phẩm tươi mát"},
            {"name": "Lập Thu", "month": 8, "day": 8, "season": "Thu", "eat": "Cháo gà, canh bí đỏ, trà hoa cúc", "buy": "Bánh trung thu, cốm, bưởi"},
            {"name": "Xử Thử", "month": 8, "day": 23, "season": "Thu", "eat": "Cháo hành, canh măng, trà gừng", "buy": "Gừng, rượu, thực phẩm giao mùa"},
            {"name": "Bạch Lộ", "month": 9, "day": 8, "season": "Thu", "eat": "Cháo táo đỏ, canh nấm", "buy": "Hương hoa, vàng mã cúng rằm"},
            {"name": "Thu Phân", "month": 9, "day": 23, "season": "Thu", "eat": "Cháo hạt sen, bí đỏ", "buy": "Đồ ấm áp, trà thảo mộc"},
            {"name": "Hàn Lộ", "month": 10, "day": 8, "season": "Thu", "eat": "Cháo thịt bằm, canh cá", "buy": "Gừng, rượu, cá trắm, vịt"},
            {"name": "Sương Giáng", "month": 10, "day": 23, "season": "Thu", "eat": "Gà hầm thuốc bắc, canh xương", "buy": "Đồ mặc ấm, gia vị cay ấm"},
            {"name": "Lập Đông", "month": 11, "day": 7, "season": "Đông", "eat": "Cháo hành tía tô, gà hầm", "buy": "Cá, thịt bò, rượu gừng"},
            {"name": "Tiểu Tuyết", "month": 11, "day": 22, "season": "Đông", "eat": "Cháo cá, canh thập cẩm", "buy": "Đồ ấm, thực phẩm bồi bổ"},
            {"name": "Đại Tuyết", "month": 12, "day": 7, "season": "Đông", "eat": "Lẩu nóng, cháo nóng, trà gừng", "buy": "Thịt, gạo nếp, rượu thuốc"},
            {"name": "Đông Chí", "month": 12, "day": 22, "season": "Đông", "eat": "Cháo gà, canh hầm xương", "buy": "Gạo nếp, đậu xanh làm bánh"}
        ]

        self.ngay_dan_gian = {
            1: ("Lưỡi trai", "Mồng một"), 2: ("Lá lúa", "Mùng hai"), 3: ("Câu liêm", "Mùng ba"),
            4: ("Lưỡi liềm", "Mùng bốn"), 5: ("Liềm giật", "Mùng năm"), 6: ("Thật trăng", "Mùng sáu"),
            7: ("Trăng non", "Mùng bảy"), 8: ("Trăng khuyết", "Mùng tám"), 9: ("Trăng non", "Mùng chín"),
            10: ("Trăng náu", "Mười rằm"), 11: ("Trăng sáng", "Mười một"), 12: ("Trăng sáng", "Mười hai"),
            13: ("Trăng sáng", "Mười ba"), 14: ("Trăng gần tròn", "Mười bốn"), 15: ("Trăng treo", "Rằm / Mười sáu"),
            16: ("Trăng tròn", "Mười sáu"), 17: ("Sảy giường chiếu", "Mười bảy"), 18: ("Rám trấu", "Mười tám"),
            19: ("Đụn dịn", "Mười chín"), 20: ("Giấc tốt", "Hăm mươi"), 21: ("Nửa đêm", "Hăm mốt"),
            22: ("Thế nào", "Hăm hai"), 23: ("Thế ấy", "Hăm ba"), 24: ("Ở đâu", "Hăm bốn"),
            25: ("Ở đấy", "Hăm lăm"), 26: ("Đã vậy", "Hăm sáu"), 27: ("Làm sao", "Hăm bảy"),
            28: ("Thế nào", "Hăm tám"), 29: ("Thế ấy", "Hăm chín"), 30: ("Chẳng thấy trăng", "Ba mươi")
        }

        self.folk_data = {
            1: {"solarTerms": "Lập Xuân – Vũ Thủy – Tết", "buy": "Muối, hương, hoa", "worship": "Gia tiên, Thổ Công", "eat": "Đồ chay rằm Giêng, bánh trôi chay", "avoid": "Ăn mắm tôm đầu năm"},
            2: {"solarTerms": "Kinh Trập – Xuân Phân", "buy": "Rau mới, cá tươi", "worship": "Tết Hàn Thực (3/3)", "eat": "Đồ mát, thanh nhẹ", "avoid": "Sát sinh nhiều"},
            3: {"solarTerms": "Thanh Minh – Cốc Vũ", "buy": "Hương hoa, xôi chè", "worship": "Mộ tổ tiên, Thổ địa", "eat": "Canh măng, cơm nếp", "avoid": "Ăn đồ tanh"},
            4: {"solarTerms": "Lập Hạ – Tiểu Mãn", "buy": "Trái cây, đậu đen", "worship": "Lễ ra mùa", "eat": "Chè đậu đen, rau ngót", "avoid": "Ăn đồ nặng"},
            5: {"solarTerms": "Mang Chủng – Hạ Chí", "buy": "Rượu nếp, thịt vịt", "worship": "Tết giết sâu bọ", "eat": "Rượu nếp, vịt luộc", "avoid": "Ăn đồ sống"},
            6: {"solarTerms": "Tiểu Thử – Đại Thử", "buy": "Đậu xanh, chè xanh", "worship": "Cầu mưa thuận gió hòa", "eat": "Đồ mát, canh chua", "avoid": "Rượu bia, đồ cay"},
            7: {"solarTerms": "Lập Thu – Xử Thử", "buy": "Hương hoa, vàng mã", "worship": "Phật, gia tiên, cô hồn", "eat": "Đồ chay, cháo", "avoid": "Đi đêm"},
            8: {"solarTerms": "Bạch Lộ – Thu Phân", "buy": "Bánh trung thu, cốm", "worship": "Rằm Trung Thu", "eat": "Bánh nướng, bánh dẻo", "avoid": "Đổ rác sau rằm"},
            9: {"solarTerms": "Hàn Lộ – Sương Giáng", "buy": "Gừng, rượu, cá trắm", "worship": "Lễ Tạ Điền", "eat": "Đồ ấm, cháo gừng", "avoid": "Ăn đồ lạnh"},
            10: {"solarTerms": "Lập Đông – Tiểu Tuyết", "buy": "Cá, thịt bò, dưa muối", "worship": "Lễ cơm mới", "eat": "Đồ ấm, cá kho", "avoid": "Nước lạnh"},
            11: {"solarTerms": "Đại Tuyết – Đông Chí", "buy": "Thịt, gạo nếp, rượu", "worship": "Đông Chí", "eat": "Bánh trôi, cháo gạo", "avoid": "Ăn chua"},
            12: {"solarTerms": "Tiểu Hàn – Đại Hàn", "buy": "Vôi, muối, cá chép", "worship": "Táo Quân, tất niên", "eat": "Bánh chưng, thịt đông", "avoid": "Cãi cọ cuối năm"}
        }

        self.number_meanings = {
            1: "Số 1 - Khởi đầu, độc lập, lãnh đạo.", 2: "Số 2 - Cân bằng, hợp tác.",
            3: "Số 3 - Sáng tạo, phát triển.", 4: "Số 4 - Ổn định, vững chắc.",
            5: "Số 5 - Thay đổi, tự do.", 6: "Số 6 - Hài hòa, gia đình.",
            7: "Số 7 - Tâm linh, trí tuệ.", 8: "Số 8 - Phát triển, thịnh vượng.",
            9: "Số 9 - Hoàn thiện, viên mãn."
        }

        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure('TNotebook', background='#1E1E2E', borderwidth=0)
        self.style.configure('TNotebook.Tab', font=('Segoe UI', 10, 'bold'), padding=[12, 8])

        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.tab1 = tk.Frame(self.notebook, bg="#2A2A3C")
        self.tab2 = tk.Frame(self.notebook, bg="#2A2A3C")
        self.tab3 = tk.Frame(self.notebook, bg="#2A2A3C")
        self.tab4 = tk.Frame(self.notebook, bg="#2A2A3C")

        self.notebook.add(self.tab1, text=" Tab 1: Tra Cứu Âm Lịch & Dân Gian ")
        self.notebook.add(self.tab2, text=" Tab 2: 24 Tiết Khí & Món Ăn ")
        self.notebook.add(self.tab3, text=" Tab 3: Tra Cứu Số Chuyên Sâu ")
        self.notebook.add(self.tab4, text=" Tab 4: Quản Lý & Tra Cứu Nguồn TXT ")

        self.xay_dung_tab1()
        self.xay_dung_tab2()
        self.xay_dung_tab3()
        self.xay_dung_tab4()

        if self.cac_file_nguon:
            self.nap_du_lieu_tu_cac_file()

    # --- QUẢN LÝ CẤU HÌNH & NHẬT KÝ ĐỘNG ---
    def tai_cau_hinh_cu(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.cac_file_nguon = data.get("nguon_txt", [])
            except:
                pass

    def luu_cau_hinh(self):
        data = {
            "script_su_dung": f"{TEN_SCRIPT}.py",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "nguon_txt": self.cac_file_nguon
        }
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    def ghi_nhap_nhat_ky(self, duong_dan_json):
        index_data = {
            "script_su_dung": f"{TEN_SCRIPT}.py",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "file_json_xuat": duong_dan_json,
            "cac_file_nguon_da_quet": self.cac_file_nguon
        }
        with open(INDEX_FILE, "w", encoding="utf-8") as f:
            json.dump(index_data, f, ensure_ascii=False, indent=4)

    def chay_ngam_xu_ly(self):
        print(f"[{TEN_SCRIPT}] Đang chạy ngầm tự động quét và xuất file...")
        self.tai_cau_hinh_cu()
        now = datetime.now()
        thu_muc_nguon = os.path.dirname(self.cac_file_nguon[0]) if self.cac_file_nguon else "MacDinh"
        ten_thu_muc_gon = os.path.basename(thu_muc_nguon) if thu_muc_nguon else "Data"
        timestamp_str = now.strftime("%Y%m%d_%H%M%S")
        ten_file_json = f"{TEN_SCRIPT}_{ten_thu_muc_gon}_{timestamp_str}.json"
        
        os.makedirs(DEFAULT_DIR, exist_ok=True)
        path_save = os.path.join(DEFAULT_DIR, ten_file_json)
        
        data_json = {
            "metadata": {
                "script_su_dung": f"{TEN_SCRIPT}.py",
                "timestamp": now.strftime("%Y-%m-%d %H:%M:%S"),
                "date_minus_7_days": (now - timedelta(days=7)).strftime("%Y-%m-%d"),
                "date_plus_7_days": (now + timedelta(days=7)).strftime("%Y-%m-%d"),
                "absolute_paths": self.cac_file_nguon,
                "source_directory": thu_muc_nguon
            },
            "people": [],
            "ref_numbers": [1, 2, 3, 4, 5, 6, 7, 8, 9],
            "custom_tabs": [{"link": "https://www.youtube.com"}],
            "events": self.danh_sach_su_kien
        }
        with open(path_save, "w", encoding="utf-8") as f:
            json.dump(data_json, f, ensure_ascii=False, indent=4)
        self.ghi_nhap_nhat_ky(path_save)
        print(f"[{TEN_SCRIPT}] Hoàn tất xuất ngầm tại: {path_save}")

    # --- CÁC THUẬT TOÁN THIÊN VĂN & LỊCH ---
    def tinh_tiet_khi_hien_tai(self, dt):
        y = dt.year
        danh_sach_nam = []
        for tk in self.tiet_khi_danh_sach:
            for yr in [y - 1, y, y + 1]:
                try:
                    danh_sach_nam.append({
                        "name": tk["name"],
                        "date": datetime(yr, tk["month"], tk["day"]),
                        "season": tk["season"],
                        "eat": tk["eat"],
                        "buy": tk["buy"]
                    })
                except:
                    pass
        danh_sach_nam.sort(key=lambda x: x["date"])

        hien_tai, tiep_theo = None, None
        for i in range(len(danh_sach_nam) - 1):
            if danh_sach_nam[i]["date"] <= dt < danh_sach_nam[i+1]["date"]:
                hien_tai = danh_sach_nam[i]
                tiep_theo = danh_sach_nam[i+1]
                break
        if not hien_tai:
            hien_tai, tiep_theo = danh_sach_nam[0], danh_sach_nam[1]
        so_ngay_con_lai = (tiep_theo["date"] - dt).days
        return hien_tai, tiep_theo, so_ngay_con_lai

    def jd_from_date(self, dd, mm, yy):
        if mm <= 2:
            yy -= 1
            mm += 12
        A = yy // 100
        B = 2 - A + (A // 4)
        return int(365.25 * (yy + 4716)) + int(30.6001 * (mm + 1)) + dd + B - 1524

    def new_moon(self, k):
        T = k / 1236.85
        T2 = T * T
        dr = math.pi / 180
        Jd1 = 2415020.75933 + 29.53058868 * k + 0.0001178 * T2
        Jd1 += 0.00033 * math.sin((166.56 + 132.87 * T) * dr)
        M = 359.2242 + 29.10535608 * k
        Mpr = 306.0253 + 385.81691806 * k
        return Jd1 + (0.1734 * math.sin(M * dr) - 0.4068 * math.sin(Mpr * dr))

    def get_new_moon_day(self, k, time_zone):
        return math.floor(self.new_moon(k) + 0.5 + time_zone / 24)

    def get_sun_longitude(self, jdn, time_zone):
        T = (jdn - 2451545.5 - time_zone / 24) / 36525
        M = 357.52910 + 35999.05030 * T
        L0 = 280.46645 + 36000.76983 * T
        DL = 1.914600 * math.sin(M * math.pi / 180)
        L = (L0 + DL) * math.pi / 180
        L = L - 2 * math.pi * math.floor(L / (2 * math.pi))
        return math.floor(L / (math.pi / 6))

    def get_lunar_month_11(self, yy, time_zone):
        off = self.jd_from_date(31, 12, yy) - 2415021
        k = math.floor(off / 29.530588853)
        nm = self.get_new_moon_day(k, time_zone)
        if self.get_sun_longitude(nm, time_zone) >= 9:
            nm = self.get_new_moon_day(k - 1, time_zone)
        return nm

    def get_leap_month_offset(self, a11, time_zone):
        k = math.floor((a11 - 2415021) / 29.530588853)
        i = 1
        arc = self.get_sun_longitude(self.get_new_moon_day(k + i, time_zone), time_zone)
        last = arc
        while arc != last and i < 14:
            last = arc
            i += 1
            arc = self.get_sun_longitude(self.get_new_moon_day(k + i, time_zone), time_zone)
        return i - 1

    def solar_to_lunar(self, dd, mm, yy, time_zone=7):
        dayNumber = self.jd_from_date(dd, mm, yy)
        k = math.floor((dayNumber - 2415021) / 29.530588853)
        monthStart = self.get_new_moon_day(k + 1, time_zone)
        if monthStart > dayNumber:
            monthStart = self.get_new_moon_day(k, time_zone)
        a11 = self.get_lunar_month_11(yy, time_zone)
        b11 = a11
        if a11 >= monthStart:
            lunarYear = yy
            a11 = self.get_lunar_month_11(yy - 1, time_zone)
        else:
            lunarYear = yy + 1
            b11 = self.get_lunar_month_11(yy + 1, time_zone)
        lunarDay = dayNumber - monthStart + 1
        diff = math.floor((monthStart - a11) / 29)
        lunarLeap, lunarMonth = 0, diff + 11
        if b11 - a11 > 365:
            leapMonthDiff = self.get_leap_month_offset(a11, time_zone)
            if diff >= leapMonthDiff:
                lunarMonth = diff + 10
                if diff == leapMonthDiff:
                    lunarLeap = 1
        if lunarMonth > 12: lunarMonth -= 12
        if lunarMonth >= 11 and diff < 4: lunarYear -= 1
        return {"day": lunarDay, "month": lunarMonth, "year": lunarYear, "leap": lunarLeap}

    # --- XÂY DỰNG CÁC TAB GIAO DIỆN ---
    def xay_dung_tab1(self):
        lbl = tk.Label(self.tab1, text="TRA CỨU ÂM LỊCH, TIẾT KHÍ & ĐẾM NGƯỢC THỜI GIAN", font=("Segoe UI", 11, "bold"), fg="#00FFC8", bg="#2A2A3C")
        lbl.pack(pady=10)

        f_input = tk.Frame(self.tab1, bg="#2A2A3C")
        f_input.pack(pady=5)

        tk.Label(f_input, text="Chọn ngày Dương lịch (DD/MM/YYYY):", fg="#FFF", bg="#2A2A3C", font=("Segoe UI", 10)).pack(side=tk.LEFT, padx=5)
        self.entry_solar = tk.Entry(f_input, font=("Segoe UI", 10), width=15)
        self.entry_solar.pack(side=tk.LEFT, padx=5)
        self.entry_solar.insert(0, datetime.now().strftime("%d/%m/%Y"))

        btn_chuyen = tk.Button(f_input, text="🔄 Tra Cứu Chi Tiết", font=("Segoe UI", 10, "bold"), bg="#00FFC8", fg="#000", command=self.xu_ly_chuyen_doi)
        btn_chuyen.pack(side=tk.LEFT, padx=10)

        self.txt_ket_qua_tab1 = tk.Text(self.tab1, wrap=tk.WORD, font=("Consolas", 10), bg="#1E1E2E", fg="#FFF", height=24)
        self.txt_ket_qua_tab1.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)
        self.xu_ly_chuyen_doi()

    def xu_ly_chuyen_doi(self):
        val = self.entry_solar.get().strip()
        try:
            dt = datetime.strptime(val, "%d/%m/%Y")
            d, m, y = dt.day, dt.month, dt.year
            lunar = self.solar_to_lunar(d, m, y, 7)
            weekdays = ["Chủ Nhật", "Thứ Hai", "Thứ Ba", "Thứ Tư", "Thứ Năm", "Thứ Sáu", "Thứ Bảy"]
            thu = weekdays[dt.weekday()]
            nhuan_str = " (Nhuận)" if lunar["leap"] == 1 else ""
            ngay_info = self.ngay_dan_gian.get(lunar["day"], ("Không rõ", "Thường"))
            m_data = self.folk_data.get(lunar["month"], self.folk_data[1])
            hien_tai, tiep_theo, con_lai = self.tinh_tiet_khi_hien_tai(dt)

            text_info = (
                f"☀️ [DƯƠNG LỊCH]: Ngày {d} tháng {m} năm {y} ({thu})\n"
                f"🌙 [ÂM LỊCH THIÊN VĂN]: Ngày {lunar['day']} tháng {lunar['month']}{nhuan_str} năm {lunar['year']}\n"
                f"--------------------------------------------------\n"
                f"⚡ [TIẾT KHÍ HIỆN TẠI]: {hien_tai['name']} (Mùa {hien_tai['season']})\n"
                f"⏳ Đếm ngược: Còn **{con_lai} ngày** nữa sẽ chuyển sang tiết **{tiep_theo['name']}**\n"
                f"🌿 TÊN GỌI DÂN GIAN TRĂNG NGÀY {lunar['day']} ÂM LỊCH: {ngay_info[0]} ({ngay_info[1]})\n"
                f"--------------------------------------------------\n"
                f"🍽️ NÊN ĂN GÌ & PHÒNG BỆNH:\n"
                f"   • Món ăn theo tiết khí: {hien_tai['eat']}\n"
                f"   • Món ăn dân gian tháng {lunar['month']}: {m_data['eat']}\n"
            )
            self.txt_ket_qua_tab1.delete("1.0", tk.END)
            self.txt_ket_qua_tab1.insert(tk.END, text_info)
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi tính toán: {e}")

    def xay_dung_tab2(self):
        lbl = tk.Label(self.tab2, text="24 TIẾT KHÍ & MÓN ĂN PHÒNG TRÁNH", font=("Segoe UI", 12, "bold"), fg="#FFD700", bg="#2A2A3C")
        lbl.pack(pady=10)
        columns = ("Tiết Khí", "Mùa", "Đồ Mua Sắm", "Món Ăn Phòng Tránh")
        self.tree_tietkhi = ttk.Treeview(self.tab2, columns=columns, show="headings", height=20)
        for col in columns:
            self.tree_tietkhi.heading(col, text=col)
            self.tree_tietkhi.column(col, width=220, anchor="center")
        self.tree_tietkhi.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)

        # Đổi tên biến vòng lặp thành 'tiet_khi_item' để tránh trùng lặp với module 'tk'
        for tiet_khi_item in self.tiet_khi_danh_sach:
            self.tree_tietkhi.insert("", "end", values=(tiet_khi_item["name"], tiet_khi_item["season"], tiet_khi_item["buy"], tiet_khi_item["eat"]))

    def xay_dung_tab3(self):
        lbl = tk.Label(self.tab3, text="TRA CỨU Ý NGHĨA SỐ DÂN GIAN", font=("Segoe UI", 12, "bold"), fg="#00FFC8", bg="#2A2A3C")
        lbl.pack(pady=15)
        f_num = tk.Frame(self.tab3, bg="#2A2A3C")
        f_num.pack(pady=5)
        tk.Label(f_num, text="Nhập con số (1-9):", fg="#FFF", bg="#2A2A3C", font=("Segoe UI", 10)).pack(side=tk.LEFT, padx=5)
        self.entry_num = tk.Entry(f_num, font=("Segoe UI", 10), width=10)
        self.entry_num.pack(side=tk.LEFT, padx=5)
        self.entry_num.insert(0, "1")
        btn_tracuu = tk.Button(f_num, text="🔍 Tra Cứu Ý Nghĩa", font=("Segoe UI", 10, "bold"), bg="#00FFC8", fg="#000", command=self.tracuu_so)
        btn_tracuu.pack(side=tk.LEFT, padx=10)
        self.txt_ket_qua_tab3 = tk.Text(self.tab3, wrap=tk.WORD, font=("Consolas", 10), bg="#1E1E2E", fg="#FFF", height=18)
        self.txt_ket_qua_tab3.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)

    def tracuu_so(self):
        val = self.entry_num.get().strip()
        if val.isdigit():
            n = int(val)
            desc = self.number_meanings.get(n, "Không có ý nghĩa.")
            self.txt_ket_qua_tab3.delete("1.0", tk.END)
            self.txt_ket_qua_tab3.insert(tk.END, f"📊 Ý nghĩa số {n}:\n{desc}\n")

    # --- TAB 4: QUẢN LÝ 4-5 TỆP TXT, TÌM KIẾM LINH HOẠT & LƯU LỊCH SỬ ---
    def xay_dung_tab4(self):
        lbl = tk.Label(self.tab4, text="QUẢN LÝ DỮ LIỆU TXT LINH HOẠT & TRA CỨU / LƯU LỊCH SỬ", font=("Segoe UI", 12, "bold"), fg="#FF6B6B", bg="#2A2A3C")
        lbl.pack(pady=5)

        f_src = tk.Frame(self.tab4, bg="#2A2A3C")
        f_src.pack(pady=5, fill=tk.X, padx=15)
        
        btn_load_multi = tk.Button(f_src, text="📂 Chọn 4-5 Tệp Nguồn TXT", font=("Segoe UI", 10, "bold"), bg="#FFA07A", fg="#000", command=self.tai_nhieu_file_txt)
        btn_load_multi.pack(side=tk.LEFT, padx=5)

        btn_export = tk.Button(f_src, text="💾 Xuất JSON (Hộp thoại Save As)", font=("Segoe UI", 10, "bold"), bg="#00FFC8", fg="#000", command=self.xuat_json_dong)
        btn_export.pack(side=tk.RIGHT, padx=5)

        # Khung các ô tìm kiếm nâng cao
        f_search = tk.LabelFrame(self.tab4, text=" 🔍 Ô Tìm Kiếm Nâng Cao & Giống Dữ Liệu Tệp TXT ", fg="#00FFC8", bg="#2A2A3C", font=("Segoe UI", 9, "bold"))
        f_search.pack(pady=5, padx=15, fill=tk.X)

        f_s1 = tk.Frame(f_search, bg="#2A2A3C")
        f_s1.pack(fill=tk.X, padx=5, pady=3)
        
        tk.Label(f_s1, text="Tên:", fg="#FFF", bg="#2A2A3C").pack(side=tk.LEFT)
        self.s_ten = tk.Entry(f_s1, width=12)
        self.s_ten.pack(side=tk.LEFT, padx=3)

        tk.Label(f_s1, text="Ngày(DD/MM/YYYY):", fg="#FFF", bg="#2A2A3C").pack(side=tk.LEFT)
        self.s_ngay = tk.Entry(f_s1, width=10)
        self.s_ngay.pack(side=tk.LEFT, padx=3)

        tk.Label(f_s1, text="Quý:", fg="#FFF", bg="#2A2A3C").pack(side=tk.LEFT)
        self.s_quy = tk.Entry(f_s1, width=4)
        self.s_quy.pack(side=tk.LEFT, padx=3)

        tk.Label(f_s1, text="Tháng:", fg="#FFF", bg="#2A2A3C").pack(side=tk.LEFT)
        self.s_thang = tk.Entry(f_s1, width=4)
        self.s_thang.pack(side=tk.LEFT, padx=3)

        f_s2 = tk.Frame(f_search, bg="#2A2A3C")
        f_s2.pack(fill=tk.X, padx=5, pady=3)

        tk.Label(f_s2, text="Tuần:", fg="#FFF", bg="#2A2A3C").pack(side=tk.LEFT)
        self.s_tuan = tk.Entry(f_s2, width=4)
        self.s_tuan.pack(side=tk.LEFT, padx=3)

        tk.Label(f_s2, text="Giờ:", fg="#FFF", bg="#2A2A3C").pack(side=tk.LEFT)
        self.s_gio = tk.Entry(f_s2, width=4)
        self.s_gio.pack(side=tk.LEFT, padx=3)

        tk.Label(f_s2, text="Phút:", fg="#FFF", bg="#2A2A3C").pack(side=tk.LEFT)
        self.s_phut = tk.Entry(f_s2, width=4)
        self.s_phut.pack(side=tk.LEFT, padx=3)

        tk.Label(f_s2, text="Bệnh mắc:", fg="#FFF", bg="#2A2A3C").pack(side=tk.LEFT)
        self.s_benh = tk.Entry(f_s2, width=15)
        self.s_benh.pack(side=tk.LEFT, padx=3)

        btn_tim = tk.Button(f_s2, text="🔍 Dò Tìm", bg="#FFD700", fg="#000", font=("Segoe UI", 9, "bold"), command=self.thuc_hien_do_tim)
        btn_tim.pack(side=tk.LEFT, padx=5)

        btn_luu_LS = tk.Button(f_s2, text="💾 Lưu Lịch Sử Vào TXT", bg="#FF6B6B", fg="#FFF", font=("Segoe UI", 9, "bold"), command=self.luu_lich_su_vao_txt)
        btn_luu_LS.pack(side=tk.LEFT, padx=5)

        columns = ("STT", "Nguồn TXT", "Tên / Sự Kiện", "Thời Điểm / Ngày", "Bệnh / Ghi Chú", "Thông Tin Khác")
        self.tree_tab4 = ttk.Treeview(self.tab4, columns=columns, show="headings", height=12)
        for col in columns:
            self.tree_tab4.heading(col, text=col)
            self.tree_tab4.column(col, width=180, anchor="center")
        self.tree_tab4.pack(fill=tk.BOTH, expand=True, padx=15, pady=5)

    def tai_nhieu_file_txt(self):
        initial_dir = os.path.dirname(self.cac_file_nguon[0]) if self.cac_file_nguon else (DEFAULT_DIR if os.path.exists(DEFAULT_DIR) else "/")
        paths = filedialog.askopenfilenames(
            title="Chọn từ 4 đến 5 tệp nguồn TXT",
            initialdir=initial_dir,
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if not paths:
            return
        
        self.cac_file_nguon = list(paths)
        self.luu_cau_hinh()
        self.nap_du_lieu_tu_cac_file()
        messagebox.showinfo("Thành công", f"Đã chọn và ghi nhớ {len(self.cac_file_nguon)} tệp nguồn TXT!")

    def nap_du_lieu_tu_cac_file(self):
        self.danh_sach_su_kien.clear()
        for item in self.tree_tab4.get_children():
            self.tree_tab4.delete(item)

        for path in self.cac_file_nguon:
            ten_file = os.path.basename(path)
            try:
                with open(path, "r", encoding="utf-8-sig", errors="ignore") as f:
                    for line in f:
                        dong = line.strip()
                        if not dong: continue
                        parts = [p.strip() for p in dong.split("\t") if p.strip()]
                        if len(parts) < 2:
                            parts = [p.strip() for p in dong.split("  ") if p.strip()]
                        
                        ten = parts[0] if len(parts) > 0 else "Không rõ"
                        ngay = parts[1] if len(parts) > 1 else ""
                        benh = parts[2] if len(parts) > 2 else "Khỏe mạnh"
                        ghichu = parts[3] if len(parts) > 3 else ""

                        self.danh_sach_su_kien.append({
                            "nguon": ten_file, "ten": ten, "ngay": ngay, "benh": benh, "ghichu": ghichu
                        })
                        self.tree_tab4.insert("", "end", values=(
                            len(self.danh_sach_su_kien), ten_file, ten, ngay, benh, ghichu
                        ))
            except Exception as e:
                print(f"Lỗi đọc file {ten_file}: {e}")

    def thuc_hien_do_tim(self):
        k_ten = self.s_ten.get().strip().lower()
        k_ngay = self.s_ngay.get().strip()
        k_benh = self.s_benh.get().strip().lower()

        for item in self.tree_tab4.get_children():
            self.tree_tab4.delete(item)

        stt = 1
        for ev in self.danh_sach_su_kien:
            match = True
            if k_ten and k_ten not in ev["ten"].lower(): match = False
            if k_ngay and k_ngay not in ev["ngay"]: match = False
            if k_benh and k_benh not in ev["benh"].lower(): match = False

            if match:
                self.tree_tab4.insert("", "end", values=(
                    stt, ev["nguon"], ev["ten"], ev["ngay"], ev["benh"], ev["ghichu"]
                ))
                stt += 1

    def luu_lich_su_vao_txt(self):
        if not self.cac_file_nguon:
            messagebox.showwarning("Cảnh báo", "Chưa có tệp nguồn TXT nào được chọn làm đích lưu!")
            return
        
        target_txt = self.cac_file_nguon[0]
        t_ten = self.s_ten.get().strip() or "Khách"
        t_ngay = self.s_ngay.get().strip() or datetime.now().strftime("%d/%m/%Y")
        t_benh = self.s_benh.get().strip() or "Bình thường"
        
        dong_moi = f"{t_ten}\t{t_ngay}\t{t_benh}\tĐược lưu lúc {datetime.now().strftime('%H:%M:%S %d/%m/%Y')}\n"
        try:
            with open(target_txt, "a", encoding="utf-8") as f:
                f.write(dong_moi)
            messagebox.showinfo("Thành công", f"Đã lưu lịch sử mới vào tệp:\n{target_txt}")
            self.nap_du_lieu_tu_cac_file()
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể lưu vào file: {e}")

    # --- XUẤT JSON ĐỘNG THEO HỘP THOẠI `asksaveasfilename` ---
    def xuat_json_dong(self):
        now = datetime.now()
        thu_muc_nguon = os.path.dirname(self.cac_file_nguon[0]) if self.cac_file_nguon else DEFAULT_DIR
        ten_thu_muc_gon = os.path.basename(thu_muc_nguon) if thu_muc_nguon else "Data"
        timestamp_str = now.strftime("%Y%m%d_%H%M%S")
        
        # Công thức đặt tên chuẩn: [TênScript]_[TênThưMụcNguồn]_[YYYYMMDD_HHMMSS].json[cite: 2]
        default_json_name = f"{TEN_SCRIPT}_{ten_thu_muc_gon}_{timestamp_str}.json"

        os.makedirs(DEFAULT_DIR, exist_ok=True)
        path_save = filedialog.asksaveasfilename(
            title="Lưu tệp JSON động",
            initialdir=DEFAULT_DIR,
            initialfile=default_json_name,
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if not path_save:
            return

        data_json = {
            "metadata": {
                "script_su_dung": f"{TEN_SCRIPT}.py",
                "timestamp": now.strftime("%Y-%m-%d %H:%M:%S"),
                "date_minus_7_days": (now - timedelta(days=7)).strftime("%Y-%m-%d"),
                "date_plus_7_days": (now + timedelta(days=7)).strftime("%Y-%m-%d"),
                "absolute_paths": self.cac_file_nguon,
                "source_directory": thu_muc_nguon
            },
            "people": [{"name": ev.get("ten"), "condition": ev.get("benh")} for ev in self.danh_sach_su_kien],
            "ref_numbers": [1, 2, 3, 4, 5, 6, 7, 8, 9],
            "custom_tabs": [{"tab_name": "Tab 4", "source_files": self.cac_file_nguon}],
            "events": self.danh_sach_su_kien
        }

        try:
            with open(path_save, "w", encoding="utf-8") as f:
                json.dump(data_json, f, ensure_ascii=False, indent=4)
            self.ghi_nhap_nhat_ky(path_save)
            messagebox.showinfo("Thành công", f"Đã xuất file JSON động thành công tại:\n{path_save}")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể lưu file JSON: {e}")

if __name__ == "__main__":
    # Mặc định chạy ngầm; thêm tham số `--gui` để hiển thị giao diện[cite: 2]
    che_do_gui = "--gui" in sys.argv
    
    if che_do_gui:
        root = tk.Tk()
        app = UngDungLichChuyenSau(root, la_chedo_gui=True)
        root.mainloop()
    else:
        root = tk.Tk()
        root.withdraw()
        app = UngDungLichChuyenSau(root, la_chedo_gui=False)
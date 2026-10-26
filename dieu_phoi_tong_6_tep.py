# -*- coding: utf-8 -*-
import os
import sys
import json
import subprocess
from datetime import datetime, timedelta
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

# 1. Định danh động theo tên tệp Python hiện tại
SCRIPT_NAME = os.path.splitext(os.path.basename(__file__))[0]
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Thư mục lưu kết quả chuẩn trên GitHub / Local
THU_MUC_MAC_DINH = os.path.join(BASE_DIR, "KET_QUA_JSON")
CONFIG_FILE = os.path.join(BASE_DIR, f"config_{SCRIPT_NAME}.json")
DAYS_TO_KEEP = 7

class QuanLyVaGieuPhoiFullApp:
    def __init__(self, root, headless=False):
        self.root = root
        self.config = self.load_config()
        self.thu_muc_luu_hien_tai = self.config.get("thu_muc_luu", THU_MUC_MAC_DINH)
        self.template_txt_file = os.path.join(self.thu_muc_luu_hien_tai, f"template_lich_su_{SCRIPT_NAME}.txt")
        self.thuong_luu_txt_file = os.path.join(self.thu_muc_luu_hien_tai, "THUONGLUU.txt")
        self.benh_tat_txt_file = os.path.join(self.thu_muc_luu_hien_tai, "danh_sach_benh.txt")
        self.index_file_dynamic = os.path.join(self.thu_muc_luu_hien_tai, f"index_{SCRIPT_NAME}_quan_ly.json")
        self.source_dir_name = os.path.basename(BASE_DIR) or "ThuMucGoc"

        if headless:
            self.run_background_task(is_headless=True)
            return

        self.root.title(f"Hệ Thống Điều Phối & Quản Lý Tra Cứu ({SCRIPT_NAME}.py)")
        self.root.geometry("1150x900")
        self.setup_ui()

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
        }

    def save_config(self, thu_muc_luu):
        try:
            data = {
                "script_su_dung": SCRIPT_NAME,
                "thu_muc_luu": thu_muc_luu,
                "cap_nhat_moi_nhat": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"Lỗi lưu cấu hình: {e}")

    def setup_ui(self):
        # Tạo Notebook chứa các Tab
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=5, pady=5)

        # ================= TAB 1: Quản lý & Lịch sử gốc =================
        self.tab_main = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_main, text=" 📊 Quản Lý & Lịch Sử ")
        self.setup_tab_main()

        # ================= TAB 2: Tab Mới - Tính Toán & Lưu Trữ Bệnh Tật =================
        self.tab_calc = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_calc, text=" 📝 Tính Toán & Lưu Trữ THUONGLUU ")
        self.setup_tab_calc()

        self.load_data_to_table()
        self.load_thuongluu_data_to_table()

    def setup_tab_main(self):
        frame_nhap = tk.LabelFrame(self.tab_main, text=" 1. Bộ Lọc, Tìm Kiếm Tên, Thời Gian, Bệnh Lý & Thư Mục ", font=("Arial", 10, "bold"))
        frame_nhap.pack(fill="x", padx=10, pady=10, ipady=5)

        tk.Label(frame_nhap, text="Thư mục lưu JSON:", font=("Arial", 9, "bold")).grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.lbl_thumuc = tk.Label(frame_nhap, text=self.thu_muc_luu_hien_tai, fg="blue", font=("Arial", 9))
        self.lbl_thumuc.grid(row=0, column=1, columnspan=3, sticky="w", padx=5, pady=5)
        tk.Button(frame_nhap, text="📁 Đổi Thư Mục Lưu", bg="#607D8B", fg="white", command=self.chon_thu_muc_luu).grid(row=0, column=4, padx=5, pady=5)

        tk.Label(frame_nhap, text="Tìm kiếm tên:", font=("Arial", 9, "bold")).grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.ent_tim_kiem_ten = tk.Entry(frame_nhap, width=30)
        self.ent_tim_kiem_ten.grid(row=1, column=1, columnspan=3, sticky="w", padx=5, pady=5)
        self.ent_tim_kiem_ten.bind("<KeyRelease>", lambda e: self.filter_table())

        labels = ["Năm", "Quý", "Tháng", "Tuần", "Ngày", "Giờ", "Phút"]
        self.time_entries = {}
        now = datetime.now()
        defaults = [now.year, (now.month - 1) // 3 + 1, now.month, now.isocalendar()[1], now.day, now.hour, now.minute]

        for i, lbl in enumerate(labels):
            r = 2 if i < 4 else 3
            c = (i % 4) * 2
            tk.Label(frame_nhap, text=f"{lbl}:").grid(row=r, column=c, sticky="e", padx=2, pady=2)
            ent = tk.Entry(frame_nhap, width=8)
            ent.insert(0, str(defaults[i]))
            ent.grid(row=r, column=c+1, sticky="w", padx=2, pady=2)
            self.time_entries[lbl.lower()] = ent

        tk.Label(frame_nhap, text="Bệnh bị mắc:", font=("Arial", 9, "bold")).grid(row=4, column=0, sticky="w", padx=5, pady=5)
        self.ent_benh = tk.Entry(frame_nhap, width=40)
        self.ent_benh.grid(row=4, column=1, columnspan=3, sticky="w", padx=5, pady=5)

        frame_btn = tk.Frame(self.tab_main)
        frame_btn.pack(fill="x", padx=10, pady=5)

        tk.Button(frame_btn, text="💾 Lưu Lịch Sử Vào Tệp Mẫu TXT", bg="#2196F3", fg="white", font=("Arial", 9, "bold"), command=self.luu_vao_file_txt).pack(side="left", padx=5)
        tk.Button(frame_btn, text="🚀 Chạy Quét & Xuất JSON (Hộp Thoại Lưu Động)", bg="#4CAF50", fg="white", font=("Arial", 9, "bold"), command=lambda: self.run_background_task(is_headless=False)).pack(side="left", padx=5)

        frame_table = tk.LabelFrame(self.tab_main, text=" 2. Bảng Lịch Sử & Kết Quả Tra Cứu ", font=("Arial", 10, "bold"))
        frame_table.pack(fill="both", expand=True, padx=10, pady=10)

        self.tree = ttk.Treeview(frame_table, columns=("Ten", "ThoiGian", "BenhLy"), show="headings")
        self.tree.heading("Ten", text="Tên Nhân Sự / Đối Tượng")
        self.tree.heading("ThoiGian", text="Thời Gian (Năm/Quý/Tháng/Tuần/Ngày/Giờ/Phút)")
        self.tree.heading("BenhLy", text="Bệnh Bị Mắc / Nội Dung")

        self.tree.column("Ten", width=180, anchor="w")
        self.tree.column("ThoiGian", width=350, anchor="w")
        self.tree.column("BenhLy", width=250, anchor="w")
        self.tree.pack(side="left", fill="both", expand=True, padx=5, pady=5)

        scroll = ttk.Scrollbar(frame_table, orient="vertical", command=self.tree.yview)
        scroll.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=scroll.set)

    def setup_tab_calc(self):
        frame_top = tk.LabelFrame(self.tab_calc, text=" Nhập Liệu Thời Gian, Tên & Bệnh Tật ", font=("Arial", 10, "bold"))
        frame_top.pack(fill="x", padx=10, pady=10, ipady=5)

        # Hàng 0: Nhập thời gian chi tiết (Giờ, Phút, Ngày, Tháng, Năm)
        tk.Label(frame_top, text="Giờ (1-1440):", font=("Arial", 9, "bold")).grid(row=0, column=0, sticky="e", padx=5, pady=5)
        self.ent_gio = tk.Entry(frame_top, width=10)
        self.ent_gio.insert(0, "1")
        self.ent_gio.grid(row=0, column=1, sticky="w", padx=5, pady=5)

        tk.Label(frame_top, text="Phút:", font=("Arial", 9, "bold")).grid(row=0, column=2, sticky="e", padx=5, pady=5)
        self.ent_phut = tk.Entry(frame_top, width=10)
        self.ent_phut.insert(0, datetime.now().strftime("%M"))
        self.ent_phut.grid(row=0, column=3, sticky="w", padx=5, pady=5)

        tk.Label(frame_top, text="Ngày:", font=("Arial", 9, "bold")).grid(row=0, column=4, sticky="e", padx=5, pady=5)
        self.ent_ngay = tk.Entry(frame_top, width=10)
        self.ent_ngay.insert(0, datetime.now().strftime("%d"))
        self.ent_ngay.grid(row=0, column=5, sticky="w", padx=5, pady=5)

        tk.Label(frame_top, text="Tháng:", font=("Arial", 9, "bold")).grid(row=1, column=0, sticky="e", padx=5, pady=5)
        self.ent_thang = tk.Entry(frame_top, width=10)
        self.ent_thang.insert(0, datetime.now().strftime("%m"))
        self.ent_thang.grid(row=1, column=1, sticky="w", padx=5, pady=5)

        tk.Label(frame_top, text="Năm sinh (hoặc Năm):", font=("Arial", 9, "bold")).grid(row=1, column=2, sticky="e", padx=5, pady=5)
        self.ent_nam = tk.Entry(frame_top, width=10)
        self.ent_nam.insert(0, "2000")
        self.ent_nam.grid(row=1, column=3, sticky="w", padx=5, pady=5)

        # Hàng 2: Chọn tên từ danh sách tab_1
        tk.Label(frame_top, text="Chọn Tên (tab_1):", font=("Arial", 9, "bold")).grid(row=2, column=0, sticky="e", padx=5, pady=5)
        self.combo_ten = ttk.Combobox(frame_top, width=28, state="readonly")
        self.combo_ten.grid(row=2, column=1, columnspan=3, sticky="w", padx=5, pady=5)
        self.cap_nhat_danh_sach_tab1()

        # Hàng 3: Chọn hoặc thêm mới danh sách bệnh tật trong txt
        tk.Label(frame_top, text="Bệnh Tật (TXT):", font=("Arial", 9, "bold")).grid(row=3, column=0, sticky="e", padx=5, pady=5)
        self.combo_benh = ttk.Combobox(frame_top, width=28)
        self.combo_benh.grid(row=3, column=1, columnspan=3, sticky="w", padx=5, pady=5)
        self.cap_nhat_danh_sach_benh()

        tk.Button(frame_top, text="💾 Lưu Lại Vào THUONGLUU.txt", bg="#FF5722", fg="white", font=("Arial", 10, "bold"), command=self.xu_ly_va_luu_thuongluu).grid(row=4, column=1, columnspan=3, pady=10, sticky="w")

        # Bảng hiển thị nội dung THUONGLUU.txt
        frame_tbl_thuongluu = tk.LabelFrame(self.tab_calc, text=" Dữ liệu trong THUONGLUU.txt ", font=("Arial", 10, "bold"))
        frame_tbl_thuongluu.pack(fill="both", expand=True, padx=10, pady=10)

        self.tree_thuongluu = ttk.Treeview(frame_tbl_thuongluu, columns=("Col1", "Col2", "Col3", "Col4", "Col5"), show="headings")
        self.tree_thuongluu.heading("Col1", text="Cột 1 (Thương tính toán)")
        self.tree_thuongluu.heading("Col2", text="Tên")
        self.tree_thuongluu.heading("Col3", text="Thời Gian Nhập")
        self.tree_thuongluu.heading("Col4", text="Bệnh Tật")
        self.tree_thuongluu.heading("Col5", text="Trạng thái lọc (Bảng 1-6)")

        self.tree_thuongluu.column("Col1", width=220, anchor="w")
        self.tree_thuongluu.column("Col2", width=180, anchor="w")
        self.tree_thuongluu.column("Col3", width=200, anchor="w")
        self.tree_thuongluu.column("Col4", width=200, anchor="w")
        self.tree_thuongluu.column("Col5", width=250, anchor="w")
        self.tree_thuongluu.pack(side="left", fill="both", expand=True, padx=5, pady=5)

        scroll_tl = ttk.Scrollbar(frame_tbl_thuongluu, orient="vertical", command=self.tree_thuongluu.yview)
        scroll_tl.pack(side="right", fill="y")
        self.tree_thuongluu.configure(yscrollcommand=scroll_tl.set)

    def cap_nhat_danh_sach_tab1(self):
        danh_sach_ten = []
        if os.path.exists(self.template_txt_file):
            try:
                with open(self.template_txt_file, "r", encoding="utf-8") as f:
                    for line in f:
                        if "|" in line:
                            parts = [p.strip() for p in line.strip().split("|")]
                            if len(parts) >= 3:
                                ten = parts[0].replace("Tên:", "").strip()
                                if ten and ten not in danh_sach_ten:
                                    danh_sach_ten.append(ten)
            except Exception:
                pass
        if not danh_sach_ten:
            danh_sach_ten = ["Khuyết Danh"]
        self.combo_ten['values'] = danh_sach_ten
        self.combo_ten.current(0)

    def cap_nhat_danh_sach_benh(self):
        danh_sach_b = []
        if os.path.exists(self.benh_tat_txt_file):
            try:
                with open(self.benh_tat_txt_file, "r", encoding="utf-8") as f:
                    for line in f:
                        b = line.strip()
                        if b and b not in danh_sach_b:
                            danh_sach_b.append(b)
            except Exception:
                pass
        if not danh_sach_b:
            danh_sach_b = ["Cảm cúm", "Đau đầu", "Đau bụng", "Huyết áp"]
        self.combo_benh['values'] = danh_sach_b
        if danh_sach_b:
            self.combo_benh.set(danh_sach_b[0])

    def lay_so_lieu_tu_6_bang(self):
        """Lấy các số có sẵn từ 6 tệp / thư mục bảng 1 tới bảng 6 để so sánh"""
        danh_sach_so = set()
        print("🔍 [KIỂM TRA] Bắt đầu quét dữ liệu từ các thư mục muc_1 đến muc_6...")
        for i in range(1, 7):
            duong_dan_muc = os.path.join(BASE_DIR, f"muc_{i}")
            if os.path.exists(duong_dan_muc) and os.path.isdir(duong_dan_muc):
                print(f"   📁 Đã tìm thấy thư mục: {duong_dan_muc}")
                for file in os.listdir(duong_dan_muc):
                    duong_dan_file = os.path.join(duong_dan_muc, file)
                    if os.path.isfile(duong_dan_file):
                        try:
                            with open(duong_dan_file, "r", encoding="utf-8", errors="ignore") as f:
                                content = f.read()
                                import re
                                numbers = re.findall(r'\d+', content)
                                print(f"      📄 Đọc tệp {file}: tìm thấy {len(numbers)} số.")
                                for num in numbers:
                                    danh_sach_so.add(int(num))
                        except Exception as e:
                            print(f"      ❌ Lỗi đọc tệp {file}: {e}")
            else:
                print(f"   ⚠️ Không tìm thấy thư mục: {duong_dan_muc}")
        print(f"✅ [KIỂM TRA] Tổng số lượng số duy nhất thu thập từ 6 bảng: {len(danh_sach_so)}")
        return danh_sach_so

    def xu_ly_va_luu_thuongluu(self):
        ten_chon = self.combo_ten.get().strip()
        benh_chon = self.combo_benh.get().strip()

        if not benh_chon:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn hoặc nhập tên bệnh tật!")
            return

        try:
            os.makedirs(os.path.dirname(self.benh_tat_txt_file), exist_ok=True)
            danh_sach_hien_tai = list(self.combo_benh['values'])
            if benh_chon not in danh_sach_hien_tai:
                danh_sach_hien_tai.append(benh_chon)
                with open(self.benh_tat_txt_file, "w", encoding="utf-8") as f:
                    for b in danh_sach_hien_tai:
                        f.write(f"{b}\n")
                self.combo_benh['values'] = danh_sach_hien_tai
        except Exception:
            pass

        try:
            gio_val = int(self.ent_gio.get().strip())
            phut_val = int(self.ent_phut.get().strip())
            ngay_val = int(self.ent_ngay.get().strip())
            thang_val = int(self.ent_thang.get().strip())
            nam_val = int(self.ent_nam.get().strip())
            
            if not (1 <= gio_val <= 1440):
                messagebox.showerror("Lỗi", "Số thứ tự giờ/phút phải nằm trong khoảng từ 1 tới 1440!")
                return

            now = datetime.now()
            dt_sinh = datetime(nam_val, thang_val, ngay_val)
            chenh_lech_ngay = (now - dt_sinh).days
            if chenh_lech_ngay < 0:
                chenh_lech_ngay = abs(chenh_lech_ngay)

            thuong_nhan_24 = chenh_lech_ngay * 24
            phan_nguyen = thuong_nhan_24 // gio_val
            phan_du = thuong_nhan_24 % gio_val

            du_nguyen = phan_nguyen % 1000
            du_du = phan_du % 1000

            cac_so_co_san = self.lay_so_lieu_tu_6_bang()

            ket_qua_loc = []
            giu_nguyen = True
            
            for val in [du_nguyen, du_du]:
                if val in cac_so_co_san:
                    giu_nguyen = False
                    ket_qua_loc.append(f"Trùng ({val}) -> Bỏ")
                else:
                    ket_qua_loc.append(f"Mới ({val}) -> Giữ")

            trang_thai_str = " | ".join(ket_qua_loc)
            cot_1_val = f"Thương: {thuong_nhan_24} | Nguyên:{phan_nguyen}(%{1000}={du_nguyen}) | Dư:{phan_du}(%{1000}={du_du})"
            thoi_gian_nhap_str = f"Ngày {ngay_val}/{thang_val}/{nam_val} - Giờ {gio_val}:{phut_val}"

            dong_ghi = f"{cot_1_val} | Tên:{ten_chon} | {thoi_gian_nhap_str} | Bệnh:{benh_chon} | TrạngThái:{trang_thai_str}\n"

            os.makedirs(os.path.dirname(self.thuong_luu_txt_file), exist_ok=True)
            with open(self.thuong_luu_txt_file, "a", encoding="utf-8") as f:
                f.write(dong_ghi)

            messagebox.showinfo("Thành công", f"Đã lưu thành công vào THUONGLUU.txt!\nTrạng thái: {trang_thai_str}")
            self.load_thuongluu_data_to_table()

        except ValueError:
            messagebox.showerror("Lỗi", "Vui lòng nhập các giá trị số hợp lệ cho thời gian và năm sinh!")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Có lỗi xảy ra: {e}")

    def load_thuongluu_data_to_table(self):
        for item in self.tree_thuongluu.get_children():
            self.tree_thuongluu.delete(item)
        if os.path.exists(self.thuong_luu_txt_file):
            try:
                with open(self.thuong_luu_txt_file, "r", encoding="utf-8") as f:
                    for line in f:
                        if "|" in line:
                            parts = [p.strip() for p in line.strip().split("|")]
                            if len(parts) >= 5:
                                col1 = parts[0]
                                ten = parts[1].replace("Tên:", "")
                                thoigian = parts[2]
                                benh = parts[3].replace("Bệnh:", "")
                                trangthai = parts[4].replace("TrạngThái:", "")
                                self.tree_thuongluu.insert("", "end", values=(col1, ten, thoigian, benh, trangthai))
            except Exception:
                pass

    def chon_thu_muc_luu(self):
        thu_muc_chon = filedialog.askdirectory(title="Chọn thư mục lưu tệp JSON", initialdir=self.thu_muc_luu_hien_tai)
        if thu_muc_chon:
            self.thu_muc_luu_hien_tai = thu_muc_chon
            self.lbl_thumuc.config(text=thu_muc_chon)
            self.template_txt_file = os.path.join(thu_muc_chon, f"template_lich_su_{SCRIPT_NAME}.txt")
            self.thuong_luu_txt_file = os.path.join(thu_muc_chon, "THUONGLUU.txt")
            self.benh_tat_txt_file = os.path.join(thu_muc_chon, "danh_sach_benh.txt")
            self.index_file_dynamic = os.path.join(thu_muc_chon, f"index_{SCRIPT_NAME}_quan_ly.json")
            self.save_config(thu_muc_chon)
            messagebox.showinfo("Thành công", f"Đã đổi thư mục lưu đích thành:\n{thu_muc_chon}")
            self.load_data_to_table()
            self.load_thuongluu_data_to_table()
            self.cap_nhat_danh_sach_tab1()

    def luu_vao_file_txt(self):
        ten_tk = self.ent_tim_kiem_ten.get().strip() or "Khuyết Danh"
        t_vals = [self.time_entries[k].get().strip() for k in ["năm", "quý", "tháng", "tuần", "ngày", "giờ", "phút"]]
        time_str = f"Năm:{t_vals[0]} | Quý:{t_vals[1]} | Tháng:{t_vals[2]} | Tuần:{t_vals[3]} | Ngày:{t_vals[4]} | Giờ:{t_vals[5]} | Phút:{t_vals[6]}"
        benh = self.ent_benh.get().strip()

        if not benh:
            messagebox.showwarning("Cảnh báo", "Vui lòng nhập thông tin bệnh bị mắc trước khi lưu!")
            return

        dong_du_lieu = f"Tên:{ten_tk} | {time_str} | Bệnh:{benh}\n"
        try:
            os.makedirs(os.path.dirname(self.template_txt_file), exist_ok=True)
            with open(self.template_txt_file, "a", encoding="utf-8") as f:
                f.write(dong_du_lieu)
            messagebox.showinfo("Thành công", f"Đã lưu lịch sử vào tệp mẫu:\n{self.template_txt_file}")
            self.load_data_to_table()
            self.cap_nhat_danh_sach_tab1()
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể ghi tệp mẫu txt: {e}")

    def load_data_to_table(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        if os.path.exists(self.template_txt_file):
            try:
                with open(self.template_txt_file, "r", encoding="utf-8") as f:
                    for line in f:
                        if "|" in line:
                            parts = [p.strip() for p in line.strip().split("|")]
                            if len(parts) >= 3:
                                ten_val = parts[0].replace("Tên:", "")
                                time_val = " | ".join(parts[1:-1])
                                benh_val = parts[-1].replace("Bệnh:", "")
                                self.tree.insert("", "end", values=(ten_val, time_val, benh_val))
            except Exception:
                pass

    def filter_table(self):
        keyword = self.ent_tim_kiem_ten.get().strip().lower()
        for item in self.tree.get_children():
            self.tree.delete(item)
        if os.path.exists(self.template_txt_file):
            try:
                with open(self.template_txt_file, "r", encoding="utf-8") as f:
                    for line in f:
                        if "|" in line:
                            parts = [p.strip() for p in line.strip().split("|")]
                            if len(parts) >= 3:
                                ten_val = parts[0].replace("Tên:", "")
                                time_val = " | ".join(parts[1:-1])
                                benh_val = parts[-1].replace("Bệnh:", "")
                                if keyword in ten_val.lower() or not keyword:
                                    self.tree.insert("", "end", values=(ten_val, time_val, benh_val))
            except Exception:
                pass

    def thuc_thi_cac_chuong_trinh_con(self):
        dem_thanh_cong = 0
        sub_folders_data = []
        danh_sach_file_quet = []

        print("🚀 [KIỂM TRA] Bắt đầu quét các thư mục con từ muc_1 đến muc_6...")
        for i in range(1, 7):
            ten_thu_muc = f"muc_{i}"
            duong_dan_con = os.path.join(BASE_DIR, ten_thu_muc)
            if os.path.exists(duong_dan_con) and os.path.isdir(duong_dan_con):
                sub_folders_data.append(ten_thu_muc)
                print(f"   📁 Thư mục nguồn tồn tại: {duong_dan_con}")
                for file in os.listdir(duong_dan_con):
                    duong_dan_file = os.path.join(duong_dan_con, file)
                    if os.path.isfile(duong_dan_file):
                        danh_sach_file_quet.append(duong_dan_file)
                        print(f"      📄 Tìm thấy tệp nguồn quét: {file}")
                    if file.lower().endswith(".py") and not "chay" in file.lower():
                        try:
                            cmd = [sys.executable, duong_dan_file]
                            process = subprocess.Popen(cmd, cwd=duong_dan_con)
                            process.wait(timeout=30)
                            dem_thanh_cong += 1
                            print(f"      ▶️ Thực thi thành công script con: {file}")
                        except Exception as e:
                            print(f"      ❌ Lỗi thực thi script con {file}: {e}")
            else:
                print(f"   ⚠️ Thư mục không tồn tại: {duong_dan_con}")
        print(f"✅ [KIỂM TRA] Quét xong. Tổng số tệp nguồn ghi nhận: {len(danh_sach_file_quet)}")
        return dem_thanh_cong, sub_folders_data, danh_sach_file_quet

    def run_background_task(self, is_headless=False):
        try:
            print("⚙️ [CHẠY NGẦM] Bắt đầu tác vụ tự động / Headless trên GitHub...")
            thu_muc_luu = self.thu_muc_luu_hien_tai
            os.makedirs(thu_muc_luu, exist_ok=True)
            self.save_config(thu_muc_luu)

            print(f"   - Thư mục lưu kết quả đích: {thu_muc_luu}")
            print(f"   - Tệp lịch sử mẫu: {self.template_txt_file} (Tồn tại: {os.path.exists(self.template_txt_file)})")
            print(f"   - Tệp THUONGLUU.txt: {self.thuong_luu_txt_file} (Tồn tại: {os.path.exists(self.thuong_luu_txt_file)})")
            print(f"   - Tệp danh sách bệnh: {self.benh_tat_txt_file} (Tồn tại: {os.path.exists(self.benh_tat_txt_file)})")

            dem_thanh_cong, sub_folders_data, danh_sach_file_quet = self.thuc_thi_cac_chuong_trinh_con()
            if os.path.exists(self.template_txt_file):
                danh_sach_file_quet.append(self.template_txt_file)
            if os.path.exists(self.thuong_luu_txt_file):
                danh_sach_file_quet.append(self.thuong_luu_txt_file)

            now = datetime.now()
            thoi_gian_str = now.strftime("%Y%m%d_%H%M%S")
            default_output_filename = f"{SCRIPT_NAME}_{self.source_dir_name}_{thoi_gian_str}.json"

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
                                    "benh_mac": parts[-1].replace("Bệnh:", "")
                                })

            ket_qua_tong_ket = []
            ref_numbers_all = [123, 456, 789]
            for rec in lich_su_records:
                item_ket_qua = {
                    "tab": "Tab_Tong_Hop",
                    "ten": rec["ten"],
                    "ngay_sinh": "2000-01-01",
                    "gio_sinh": "00:00",
                    "chi_so": "Ngày",
                    "gia_tri_goc": 100,
                    "phan_nguyen": 10,
                    "mod_1000_nguyen": 10,
                    "trung_nguyen": 10 in ref_numbers_all,
                    "phan_du": 0,
                    "mod_1000_du": 0,
                    "trung_du": 0 in ref_numbers_all,
                    "can_bu": 5,
                    "thong_tin_du": f"Hết vòng đến bệnh: {rec['benh_mac']}",
                    "canh_bao_col": "Không cảnh báo",
                    "moc_thoi_gian": now.strftime("%Y-%m-%d %H:%M:%S"),
                    "link_video": "https://www.youtube.com/watch?v=example",
                    "chi_tiet_trung_khop": "Nguyên: 10 (%1000=10) | Dư: 0 (%1000=0)"
                }
                ket_qua_tong_ket.append(item_ket_qua)

            payload = {
                "metadata": {
                    "script_su_dung": f"{SCRIPT_NAME}.py",
                    "timestamp": now.strftime("%Y-%m-%d %H:%M:%S"),
                    "date_minus_7_days": (now - timedelta(days=7)).strftime("%Y-%m-%d"),
                    "date_plus_7_days": (now + timedelta(days=7)).strftime("%Y-%m-%d"),
                    "thu_muc_nguon": self.source_dir_name,
                    "file_nguon_quet": danh_sach_file_quet
                },
                "people": lich_su_records,
                "ref_numbers": ref_numbers_all,
                "tabs_data": sub_folders_data,
                "ket_qua_tong_ket": ket_qua_tong_ket
            }

            if is_headless:
                out_path = os.path.join(thu_muc_luu, default_output_filename)
                with open(out_path, "w", encoding="utf-8") as f:
                    json.dump(payload, f, ensure_ascii=False, indent=4)
                print(f"[{SCRIPT_NAME}.py] ✅ Đã tự động xuất JSON ngầm tại: {out_path}")
            else:
                out_path = filedialog.asksaveasfilename(
                    title="Lưu tệp JSON chuẩn",
                    initialdir=thu_muc_luu,
                    initialfile=default_output_filename,
                    defaultextension=".json",
                    filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")]
                )
                if not out_path:
                    return
                with open(out_path, "w", encoding="utf-8") as f:
                    json.dump(payload, f, ensure_ascii=False, indent=4)
                messagebox.showinfo("Thành công", f"Đã xuất JSON tại:\n{out_path}")

        except Exception as e:
            if is_headless:
                print(f"[{SCRIPT_NAME}.py] ❌ Lỗi chạy ngầm: {e}")
                sys.exit(1)
            else:
                messagebox.showerror("Lỗi", f"Lỗi thực thi: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1].lower() == "--gui":
        root = tk.Tk()
        app = QuanLyVaGieuPhoiFullApp(root, headless=False)
        root.mainloop()
    else:
        QuanLyVaGieuPhoiFullApp(None, headless=True)

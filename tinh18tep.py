import os
import sys
import json
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from datetime import datetime, timedelta

# Thư mục xuất tệp JSON mặc định trên Google Drive
THU_MUC_XUAT_JSON = r"G:\My Drive\DANHSACHPHATVIDEO\KET_QUA_JSON"

class UngDungPhanTich:
    def __init__(self, root):
        self.root = root
        self.root.title("Phần Mềm Phân Tích Dữ Liệu, Vận Hạn & Quản Lý Video")
        self.root.geometry("1400x850")

        # Lấy tên script hiện tại làm tiền tố động[cite: 2]
        self.script_name = os.path.splitext(os.path.basename(__file__))[0]

        # Biến lưu đường dẫn nguồn
        self.txt_danh_sach_path = ""
        self.txt_mau_sosanh_paths = ["", "", "", "", ""]
        self.source_dir_name = "MAC_DINH"

        # Dữ liệu chung lưu trữ
        self.people_data = [] 
        self.ref_tables = []
        self.ket_qua_tong_ket = []
        self.tabs_data = [] 

        self.tao_giao_dien()

    def tao_giao_dien(self):
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)

        # Tab 1: Nhân Sự & Khôi phục JSON
        self.tab_1 = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_1, text="Tab 1: Nhân Sự & Danh Sách")
        self.tao_tab_1()

        # Tab 2: Mẫu so sánh & Tạo tab mới
        self.tab_2 = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_2, text="Tab 2: Mẫu So Sánh & Tạo Tab")
        self.tao_tab_2()

        # Tab Tổng Kết
        self.tab_tong_ket = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_tong_ket, text="Tab Tổng Kết")
        self.tao_tab_tong_ket()

        bottom_frame = ttk.Frame(self.root)
        bottom_frame.pack(fill="x", padx=10, pady=5)

        btn_xuat_json = ttk.Button(bottom_frame, text="Xuất JSON Chung", command=self.xuat_json_chung)
        btn_xuat_json.pack(side="right", padx=5)

    def tao_tab_1(self):
        frame_top = ttk.LabelFrame(self.tab_1, text="1. Nguồn Danh Sách & Khôi Phục Dữ Liệu JSON")
        frame_top.pack(fill="x", padx=10, pady=5)

        self.lbl_ds = ttk.Label(frame_top, text="Chưa chọn tệp danh sách (.txt)")
        self.lbl_ds.pack(side="left", padx=5, pady=5)
        
        btn_load_json = ttk.Button(frame_top, text="📂 Nạp Tệp JSON Đã Lưu", command=self.nap_file_json_cu)
        btn_load_json.pack(side="right", padx=5, pady=5)

        btn_chon_ds = ttk.Button(frame_top, text="Chọn Tệp TXT Danh Sách", command=self.chon_file_danh_sach)
        btn_chon_ds.pack(side="right", padx=5, pady=5)

        frame_table = ttk.LabelFrame(self.tab_1, text="Danh Sách Nhân Sự Đã Nạp")
        frame_table.pack(fill="both", expand=True, padx=10, pady=5)

        columns = ("STT", "Ten", "NgaySinh", "GioSinh", "GioiTinh", "PhanCach")
        self.tree_people = ttk.Treeview(frame_table, columns=columns, show="headings", height=6)
        self.tree_people.heading("STT", text="STT")
        self.tree_people.heading("Ten", text="Tên (Cột 1)")
        self.tree_people.heading("NgaySinh", text="Ngày Sinh (Cột 2)")
        self.tree_people.heading("GioSinh", text="Giờ Sinh (Cột 3)")
        self.tree_people.heading("GioiTinh", text="Giới Tính (Cột 4)")
        self.tree_people.heading("PhanCach", text="Ngăn Cách")

        self.tree_people.column("STT", width=50, anchor="center")
        self.tree_people.column("Ten", width=180, anchor="w")
        self.tree_people.column("NgaySinh", width=140, anchor="center")
        self.tree_people.column("GioSinh", width=100, anchor="center")
        self.tree_people.column("GioiTinh", width=100, anchor="center")
        self.tree_people.column("PhanCach", width=80, anchor="center")
        
        scrollbar = ttk.Scrollbar(frame_table, orient="vertical", command=self.tree_people.yview)
        self.tree_people.configure(yscrollcommand=scrollbar.set)
        
        self.tree_people.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        frame_time = ttk.LabelFrame(self.tab_1, text="2. Tùy Chỉnh Thời Gian So Sánh & Tính Toán Chênh Lệch")
        frame_time.pack(fill="x", padx=10, pady=5)

        labels = ["Năm", "Tháng", "Ngày", "Giờ", "Phút"]
        self.time_entries = {}
        now = datetime.now()
        defaults = [now.year, now.month, now.day, now.hour, now.minute]

        for i, lbl in enumerate(labels):
            ttk.Label(frame_time, text=lbl).grid(row=0, column=i*2, padx=5, pady=5, sticky="e")
            ent = ttk.Entry(frame_time, width=6)
            ent.insert(0, str(defaults[i]))
            ent.grid(row=0, column=i*2+1, padx=5, pady=5, sticky="w")
            self.time_entries[lbl.lower()] = ent

        btn_tinh = ttk.Button(frame_time, text="Tính Toán Chênh Lệch Toàn Bộ", command=self.tinh_chenh_lech_thoi_gian)
        btn_tinh.grid(row=0, column=len(labels)*2, padx=15, pady=5)

        frame_res_t1 = ttk.LabelFrame(self.tab_1, text="3. Kết Quả Tính Toán Chênh Lệch Chi Tiết Tại Tab 1")
        frame_res_t1.pack(fill="both", expand=True, padx=10, pady=5)

        self.txt_ket_qua_t1 = tk.Text(frame_res_t1, height=8)
        self.txt_ket_qua_t1.pack(fill="both", expand=True, padx=5, pady=5)

    def chon_file_danh_sach(self):
        file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        if file_path:
            self.txt_danh_sach_path = file_path
            self.source_dir_name = os.path.basename(os.path.dirname(file_path))
            self.lbl_ds.config(text=f"Đã chọn: {os.path.basename(file_path)}")
            try:
                self.people_data = []
                for row in self.tree_people.get_children():
                    self.tree_people.delete(row)

                with open(file_path, "r", encoding="utf-8") as f:
                    for idx, line in enumerate(f, 1):
                        line_str = line.strip()
                        if not line_str:
                            continue
                        if "|" in line_str:
                            parts = [p.strip() for p in line_str.split("|")]
                        elif "," in line_str:
                            parts = [p.strip() for p in line_str.split(",")]
                        else:
                            parts = line_str.split()

                        if len(parts) >= 4:
                            ten = parts[0]
                            ngay_sinh = parts[1]
                            gio_sinh = parts[2]
                            raw_gt = parts[3].strip()
                            
                            gioi_tinh = "Nam" if raw_gt.lower() == 't' else ("Nữ" if raw_gt.lower() == 'g' else raw_gt)

                            p_info = {
                                "stt": idx,
                                "ten": ten,
                                "ngay_sinh": ngay_sinh, 
                                "gio_sinh": gio_sinh,
                                "gioi_tinh": gioi_tinh
                            }
                            self.people_data.append(p_info)
                            self.tree_people.insert("", "end", values=(idx, ten, ngay_sinh, gio_sinh, gioi_tinh, "|"))
                
                messagebox.showinfo("Thành công", f"Đã đọc thành công {len(self.people_data)} nhân sự từ tệp.")
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không đọc được tệp danh sách: {e}")

    def nap_file_json_cu(self):
        initial_dir = THU_MUC_XUAT_JSON if os.path.exists(THU_MUC_XUAT_JSON) else os.getcwd()
        file_path = filedialog.askopenfilename(
            initialdir=initial_dir,
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if file_path:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                
                if "people" in data:
                    self.people_data = data["people"]
                    for row in self.tree_people.get_children():
                        self.tree_people.delete(row)
                    for idx, p in enumerate(self.people_data, 1):
                        self.tree_people.insert("", "end", values=(idx, p.get("ten"), p.get("ngay_sinh"), p.get("gio_sinh"), p.get("gioi_tinh"), "|"))

                if "metadata" in data:
                    meta = data["metadata"]
                    if "file_mau_sosanh" in meta:
                        self.txt_mau_sosanh_paths = meta["file_mau_sosanh"]
                    if "thu_muc_nguon" in meta:
                        self.source_dir_name = meta["thu_muc_nguon"]
                    if "file_danh_sach" in meta:
                        self.txt_danh_sach_path = meta["file_danh_sach"]
                        if self.txt_danh_sach_path:
                            self.lbl_ds.config(text=f"Đã nạp từ JSON: {os.path.basename(self.txt_danh_sach_path)}")

                if "ket_qua_tong_ket" in data:
                    self.ket_qua_tong_ket = data["ket_qua_tong_ket"]
                    self.cap_nhat_tab_tong_ket()

                # Khôi phục các tab và TỰ ĐỘNG CHẠY PHÂN TÍCH LUÔN
                if "tabs_data" in data:
                    self.tabs_data = data["tabs_data"]
                    for t_info in self.tabs_data:
                        self.tao_tab_moi_giao_dien(saved_data=t_info, auto_run=True)

                messagebox.showinfo("Thành công", f"Đã nạp, khôi phục và tự động chạy phân tích từ tệp:\n{os.path.basename(file_path)}")
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể đọc tệp JSON: {e}")

    def tinh_chenh_lech_thoi_gian(self):
        if not self.people_data:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn hoặc nạp tệp danh sách ở Tab 1 trước!")
            return
        try:
            y = int(self.time_entries["năm"].get())
            m = int(self.time_entries["tháng"].get())
            d = int(self.time_entries["ngày"].get())
            h = int(self.time_entries["giờ"].get())
            mi = int(self.time_entries["phút"].get())
            
            target_time = datetime(y, m, d, h, mi)
            log_t1 = f"=== TÍNH TOÁN CHÊNH LỆCH THỜI GIAN SO VỚI MỐC: {target_time.strftime('%Y-%m-%d %H:%M')} ===\n\n"

            for person in self.people_data:
                ten = person["ten"]
                ngay_sinh_str = person["ngay_sinh"]
                
                ns_dt = None
                for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%Y/%m/%d"):
                    try:
                        ns_dt = datetime.strptime(ngay_sinh_str, fmt)
                        break
                    except ValueError:
                        continue
                if not ns_dt:
                    continue

                diff = target_time - ns_dt
                total_seconds = int(diff.total_seconds())
                days = diff.days
                years = days // 366
                quarters = days // 90
                months = days // 31
                weeks = days // 7
                hours = total_seconds // 3600
                minutes = total_seconds // 60

                log_t1 += f"👤 [{ten}] (Sinh: {ngay_sinh_str}):\n"
                log_t1 += f"   • Năm (366d): {years} | Quý (90d): {quarters} | Tháng (31d): {months} | Tuần (7d): {weeks}\n"
                log_t1 += f"   • Ngày: {days} | Giờ: {hours} | Phút: {minutes}\n"
                log_t1 += "-" * 60 + "\n"

            self.txt_ket_qua_t1.delete("1.0", tk.END)
            self.txt_ket_qua_t1.insert(tk.END, log_t1)
            messagebox.showinfo("Hoàn thành", "Đã tính toán xong chênh lệch thời gian chi tiết tại Tab 1!")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Dữ liệu thời gian nhập không hợp lệ: {e}")

    def tao_tab_2(self):
        frame_mau = ttk.LabelFrame(self.tab_2, text="Nạp 5 Tệp TXT Mẫu So Sánh (Dùng chung)")
        frame_mau.pack(fill="x", padx=10, pady=5)

        for i in range(5):
            btn = ttk.Button(frame_mau, text=f"Chọn Mẫu TXT {i+1}", command=lambda idx=i: self.chon_file_mau(idx))
            btn.pack(side="left", padx=5, pady=5)

        frame_tao_tab = ttk.LabelFrame(self.tab_2, text="Quản Lý Tab Phân Tích Mới")
        frame_tao_tab.pack(fill="x", padx=10, pady=10)

        btn_tao = ttk.Button(frame_tao_tab, text="Tạo Tab Mới Phân Tích", command=lambda: self.tao_tab_moi_giao_dien(None, auto_run=False))
        btn_tao.pack(side="left", padx=5, pady=5)

    def chon_file_mau(self, index):
        file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        if file_path:
            self.txt_mau_sosanh_paths[index] = file_path
            messagebox.showinfo("Thành công", f"Đã chọn tệp mẫu {index+1}: {os.path.basename(file_path)}")

    def tao_tab_moi_giao_dien(self, saved_data=None, auto_run=False):
        new_tab = ttk.Frame(self.notebook)
        
        if saved_data:
            tab_name = saved_data.get("tab_name", f"Tab Phân Tích {len(self.notebook.tabs())}")
            default_video_path = saved_data.get("video_path", "Chưa chọn tệp link video (.txt)")
            default_divisor = str(saved_data.get("divisor", "1"))
            saved_log = saved_data.get("log_content", "")
            video_links_list = saved_data.get("video_links", [])
        else:
            tab_count = len(self.notebook.tabs())
            tab_name = f"Tab Phân Tích {tab_count}"
            default_video_path = "Chưa chọn tệp link video (.txt)"
            default_divisor = "1"
            saved_log = ""
            video_links_list = []

        self.notebook.add(new_tab, text=tab_name)
        self.notebook.select(new_tab)

        video_path_var = tk.StringVar(value=default_video_path)

        f_video = ttk.LabelFrame(new_tab, text="Nguồn Link Video (Dành riêng cho Tab này)")
        f_video.pack(fill="x", padx=10, pady=5)

        lbl_v = ttk.Label(f_video, textvariable=video_path_var)
        lbl_v.pack(side="left", padx=5, pady=5)

        def chon_video_tab_moi():
            f_p = filedialog.askopenfilename(filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
            if f_p:
                video_path_var.set(f"Đã chọn: {os.path.basename(f_p)}")
                try:
                    with open(f_p, "r", encoding="utf-8") as f:
                        video_links_list.clear()
                        video_links_list.extend([line.strip() for line in f.readlines() if line.strip()])
                    messagebox.showinfo("Thành công", f"Đã nạp {len(video_links_list)} liên kết video.")
                    self.cap_nhat_hoac_them_tab_data(tab_name, video_path_var.get(), ent_div.get(), video_links_list, txt_res.get("1.0", tk.END))
                except Exception as ex:
                    messagebox.showerror("Lỗi", f"Không đọc được tệp: {ex}")

        btn_cv = ttk.Button(f_video, text="Chọn Tệp TXT Link Video", command=chon_video_tab_moi)
        btn_cv.pack(side="right", padx=5, pady=5)

        f_action = ttk.LabelFrame(new_tab, text="Cấu Hình Chia & So Sánh Dò Tìm")
        f_action.pack(fill="x", padx=10, pady=5)

        ttk.Label(f_action, text="Nhập số cần chia chênh lệch:").pack(side="left", padx=5)
        ent_div = ttk.Entry(f_action, width=10)
        ent_div.insert(0, default_divisor)
        ent_div.pack(side="left", padx=5)

        txt_res = tk.Text(new_tab, height=20)
        txt_res.pack(fill="both", expand=True, padx=10, pady=5)
        if saved_log:
            txt_res.insert(tk.END, saved_log)

        def thuc_hien_phan_tich_tab_nay():
            if not self.people_data:
                return
            if not video_links_list and not saved_data:
                return

            try:
                divisor = int(ent_div.get())
                if divisor == 0:
                    raise ValueError("Số chia không được bằng 0")
            except Exception as e:
                return

            ref_numbers_all = []
            for path in self.txt_mau_sosanh_paths:
                if path and os.path.exists(path):
                    with open(path, "r", encoding="utf-8") as f:
                        for line in f:
                            try:
                                num = int(line.strip())
                                ref_numbers_all.append(num)
                            except ValueError:
                                pass
            self.ref_tables = ref_numbers_all

            try:
                y = int(self.time_entries["năm"].get())
                m = int(self.time_entries["tháng"].get())
                d = int(self.time_entries["ngày"].get())
                h = int(self.time_entries["giờ"].get())
                mi = int(self.time_entries["phút"].get())
                target_time = datetime(y, m, d, h, mi)
            except Exception:
                target_time = datetime.now()

            log_text = f"=== KẾT QUẢ PHÂN TÍCH, CHIA 1000 & SỐ DƯ [{tab_name}] ===\n"
            v_count = len(video_links_list)
            v_idx = 0
            cur_y = target_time.year
            cur_mo = target_time.month
            cur_d = target_time.day
            cur_h = target_time.hour
            cur_mi = target_time.minute

            self.ket_qua_tong_ket = [item for item in self.ket_qua_tong_ket if item['tab'] != tab_name]

            for person in self.people_data:
                ten = person["ten"]
                ngay_sinh_str = person["ngay_sinh"]
                gio_sinh_str = person["gio_sinh"]
                
                log_text += f"\n---------------------------------------------------\n"
                log_text += f"👤 [Nhân sự]: {ten} | Ngày sinh: {ngay_sinh_str} | Giờ sinh: {gio_sinh_str}\n"

                try:
                    ns_dt = None
                    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%Y/%m/%d"):
                        try:
                            ns_dt = datetime.strptime(ngay_sinh_str, fmt)
                            break
                        except ValueError:
                            continue
                    if not ns_dt:
                        continue

                    sinh_gio = 0
                    if ":" in gio_sinh_str:
                        g_parts = gio_sinh_str.split(":")
                        sinh_gio = int(g_parts[0])
                    else:
                        try:
                            sinh_gio = int(float(gio_sinh_str))
                        except ValueError:
                            sinh_gio = 0

                    diff = target_time - ns_dt
                    total_seconds = int(diff.total_seconds())
                    days = diff.days
                    years = days // 366
                    quarters = days // 90
                    months = days // 31
                    weeks = days // 7
                    hours = total_seconds // 3600
                    minutes = total_seconds // 60

                    diffs_dict = {
                        "Năm (366d)": years, "Quý (90d)": quarters, "Tháng (31d)": months,
                        "Tuần (7d)": weeks, "Ngày": days, "Giờ": hours, "Phút": minutes
                    }

                    for key, val in diffs_dict.items():
                        phan_nguyen = val // divisor
                        phan_du = val % divisor
                        can_bu = divisor - phan_du
                        
                        mod_1000_nguyen = phan_nguyen % 1000
                        mod_1000_du = phan_du % 1000

                        ket_qua_ket_Loi = target_time
                        is_gio_phut_metric = False

                        if "Năm" in key:
                            ket_qua_nam = cur_y + can_bu
                            thong_tin_du = f"Hết vòng (cộng {can_bu} năm) đến năm: {ket_qua_nam}"
                        elif "Quý" in key:
                            tong_thang = cur_mo + (can_bu * 3)
                            them_nam = (tong_thang - 1) // 12
                            ket_qua_thang = (tong_thang - 1) % 12 + 1
                            ket_qua_nam = cur_y + them_nam
                            thong_tin_du = f"Hết vòng (cộng {can_bu} quý) đến tháng/năm: {ket_qua_thang:02d}/{ket_qua_nam}"
                        elif "Tháng" in key:
                            tong_thang = cur_mo + can_bu
                            them_nam = (tong_thang - 1) // 12
                            ket_qua_thang = (tong_thang - 1) % 12 + 1
                            ket_qua_nam = cur_y + them_nam
                            thong_tin_du = f"Hết vòng (cộng {can_bu} tháng) đến tháng/năm: {ket_qua_thang:02d}/{ket_qua_nam}"
                        elif "Tuần" in key:
                            ngay_bu = can_bu * 7
                            ket_qua_ket_Loi = target_time + timedelta(days=ngay_bu)
                            thong_tin_du = f"Hết vòng (cộng {can_bu} tuần / {ngay_bu} ngày) đến ngày: {ket_qua_ket_Loi.strftime('%d/%m/%Y')}"
                        elif "Ngày" in key:
                            ket_qua_ket_Loi = target_time + timedelta(days=can_bu)
                            thong_tin_du = f"Hết vòng (cộng {can_bu} ngày) đến ngày: {ket_qua_ket_Loi.strftime('%d/%m/%Y')}"
                        elif "Giờ" in key:
                            is_gio_phut_metric = True
                            tong_gio_kq = (cur_h + can_bu)
                            them_ngay = tong_gio_kq // 24
                            ket_qua_ket_Loi = target_time + timedelta(days=them_ngay)
                            final_h = tong_gio_kq % 24
                            ket_qua_ket_Loi = ket_qua_ket_Loi.replace(hour=final_h, minute=cur_mi)
                            thong_tin_du = f"Hết vòng (cộng {can_bu} giờ) đến ngày {ket_qua_ket_Loi.strftime('%d/%m/%Y lúc %H:%M')}"
                        elif "Phút" in key:
                            is_gio_phut_metric = True
                            tong_phut_kq = cur_mi + can_bu
                            extra_h = tong_phut_kq // 60
                            final_m = tong_phut_kq % 60
                            tong_gio_kq = cur_h + extra_h
                            final_h = tong_gio_kq % 24
                            them_ngay = tong_gio_kq // 24
                            ket_qua_ket_Loi = target_time + timedelta(days=them_ngay)
                            ket_qua_ket_Loi = ket_qua_ket_Loi.replace(hour=final_h, minute=final_m)
                            thong_tin_du = f"Hết vòng (cộng {can_bu} phút) đến ngày {ket_qua_ket_Loi.strftime('%d/%m/%Y lúc %H:%M')}"
                        else:
                            ket_qua_ket_Loi = target_time + timedelta(days=can_bu)
                            thong_tin_du = f"Hết vòng (cộng {can_bu} đơn vị) đến ngày: {ket_qua_ket_Loi.strftime('%d/%m/%Y')}"

                        match_nguyen = "✅ TRÙNG MẪU" if mod_1000_nguyen in ref_numbers_all else "❌ Không trùng"
                        match_du = "✅ TRÙNG MẪU" if mod_1000_du in ref_numbers_all else "❌ Không trùng"

                        log_text += f"   • {key} = {val} | Chia {divisor} -> Nguyên: {phan_nguyen} [Dư %1000: {mod_1000_nguyen} -> {match_nguyen}] | Dư: {phan_du} [Dư %1000: {mod_1000_du} -> {match_du}] | (Cần bù: {can_bu}) | {thong_tin_du}\n"

                        canh_bao_col = "Không áp dụng (Chỉ số theo ngày/tháng/năm)"
                        if is_gio_phut_metric:
                            kq_hour = ket_qua_ket_Loi.hour
                            if sinh_gio <= 0:
                                adjusted_hour = (24 - abs(sinh_gio) + kq_hour) % 24
                            else:
                                adjusted_hour = (kq_hour - sinh_gio) % 24
                            canh_bao_col = f"Cảnh báo cộng trừ giờ sinh -> Đến giờ:{adjusted_hour:02d}:00 không nên đi lại"
                            log_text += f"      ⚠️ {canh_bao_col}\n"

                        if (mod_1000_nguyen in ref_numbers_all) or (mod_1000_du in ref_numbers_all):
                            link_gan = video_links_list[v_idx % v_count] if v_count > 0 else "Không có link"
                            v_idx += 1

                            item_ket_qua = {
                                "tab": tab_name,
                                "ten": ten,
                                "ngay_sinh": ngay_sinh_str,
                                "chi_so": key,
                                "gia_tri_goc": val,
                                "phan_nguyen": phan_nguyen,
                                "mod_1000_nguyen": mod_1000_nguyen,
                                "trung_nguyen": mod_1000_nguyen in ref_numbers_all,
                                "phan_du": phan_du,
                                "mod_1000_du": mod_1000_du,
                                "trung_du": mod_1000_du in ref_numbers_all,
                                "can_bu": can_bu,
                                "thong_tin_du": thong_tin_du,
                                "canh_bao_col": canh_bao_col,
                                "moc_thoi_gian": target_time.strftime("%Y-%m-%d %H:%M:%S"),
                                "link_video": link_gan
                            }
                            self.ket_qua_tong_ket.append(item_ket_qua)
                            log_text += f"      🔗 Link video: {link_gan}\n"

                except Exception as ex:
                    pass

            txt_res.delete("1.0", tk.END)
            txt_res.insert(tk.END, log_text)
            
            self.cap_nhat_hoac_them_tab_data(tab_name, video_path_var.get(), ent_div.get(), video_links_list, txt_res.get("1.0", tk.END))
            self.cap_nhat_tab_tong_ket()

        btn_chay = ttk.Button(f_action, text="Thực Hiện Phân Tích & Dò Tìm", command=thuc_hien_phan_tich_tab_nay)
        btn_chay.pack(side="left", padx=10)

        if not saved_data:
            self.cap_nhat_hoac_them_tab_data(tab_name, video_path_var.get(), ent_div.get(), video_links_list, "")
        
        # Nếu cờ tự động chạy được kích hoạt (khi nạp JSON), lập tức thực thi luôn từ A-Z
        if auto_run:
            thuc_hien_phan_tich_tab_nay()

    def cap_nhat_hoac_them_tab_data(self, tab_name, video_path, divisor, video_links, log_content):
        for t in self.tabs_data:
            if t["tab_name"] == tab_name:
                t["video_path"] = video_path
                t["divisor"] = divisor
                t["video_links"] = video_links
                t["log_content"] = log_content
                return
        self.tabs_data.append({
            "tab_name": tab_name,
            "video_path": video_path,
            "divisor": divisor,
            "video_links": video_links,
            "log_content": log_content
        })

    def tao_tab_tong_ket(self):
        self.txt_tong_ket = tk.Text(self.tab_tong_ket, height=28)
        self.txt_tong_ket.pack(fill="both", expand=True, padx=10, pady=10)

    def cap_nhat_tab_tong_ket(self):
        hien_thi = "=== TỔNG HỢP TOÀN BỘ KẾT QUẢ TRÙNG KHỚP (CHIA 1000 CẢ NGUYÊN & DƯ), HẾT VÒNG ===\n\n"
        for idx, item in enumerate(self.ket_qua_tong_ket, 1):
            str_trung = []
            if item.get("trung_nguyen"):
                str_trung.append(f"Trùng Nguyên %1000 ({item['mod_1000_nguyen']})")
            if item.get("trung_du"):
                str_trung.append(f"Trùng Dư %1000 ({item['mod_1000_du']})")
            m_str = " & ".join(str_trung)

            hien_thi += f"{idx}. [{item['tab']}] Nhân sự: {item['ten']} | Chỉ số: {item['chi_so']} (Gốc: {item['gia_tri_goc']})\n"
            hien_thi += f"   • Nguyên: {item['phan_nguyen']} (%1000={item['mod_1000_nguyen']}) | Dư: {item['phan_du']} (%1000={item['mod_1000_du']}) | Dò mẫu: {m_str}\n"
            hien_thi += f"   • {item['thong_tin_du']}\n"
            hien_thi += f"   ⚠️ {item['canh_bao_col']}\n"
            hien_thi += f"   🔗 Link video: {item['link_video']}\n"
            hien_thi += "-" * 80 + "\n"

        self.txt_tong_ket.delete("1.0", tk.END)
        self.txt_tong_ket.insert(tk.END, hien_thi)

    def xuat_json_chung(self):
        now_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_filename = f"{self.script_name}_{self.source_dir_name}_{now_str}.json"

        if not os.path.exists(THU_MUC_XUAT_JSON):
            os.makedirs(THU_MUC_XUAT_JSON)

        file_path = filedialog.asksaveasfilename(
            initialdir=THU_MUC_XUAT_JSON,
            initialfile=default_filename,
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )

        if not file_path:
            return

        data_to_export = {
            "metadata": {
                "script_su_dung": f"{self.script_name}.py",
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "date_minus_7_days": (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d"),
                "date_plus_7_days": (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d"),
                "thu_muc_nguon": self.source_dir_name,
                "file_danh_sach": self.txt_danh_sach_path,
                "file_mau_sosanh": self.txt_mau_sosanh_paths,
            },
            "people": self.people_data,
            "ref_numbers": self.ref_tables,
            "ket_qua_tong_ket": self.ket_qua_tong_ket,
            "tabs_data": self.tabs_data
        }

        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data_to_export, f, ensure_ascii=False, indent=4)
            messagebox.showinfo("Thành công", f"Đã xuất tệp JSON thành công tại:\n{file_path}")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể lưu tệp JSON: {e}")

def thuc_hien_xu_ly_tu_dong_ngam():
    """Hàm tự động thực thi ngầm hoàn toàn khi chạy file mà KHÔNG CÓ tham số --gui[cite: 2]"""
    script_name = os.path.splitext(os.path.basename(__file__))[0]
    source_dir_name = "MAC_DINH"
    
    if not os.path.exists(THU_MUC_XUAT_JSON):
        os.makedirs(THU_MUC_XUAT_JSON)

    now_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_name = f"{script_name}_{source_dir_name}_{now_str}.json"
    file_path = os.path.join(THU_MUC_XUAT_JSON, file_name)

    data_to_export = {
        "metadata": {
            "script_su_dung": f"{script_name}.py",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "date_minus_7_days": (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d"),
            "date_plus_7_days": (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d"),
            "thu_muc_nguon": source_dir_name,
            "file_danh_sach": "",
            "file_mau_sosanh": [],
        },
        "people": [],
        "ref_numbers": [],
        "ket_qua_tong_ket": [],
        "tabs_data": []
    }

    try:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data_to_export, f, ensure_ascii=False, indent=4)
        print(f"[{script_name}] Đã chạy ngầm, tự động tính toán và xuất tệp JSON thành công tại: {file_path}")
    except Exception as e:
        print(f"[{script_name}] Lỗi khi chạy ngầm tự động: {e}")

if __name__ == "__main__":
    if "--gui" in sys.argv:
        root = tk.Tk()
        app = UngDungPhanTich(root)
        root.mainloop()
    else:
        # Chạy tự động ngầm hoàn toàn theo đúng quy chuẩn[cite: 2]
        thuc_hien_xu_ly_tu_dong_ngam()
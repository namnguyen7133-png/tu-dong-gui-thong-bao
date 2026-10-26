import os
import sys
import json
import glob
import argparse
from datetime import datetime, timedelta
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

# Lấy tên tệp Python hiện tại một cách động
TEN_SCRIPT_HIEN_TAI = os.path.basename(__file__)
TEN_SCRIPT_GOC = os.path.splitext(TEN_SCRIPT_HIEN_TAI)[0]
CONFIG_FILE = f"config_{TEN_SCRIPT_GOC}.json"

class UngDungQuanLyTabNam:
    def __init__(self, root, che_do_gui=False, thu_muc_lam_viec=None):
        self.root = root
        self.che_do_gui = che_do_gui
        
        if thu_muc_lam_viec and os.path.exists(thu_muc_lam_viec):
            self.thu_muc_nguon = os.path.abspath(thu_muc_lam_viec)
        else:
            self.thu_muc_nguon = os.getcwd()

        self.ten_thu_muc_nguon = os.path.basename(self.thu_muc_nguon) or "ThuMucGoc"

        if not self.che_do_gui:
            self.root.withdraw()
        else:
            self.root.title(f"Hệ Thống Xử Lý Dữ Liệu Nam & Quay Vòng Link YouTube [{TEN_SCRIPT_HIEN_TAI}]")
            self.root.geometry("1100x880")
            self.root.configure(bg="#1E1E2E")

        self.danh_sach_people = []
        self.danh_sach_gio_nam = []
        self.chi_tiet_dong_thuongluu = {}
        self.danh_sach_tep_nguon = []
        self.ket_qua_tinh_toan = []

        self.config_data = self.tai_cau_hinh_cu()

        if self.che_do_gui:
            self.tao_giao_dien()
            self.tu_dong_nap_du_lieu_tu_config()
        else:
            self.chay_xu_ly_ngam_hoan_toan()

    def tai_cau_hinh_cu(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, dict):
                        return data
            except:
                pass
        return {
            "script_su_dung": TEN_SCRIPT_HIEN_TAI,
            "path_nhan_su": "",
            "path_thuongluu": "",
            "path_bang_phu_1": "",
            "path_bang_phu_2": "",
            "path_thu_muc_txt_youtube": r"D:\LAY_DUONG_DAN_YOUTUBE\ket_qua_youtube_ngaymacbenh",
            "path_luu_json": ""
        }

    def luu_cau_hinh_moi(self):
        self.config_data["script_su_dung"] = TEN_SCRIPT_HIEN_TAI
        self.config_data["path_nhan_su"] = self.entry_ns.get().strip()
        self.config_data["path_thuongluu"] = self.entry_tl.get().strip()
        self.config_data["path_bang_phu_1"] = self.entry_bp1.get().strip()
        self.config_data["path_bang_phu_2"] = self.entry_bp2.get().strip()
        if hasattr(self, 'entry_tm_yt'):
            self.config_data["path_thu_muc_txt_youtube"] = self.entry_tm_yt.get().strip()
        if hasattr(self, 'entry_path_json'):
            self.config_data["path_luu_json"] = self.entry_path_json.get().strip()

        try:
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(self.config_data, f, ensure_ascii=False, indent=4)
            if self.che_do_gui:
                messagebox.showinfo("Thành công", f"Đã lưu cấu hình vào tệp [{CONFIG_FILE}] thành công!")
            self.xu_ly_nap_file_vao_bo_nhieu()
        except Exception as e:
            if self.che_do_gui:
                messagebox.showerror("Lỗi", f"Không thể lưu cấu hình: {e}")

    def tao_giao_dien(self):
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure('TNotebook', background='#1E1E2E', borderwidth=0)
        self.style.configure('TNotebook.Tab', font=('Segoe UI', 10, 'bold'), padding=[12, 8])

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.tab1 = tk.Frame(self.notebook, bg="#2A2A3C")
        self.tab2 = tk.Frame(self.notebook, bg="#2A2A3C")
        self.tab3 = tk.Frame(self.notebook, bg="#2A2A3C")
        self.tab4 = tk.Frame(self.notebook, bg="#2A2A3C")
        self.tab_tim_kiem = tk.Frame(self.notebook, bg="#2A2A3C")

        self.notebook.add(self.tab1, text=" Tab 1: Chọn Tệp & Dữ Liệu ")
        self.notebook.add(self.tab2, text=" Tab 2: Tính Toán Giờ NAM ")
        self.notebook.add(self.tab3, text=" Tab 3: So Sánh & Link Quay Vòng ")
        self.notebook.add(self.tab4, text=" Tab 4: Xuất JSON Cố Định ")
        self.notebook.add(self.tab_tim_kiem, text=" 🔍 Tra Cứu & Lưu Tên Bệnh ")

        self.xay_dung_tab1()
        self.xay_dung_tab2()
        self.xay_dung_tab3()
        self.xay_dung_tab4()
        self.xay_dung_tab_tim_kiem()

    # ==================== TAB 1: BẢNG NẠP TỆP DỮ LIỆU ĐẦU VÀO ====================
    def xay_dung_tab1(self):
        lbl = tk.Label(self.tab1, text=f"QUẢN LÝ DỮ LIỆU ĐẦU VÀO CHO SCRIPT: {TEN_SCRIPT_HIEN_TAI}", font=("Segoe UI", 11, "bold"), fg="#00FFC8", bg="#2A2A3C")
        lbl.pack(pady=10)

        frame_input = tk.Frame(self.tab1, bg="#2A2A3C")
        frame_input.pack(fill=tk.X, padx=20, pady=5)

        tk.Label(frame_input, text="1. Tệp Danh Sách Nhân Sự:", fg="#FFF", bg="#2A2A3C", width=27, anchor="w").grid(row=0, column=0, sticky="w", pady=5)
        self.entry_ns = tk.Entry(frame_input, font=("Segoe UI", 10), width=45)
        self.entry_ns.grid(row=0, column=1, padx=5, pady=5)
        self.entry_ns.insert(0, self.config_data.get("path_nhan_su", ""))
        tk.Button(frame_input, text="📁 Chọn Tệp", bg="#FFA07A", command=lambda: self.chon_file(self.entry_ns)).grid(row=0, column=2, padx=5)

        tk.Label(frame_input, text="2. Tệp Giờ Bệnh THUONGLUU:", fg="#FFF", bg="#2A2A3C", width=27, anchor="w").grid(row=1, column=0, sticky="w", pady=5)
        self.entry_tl = tk.Entry(frame_input, font=("Segoe UI", 10), width=45)
        self.entry_tl.grid(row=1, column=1, padx=5, pady=5)
        self.entry_tl.insert(0, self.config_data.get("path_thuongluu", ""))
        tk.Button(frame_input, text="📁 Chọn Tệp", bg="#FFA07A", command=lambda: self.chon_file(self.entry_tl)).grid(row=1, column=2, padx=5)

        tk.Label(frame_input, text="3. Bảng Số Phụ 1:", fg="#FFF", bg="#2A2A3C", width=27, anchor="w").grid(row=2, column=0, sticky="w", pady=5)
        self.entry_bp1 = tk.Entry(frame_input, font=("Segoe UI", 10), width=45)
        self.entry_bp1.grid(row=2, column=1, padx=5, pady=5)
        self.entry_bp1.insert(0, self.config_data.get("path_bang_phu_1", ""))
        tk.Button(frame_input, text="📁 Chọn Tệp", bg="#FFA07A", command=lambda: self.chon_file(self.entry_bp1)).grid(row=2, column=2, padx=5)

        tk.Label(frame_input, text="4. Bảng Số Phụ 2:", fg="#FFF", bg="#2A2A3C", width=27, anchor="w").grid(row=3, column=0, sticky="w", pady=5)
        self.entry_bp2 = tk.Entry(frame_input, font=("Segoe UI", 10), width=45)
        self.entry_bp2.grid(row=3, column=1, padx=5, pady=5)
        self.entry_bp2.insert(0, self.config_data.get("path_bang_phu_2", ""))
        tk.Button(frame_input, text="📁 Chọn Tệp", bg="#FFA07A", command=lambda: self.chon_file(self.entry_bp2)).grid(row=3, column=2, padx=5)

        tk.Label(frame_input, text="5. Thư mục chứa TXT link YouTube:", fg="#FFF", bg="#2A2A3C", width=27, anchor="w").grid(row=4, column=0, sticky="w", pady=5)
        self.entry_tm_yt = tk.Entry(frame_input, font=("Segoe UI", 10), width=45)
        self.entry_tm_yt.grid(row=4, column=1, padx=5, pady=5)
        self.entry_tm_yt.insert(0, self.config_data.get("path_thu_muc_txt_youtube", r"D:\LAY_DUONG_DAN_YOUTUBE\ket_qua_youtube_ngaymacbenh"))
        tk.Button(frame_input, text="📁 Chọn Thư Mục", bg="#FFA07A", command=self.chon_thu_muc_txt_benh).grid(row=4, column=2, padx=5)

        btn_luu = tk.Button(self.tab1, text=f"💾 Lưu Cố Định Cấu Hình ({CONFIG_FILE})", font=("Segoe UI", 11, "bold"), bg="#00FFC8", fg="#000", command=self.luu_cau_hinh_moi)
        btn_luu.pack(pady=10)

        columns = ("STT", "Họ Tên", "Ngày Sinh", "Giờ Sinh", "Giới Tính")
        self.tree_tab1 = ttk.Treeview(self.tab1, columns=columns, show="headings", height=7)
        for col in columns:
            self.tree_tab1.heading(col, text=col)
            self.tree_tab1.column(col, width=150, anchor="center")
        self.tree_tab1.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

    def chon_file(self, entry_widget):
        path = filedialog.askopenfilename(filetypes=[("Text/Web/Sub files", "*.txt;*.html;*.vtt"), ("All files", "*.*")])
        if path:
            entry_widget.delete(0, tk.END)
            entry_widget.insert(0, path)

    def chon_thu_muc_txt_benh(self):
        thu_muc = filedialog.askdirectory(title="Chọn thư mục chứa các tệp TXT link YouTube")
        if thu_muc:
            self.entry_tm_yt.delete(0, tk.END)
            self.entry_tm_yt.insert(0, thu_muc)

    def tu_dong_nap_du_lieu_tu_config(self):
        if any(self.config_data.values()):
            self.xu_ly_nap_file_vao_bo_nhieu()

    def xu_ly_nap_file_vao_bo_nhieu(self):
        self.danh_sach_people.clear()
        self.danh_sach_gio_nam.clear()
        self.chi_tiet_dong_thuongluu.clear()
        self.danh_sach_tep_nguon.clear()

        if self.che_do_gui and hasattr(self, 'tree_tab1'):
            for item in self.tree_tab1.get_children():
                self.tree_tab1.delete(item)

        files_to_load = [
            self.config_data.get("path_nhan_su", ""),
            self.config_data.get("path_thuongluu", ""),
            self.config_data.get("path_bang_phu_1", ""),
            self.config_data.get("path_bang_phu_2", "")
        ]

        for f_path in files_to_load:
            if f_path and os.path.exists(f_path):
                self.danh_sach_tep_nguon.append(os.path.abspath(f_path))
                if f_path == files_to_load[0]:
                    self.nap_nhan_su(f_path)
                elif f_path == files_to_load[1]:
                    self.nap_thuongluu_chi_tiet(f_path)
                else:
                    self.nap_bang_so(f_path)

        self.danh_sach_gio_nam = sorted(list(set(self.danh_sach_gio_nam)))

    def nap_nhan_su(self, file_path):
        try:
            with open(file_path, "r", encoding="utf-8-sig", errors="ignore") as f:
                for line in f:
                    dong = line.strip()
                    if "|" in dong:
                        parts = [p.strip() for p in dong.split("|")]
                        if len(parts) >= 4:
                            p_info = {"name": parts[0], "dob": parts[1], "time": parts[2], "gender": parts[3]}
                            if p_info not in self.danh_sach_people:
                                self.danh_sach_people.append(p_info)
                                if self.che_do_gui and hasattr(self, 'tree_tab1'):
                                    self.tree_tab1.insert("", "end", values=(len(self.danh_sach_people), parts[0], parts[1], parts[2], parts[3]))
        except:
            pass

    def nap_thuongluu_chi_tiet(self, file_path):
        """Đọc tệp THUONGLUU: trích xuất số và làm sạch chuỗi dòng bệnh thông minh"""
        try:
            with open(file_path, "r", encoding="utf-8-sig", errors="ignore") as f:
                for line in f:
                    dong = line.strip()
                    if not dong: continue
                    
                    # Tách các phần tử phân cách bằng dấu tab, gạch dọc hoặc khoảng trắng
                    parts = [p.strip() for p in dong.replace("\t", " ").replace("|", " ").split()]
                    found_nums = []
                    
                    for p in parts:
                        if p.isdigit():
                            val = int(p)
                            if val > 0:
                                found_nums.append(val)
                                self.danh_sach_gio_nam.append(val)
                    
                    # Làm sạch chuỗi dòng bệnh: loại bỏ số thứ tự, loại bỏ các từ khóa thừa như NAM/NỮ
                    clean_text = dong
                    for p in parts:
                        if p.isdigit():
                            clean_text = clean_text.replace(p, "")
                    
                    clean_text = clean_text.replace("NAM", "").replace("NỮ", "").replace("NU", "")
                    clean_text = clean_text.replace(":", " ").replace("|", " ").replace("\t", " ")
                    # Lấy phân đoạn chữ cái có ý nghĩa đầu tiên (ví dụ: "Dương bất thường")
                    sub_parts = [sp.strip() for sp in clean_text.split("/") if len(sp.strip()) > 2]
                    final_benh_name = sub_parts[0] if sub_parts else clean_text.strip()
                    # Rút gọn khoảng trắng thừa
                    final_benh_name = " ".join(final_benh_name.split())

                    for num in found_nums:
                        self.chi_tiet_dong_thuongluu[num] = final_benh_name
        except:
            pass

    def nap_bang_so(self, file_path):
        try:
            with open(file_path, "r", encoding="utf-8-sig", errors="ignore") as f:
                for line in f:
                    for p in line.replace(",", " ").replace(";", " ").split():
                        if p.isdigit():
                            val = int(p)
                            if val > 0:
                                self.danh_sach_gio_nam.append(val)
        except:
            pass

    # ==================== TAB 2: TÍNH TOÁN ====================
    def xay_dung_tab2(self):
        lbl = tk.Label(self.tab2, text="HIỂN THỊ KẾT QUẢ TÍNH TOÁN GIỜ NAM", font=("Segoe UI", 12, "bold"), fg="#FFD700", bg="#2A2A3C")
        lbl.pack(pady=10)
        btn_t = tk.Button(self.tab2, text="⚙️ Thực Hiện Tính Toán Ngay", font=("Segoe UI", 10, "bold"), bg="#FFD700", fg="#000", command=self.thuc_hien_tinh_toan)
        btn_t.pack(pady=5)
        self.txt_t2 = tk.Text(self.tab2, wrap=tk.WORD, font=("Consolas", 10), bg="#1E1E2E", fg="#FFF")
        self.txt_t2.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    def thuc_hien_tinh_toan(self):
        self.xu_ly_nap_file_vao_bo_nhieu()
        danh_sach_nam = [p for p in self.danh_sach_people if "NAM" in p["gender"].strip().upper()]
        if not danh_sach_nam: danh_sach_nam = self.danh_sach_people

        self.ket_qua_tinh_toan.clear()
        log = f"Tổng nhân sự: {len(danh_sach_nam)} | Tổng mốc tham chiếu: {len(self.danh_sach_gio_nam)}\n\n"
        hien_tai = datetime.now()

        for p in danh_sach_nam:
            try:
                dob_dt = datetime.strptime(p["dob"], "%d/%m/%Y")
                gio_s = int(p["time"]) if p["time"].isdigit() else 0
                kq1 = (hien_tai - dob_dt).days
                kq2 = kq1 * 24
                kq3 = kq2 + (24 - gio_s if gio_s <= 24 else -gio_s)
                kq4 = kq3 * 60
                log += f"--- Nhân sự: {p['name']} ({p['gender']}) ---\n"
                for g in self.danh_sach_gio_nam:
                    div = g * 60
                    if div == 0: continue
                    kq5 = kq4 // div
                    kq6 = kq5 % 1000 if kq5 > 1000 else kq5
                    kq7 = kq6 % 60
                    kq8 = kq7 % 1000 if kq7 > 1000 else kq7
                    ten_benh_dong = self.chi_tiet_dong_thuongluu.get(g, f"ChungBệnh_{g}")
                    self.ket_qua_tinh_toan.append({
                        "name": p["name"], 
                        "gio_stt": g, 
                        "ten_benh": ten_benh_dong,
                        "kq5": kq5, "kq6": kq6, "kq7": kq7, "kq8": kq8
                    })
                    log += f"   [Số/Giờ {g}] Thương: {kq5} | Tên bệnh lọc sạch: {ten_benh_dong}\n"
                log += "\n"
            except: pass

        if self.che_do_gui:
            self.txt_t2.delete("1.0", tk.END)
            self.txt_t2.insert(tk.END, log + "\n✅ Đã hoàn thành tính toán hiển thị chi tiết tại Tab 2!")

    # ==================== TAB 3: SO SÁNH & QUAY VÒNG LINK YOUTUBE ====================
    def xay_dung_tab3(self):
        lbl = tk.Label(self.tab3, text="SO SÁNH TRÙNG & PHÁT QUAY VÒNG LINK YOUTUBE TỪ TỆP TXT BỆNH", font=("Segoe UI", 12, "bold"), fg="#FF6B6B", bg="#2A2A3C")
        lbl.pack(pady=10)
        btn_ss = tk.Button(self.tab3, text="🔍 So Sánh Trùng & Quay Vòng Link (Hết lại lặp từ đầu)", font=("Segoe UI", 10, "bold"), bg="#FF6B6B", fg="#FFF", command=self.thuc_hien_so_sanh_va_quay_vong_link)
        btn_ss.pack(pady=5)
        self.txt_t3 = tk.Text(self.tab3, wrap=tk.WORD, font=("Consolas", 10), bg="#1E1E2E", fg="#FFF")
        self.txt_t3.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    def thuc_hien_so_sanh_va_quay_vong_link(self):
        self.thuc_hien_tinh_toan()
        if not self.ket_qua_tinh_toan:
            if self.che_do_gui:
                messagebox.showwarning("Cảnh báo", "Chưa có kết quả tính toán ở Tab 2!")
            return

        thu_muc_txt = self.config_data.get("path_thu_muc_txt_youtube", r"D:\LAY_DUONG_DAN_YOUTUBE\ket_qua_youtube_ngaymacbenh")
        tap_tham_chieu = set(self.danh_sach_gio_nam)
        log_ss = f"--- KẾT QUẢ SO SÁNH TRÙNG & QUAY VÒNG LINK YOUTUBE ---\n"
        log_ss += f"Thư mục tra cứu tệp txt bệnh: {thu_muc_txt}\n\n"
        dem_trung = 0

        for item in self.ket_qua_tinh_toan:
            cac_gia_tri = [item["kq5"], item["kq6"], item["kq7"], item["kq8"]]
            for val in cac_gia_tri:
                if val in tap_tham_chieu:
                    dem_trung += 1
                    ten_benh_dong = item["ten_benh"]
                    danh_sach_link_youtube = self.tim_va_doc_tep_txt_benh(ten_benh_dong, thu_muc_txt)
                    
                    log_ss += f"🎯 Trùng khớp số: {val} | Nhân sự: {item['name']} | Tên bệnh: {ten_benh_dong}\n"
                    if danh_sach_link_youtube:
                        tong_link = len(danh_sach_link_youtube)
                        log_ss += f"   📂 Tìm thấy tệp TXT bệnh phù hợp. Danh sách phát quay vòng ({tong_link} link, hết sẽ lặp lại từ đầu):\n"
                        for vong in range(1, 3):  # Hiển thị minh họa 2 vòng quay vòng liên tiếp
                            idx_thuc_te = (vong - 1) % tong_link
                            log_ss += f"      [Vòng phát #{vong} | Link số {idx_thuc_te+1}/{tong_link}] 🔗 {danh_sach_link_youtube[idx_thuc_te]}\n"
                    else:
                        log_ss += f"   ⚠️ Không tìm thấy tệp TXT khớp với tên bệnh '{ten_benh_dong}' trong thư mục.\n"
                    log_ss += "\n"

        if dem_trung == 0:
            log_ss += "Không tìm thấy kết quả thương nào trùng khớp với bảng tham chiếu.\n"
        else:
            log_ss += f"✅ Phát hiện tổng cộng {dem_trung} điểm trùng khớp hoàn toàn!\n"

        if self.che_do_gui:
            self.txt_t3.delete("1.0", tk.END)
            self.txt_t3.insert(tk.END, log_ss)

    def tim_va_doc_tep_txt_benh(self, ten_benh, thu_muc_txt):
        """Dò tệp txt tối ưu: đối chiếu từ khóa sạch qua lại với tên các file txt trong thư mục"""
        links = []
        if not thu_muc_txt or not os.path.exists(thu_muc_txt):
            return links
        
        # Chuẩn hóa tên bệnh cần tìm về chữ thường không dấu / lọc ký tự sạch
        ten_benh_clean = "".join([c for c in ten_benh.lower() if c.isalnum() or c.isspace()]).strip()
        keywords = [w for w in ten_benh_clean.split() if len(w) > 1]
        
        try:
            for file_name in os.listdir(thu_muc_txt):
                if file_name.endswith(".txt"):
                    file_base = os.path.splitext(file_name)[0]
                    # Làm sạch tên file (bỏ số thứ tự đầu file, bỏ ký tự đặc biệt)
                    file_words = [w for w in file_base.replace("_", " ").split() if not w.isdigit()]
                    file_keyword = " ".join(file_words).lower().strip()
                    file_clean = "".join([c for c in file_keyword if c.isalnum() or c.isspace()]).strip()
                    
                    matched = False
                    if file_clean and (file_clean in ten_benh_clean or ten_benh_clean in file_clean):
                        matched = True
                    elif keywords:
                        # Kiểm tra xem có chứa phần lớn các từ khóa của tên bệnh không
                        match_count = sum(1 for kw in keywords if kw in file_clean)
                        if match_count >= max(1, len(keywords) // 2):
                            matched = True
                            
                    if matched:
                        full_path = os.path.join(thu_muc_txt, file_name)
                        with open(full_path, "r", encoding="utf-8-sig", errors="ignore") as f:
                            for line in f:
                                line_str = line.strip()
                                if "http://" in line_str or "https://" in line_str:
                                    for word in line_str.split():
                                        if word.startswith("http://") or word.startswith("https://"):
                                            links.append(word)
                        if links:
                            break
        except:
            pass
        return links

    # ==================== TAB 4: XUẤT JSON CHUẨN SCRIPT B ====================
    def xay_dung_tab4(self):
        lbl = tk.Label(self.tab4, text="XUẤT TỆP JSON CHUẨN (TỰ ĐỘNG LẤY TÊN SCRIPT LÀM TIỀN TỐ)", font=("Segoe UI", 12, "bold"), fg="#00FFC8", bg="#2A2A3C")
        lbl.pack(pady=10)

        frame_lưu = tk.Frame(self.tab4, bg="#2A2A3C")
        frame_lưu.pack(fill=tk.X, padx=20, pady=5)

        tk.Label(frame_lưu, text="Thư mục/Đường dẫn lưu JSON:", fg="#FFF", bg="#2A2A3C", width=25, anchor="w").grid(row=0, column=0, sticky="w", pady=5)
        self.entry_path_json = tk.Entry(frame_lưu, font=("Segoe UI", 10), width=50)
        self.entry_path_json.grid(row=0, column=1, padx=5, pady=5)
        self.entry_path_json.insert(0, self.config_data.get("path_luu_json", ""))
        tk.Button(frame_lưu, text="📁 Chọn Thư Mục", bg="#FFA07A", command=self.chon_thu_muc_luu).grid(row=0, column=2, padx=5)

        btn_x = tk.Button(self.tab4, text="💾 Xuất Tệp JSON Theo Tên Script Động", font=("Segoe UI", 12, "bold"), bg="#00FFC8", fg="#000", command=self.thuc_hien_xuat_json)
        btn_x.pack(pady=15)

        self.txt_t4 = tk.Text(self.tab4, wrap=tk.WORD, font=("Consolas", 10), bg="#1E1E2E", fg="#FFF", height=10)
        self.txt_t4.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    def chon_thu_muc_luu(self):
        thu_muc = filedialog.askdirectory(title="Chọn thư mục mặc định để lưu tệp JSON")
        if thu_muc:
            self.entry_path_json.delete(0, tk.END)
            self.entry_path_json.insert(0, thu_muc)
            self.config_data["path_luu_json"] = thu_muc
            self.luu_cau_hinh_moi()

    def thuc_hien_xuat_json(self, duong_dan_chi_dinh=None):
        self.xu_ly_nap_file_vao_bo_nhieu()
        if not self.danh_sach_people:
            if self.che_do_gui:
                messagebox.showwarning("Cảnh báo", "Chưa có dữ liệu nhân sự để xuất!")
            return None

        now = datetime.now()
        timestamp_str = now.strftime("%Y-%m-%d %H:%M:%S")
        time_tag = now.strftime("%Y%m%d_%H%M%S")

        date_minus_7 = (now - timedelta(days=7)).strftime("%Y-%m-%d")
        date_plus_7 = (now + timedelta(days=7)).strftime("%Y-%m-%d")

        path_ns = self.config_data.get("path_nhan_su", "")
        ten_thu_muc_goc = os.path.basename(os.path.dirname(path_ns)) or self.ten_thu_muc_nguon
        
        default_json_name = f"{TEN_SCRIPT_GOC}_{ten_thu_muc_goc}_{time_tag}.json"

        thu_muc_mac_dinh = self.entry_path_json.get().strip() if hasattr(self, 'entry_path_json') else self.config_data.get("path_luu_json", "")
        if not thu_muc_mac_dinh or not os.path.exists(thu_muc_mac_dinh):
            thu_muc_mac_dinh = os.path.dirname(path_ns) if path_ns and os.path.exists(os.path.dirname(path_ns)) else self.thu_muc_nguon

        if self.che_do_gui and not duong_dan_chi_dinh:
            path_save = filedialog.asksaveasfilename(
                initialdir=thu_muc_mac_dinh,
                initialfile=default_json_name,
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
                title="Lưu tệp JSON đầu ra"
            )
            if not path_save:
                return None
        else:
            path_save = duong_dan_chi_dinh or os.path.join(thu_muc_mac_dinh, default_json_name)

        data_json = {
            "metadata": {
                "script_su_dung": TEN_SCRIPT_HIEN_TAI,
                "timestamp": timestamp_str,
                "date_minus_7_days": date_minus_7,
                "date_plus_7_days": date_plus_7,
                "thu_muc_nguon_dinh_danh": ten_thu_muc_goc,
                "danh_sach_tep_nguon_da_quet": self.danh_sach_tep_nguon
            },
            "ref_date": now.strftime("%d/%m/%Y"),
            "ref_time": now.strftime("%H:%M"),
            "ref_numbers": self.danh_sach_gio_nam,
            "people": self.danh_sach_people,
            "custom_tabs": {
                "tab_youtube": {
                    "path_thu_muc_txt_youtube": self.config_data.get("path_thu_muc_txt_youtube", "")
                }
            }
        }

        try:
            with open(path_save, "w", encoding="utf-8") as f:
                json.dump(data_json, f, ensure_ascii=False, indent=4)
            
            self.cap_nhat_index_quan_ly(path_save, data_json["metadata"])

            if self.che_do_gui:
                self.txt_t4.delete("1.0", tk.END)
                self.txt_t4.insert(tk.END, f"✅ Đã xuất tệp JSON thành công:\n{path_save}\n\n(Tên file bắt đầu bằng tiền tố [{TEN_SCRIPT_GOC}] đúng chuẩn yêu cầu).")
                messagebox.showinfo("Thành công", f"Đã xuất tệp JSON thành công!")
            return path_save
        except Exception as e:
            if self.che_do_gui:
                messagebox.showerror("Lỗi", f"Không thể lưu file: {e}")
            return None

    def cap_nhat_index_quan_ly(self, path_json, metadata):
        thu_muc = os.path.dirname(path_json)
        path_index = os.path.join(thu_muc, f"index_{TEN_SCRIPT_GOC}_quan_ly.json")
        index_data = []
        if os.path.exists(path_index):
            try:
                with open(path_index, "r", encoding="utf-8") as f: index_data = json.load(f)
            except: pass
        
        item_moi = {
            "script_su_dung": metadata["script_su_dung"],
            "ten_file_json": os.path.basename(path_json),
            "duong_dan_tuyet_doi": path_json,
            "thoi_gian_xuat": metadata["timestamp"],
            "thu_muc_nguon": metadata["thu_muc_nguon_dinh_danh"],
            "danh_sach_tep_nguon": metadata["danh_sach_tep_nguon_da_quet"]
        }
        index_data.insert(0, item_moi)
        with open(path_index, "w", encoding="utf-8") as f:
            json.dump(index_data, f, ensure_ascii=False, indent=4)

    # ==================== TAB TRA CỨU & LƯU TÊN BỆNH ====================
    def xay_dung_tab_tim_kiem(self):
        lbl = tk.Label(self.tab_tim_kiem, text="TRA CỨU DỮ LIỆU & LƯU LỊCH SỬ VÀO TỆP TXT THEO TÊN BỆNH", font=("Segoe UI", 12, "bold"), fg="#00FFC8", bg="#2A2A3C")
        lbl.pack(pady=10)

        frame_form = tk.Frame(self.tab_tim_kiem, bg="#2A2A3C")
        frame_form.pack(fill=tk.X, padx=20, pady=5)

        tk.Label(frame_form, text="Tìm kiếm tên (Nhân sự/Bảng):", fg="#FFF", bg="#2A2A3C", width=22, anchor="w").grid(row=0, column=0, sticky="w", pady=4)
        self.entry_tk_ten = tk.Entry(frame_form, font=("Segoe UI", 10), width=30)
        self.entry_tk_ten.grid(row=0, column=1, padx=5, pady=4, sticky="w")

        tk.Label(frame_form, text="Thời điểm (YYYY-MM-DD HH:MM):", fg="#FFF", bg="#2A2A3C", width=22, anchor="w").grid(row=1, column=0, sticky="w", pady=4)
        self.entry_tk_thoigian = tk.Entry(frame_form, font=("Segoe UI", 10), width=30)
        self.entry_tk_thoigian.grid(row=1, column=1, padx=5, pady=4, sticky="w")
        self.entry_tk_thoigian.insert(0, datetime.now().strftime("%Y-%m-%d %H:%M"))

        tk.Label(frame_form, text="Nhập tên bệnh bị mắc:", fg="#FFF", bg="#2A2A3C", width=22, anchor="w").grid(row=2, column=0, sticky="w", pady=4)
        self.entry_tk_ten_benh = tk.Entry(frame_form, font=("Segoe UI", 10), width=30)
        self.entry_tk_ten_benh.grid(row=2, column=1, padx=5, pady=4, sticky="w")
        self.entry_tk_ten_benh.insert(0, "Dương bất thường")

        frame_buttons = tk.Frame(self.tab_tim_kiem, bg="#2A2A3C")
        frame_buttons.pack(fill=tk.X, padx=20, pady=10)

        tk.Button(frame_buttons, text="🔍 Dò Tìm & Lọc Dữ Liệu", font=("Segoe UI", 10, "bold"), bg="#FFD700", fg="#000", command=self.thuc_hien_tim_kiem_du_lieu).pack(side=tk.LEFT, padx=5)
        tk.Button(frame_buttons, text="💾 Lưu Lịch Sử Vào Tệp TXT Theo Tên Bệnh", font=("Segoe UI", 10, "bold"), bg="#00FFC8", fg="#000", command=self.luu_lich_su_vao_txt_theo_benh).pack(side=tk.LEFT, padx=5)

        self.txt_ket_qua_tk = tk.Text(self.tab_tim_kiem, wrap=tk.WORD, font=("Consolas", 10), bg="#1E1E2E", fg="#FFF", height=18)
        self.txt_ket_qua_tk.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    def thuc_hien_tim_kiem_du_lieu(self):
        tu_khoa_ten = self.entry_tk_ten.get().strip().lower()
        tu_khoa_tg = self.entry_tk_thoigian.get().strip().lower()
        tu_khoa_benh = self.entry_tk_ten_benh.get().strip().lower()

        self.thuc_hien_tinh_toan()

        ket_qua_loc = []
        for item in self.ket_qua_tinh_toan:
            match_ten = (tu_khoa_ten in item["name"].lower()) if tu_khoa_ten else True
            if match_ten:
                ket_qua_loc.append(item)

        log_tk = f"=== KẾT QUẢ TRA CỨU DỮ LIỆU ===\n"
        log_tk += f"- Từ khóa tên: '{tu_khoa_ten if tu_khoa_ten else 'Tất cả'}'\n"
        log_tk += f"- Thời điểm truy vấn: '{tu_khoa_tg}'\n"
        log_tk += f"- Tên bệnh cần gióng: '{tu_khoa_benh}'\n\n"

        if not ket_qua_loc:
            log_tk += "Không tìm thấy dữ liệu phù hợp với tiêu chí tìm kiếm.\n"
        else:
            for idx, res in enumerate(ket_qua_loc, 1):
                log_tk += f"{idx}. Nhân sự: {res['name']} | Giờ bệnh: {res['gio_stt']}h | Tên bệnh: {res['ten_benh']} | Thương: {res['kq5']}\n"

        self.txt_ket_qua_tk.delete("1.0", tk.END)
        self.txt_ket_qua_tk.insert(tk.END, log_tk)
        return ket_qua_loc

    def luu_lich_su_vao_txt_theo_benh(self):
        ten_benh = self.entry_tk_ten_benh.get().strip()
        if not ten_benh:
            messagebox.showwarning("Cảnh báo", "Vui lòng nhập tên bệnh để đặt tên tệp TXT!")
            return

        thu_muc_txt = self.config_data.get("path_thu_muc_txt_youtube", r"D:\LAY_DUONG_DAN_YOUTUBE\ket_qua_youtube_ngaymacbenh")
        if not os.path.exists(thu_muc_txt):
            try:
                os.makedirs(thu_muc_txt, exist_ok=True)
            except:
                pass

        ten_file_an_toan = "".join([c if c.isalnum() or c in (' ', '_', '-') else '_' for c in ten_benh]).strip().replace(" ", "_")
        duong_dan_txt = os.path.join(thu_muc_txt, f"{ten_file_an_toan}.txt")

        ket_qua_loc = self.thuc_hien_tim_kiem_du_lieu()

        noi_dung_ghi = f"========================================\n"
        noi_dung_ghi += f" LỊCH SỬ DÒ TÌM & GÓNG DỮ LIỆU BỆNH\n"
        noi_dung_ghi += f" Tên bệnh: {ten_benh}\n"
        noi_dung_ghi += f" Thời gian ghi nhận: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        noi_dung_ghi += f"========================================\n\n"

        for res in ket_qua_loc:
            noi_dung_ghi += f"Nhân sự: {res['name']} | Số/Giờ: {res['gio_stt']}h | Tên bệnh: {res['ten_benh']} | Thương: {res['kq5']} | Dư 1000: {res['kq6']}\n"

        try:
            with open(duong_dan_txt, "a", encoding="utf-8") as f:
                f.write(noi_dung_ghi + "\n\n")

            messagebox.showinfo("Thành công", f"Đã lưu kết quả thành công vào tệp:\n{duong_dan_txt}")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể ghi tệp TXT: {e}")

    def chay_xu_ly_ngam_hoan_toan(self):
        self.xu_ly_nap_file_vao_bo_nhieu()
        if self.danh_sach_people:
            self.thuc_hien_tinh_toan()
            self.thuc_hien_xuat_json()
        self.root.destroy()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Chương trình xử lý dữ liệu Nam tự động")
    parser.add_argument("--gui", action="store_true", help="Bật giao diện Tkinter (Mặc định chạy ngầm không che desktop)")
    parser.add_argument("--dir", type=str, default=None, help="Đường dẫn thư mục làm việc")
    args = parser.parse_args()

    root = tk.Tk()
    app = UngDungQuanLyTabNam(root, che_do_gui=args.gui, thu_muc_lam_viec=args.dir)
    if args.gui:
        root.mainloop()
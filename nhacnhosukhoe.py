import os
import sys
import json
from datetime import datetime, timedelta
import tkinter as tk
from tkinter import messagebox, filedialog, ttk

# === TỰ ĐỘNG CÀI ĐẶT THƯ VIỆN NẾU THIẾU ===
def ensure_dependencies():
    for pkg in ["psutil", "pywin32"]:
        try:
            __import__(pkg)
        except ImportError:
            import subprocess
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", pkg, "--quiet"])
            except:
                pass

ensure_dependencies()

# 1. ĐỊNH DANH ĐỘNG THEO TÊN TỆP PYTHON
PYTHON_SCRIPT_RAW = os.path.basename(__file__)
PYTHON_SCRIPT_NAME = os.path.splitext(PYTHON_SCRIPT_RAW)[0]

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if not os.path.exists(BASE_DIR):
    BASE_DIR = os.getcwd()

CONFIG_FILE = os.path.join(BASE_DIR, f"{PYTHON_SCRIPT_NAME}_config.json")
INDEX_JSON_FILE = os.path.join(BASE_DIR, f"{PYTHON_SCRIPT_NAME}_index_mapping.json")
HISTORY_TXT_FILE = os.path.join(BASE_DIR, f"{PYTHON_SCRIPT_NAME}_lich_su_nhap.txt")
RETENTION_DAYS = 7

def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            pass
    return {"source_files": [], "last_export_dir": BASE_DIR}

def save_config(cfg):
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(cfg, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"Lỗi lưu config: {e}")

def parse_date_safe(s):
    for fmt in ("%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y"):
        try:
            return datetime.strptime(s.strip(), fmt)
        except:
            continue
    return None

# ================= GIAO DIỆN TKINTER ĐẦY ĐỦ TÍNH NĂNG & HIỂN THỊ KẾT QUẢ =================
class AdvancedAppGUI:
    def __init__(self, root):
        self.root = root
        self.root.title(f"Hệ Thống Tính Toán & Quản Lý Dữ Liệu - {PYTHON_SCRIPT_RAW}")
        self.root.geometry("950x700")
        
        self.config_data = load_config()
        self.source_files = self.config_data.get("source_files", [])

        # --- TIÊU ĐỀ ---
        lbl_title = tk.Label(root, text=f"BẢNG ĐIỀU KHIỂN & TÍNH TOÁN: {PYTHON_SCRIPT_RAW}", font=("Arial", 12, "bold"), fg="darkblue")
        lbl_title.pack(pady=5)

        # --- KHUNG 1: QUẢN LÝ NGUỒN DỮ LIỆU TXT ---
        frame_source = tk.LabelFrame(root, text=" 1. Nguồn Dữ Liệu TXT / Lịch Sử ", font=("Arial", 10, "bold"))
        frame_source.pack(fill="x", padx=15, pady=3)

        btn_add_files = tk.Button(frame_source, text="📂 Chọn Tệp Nguồn TXT", bg="#007ACC", fg="white", font=("Arial", 9, "bold"), command=self.add_source_files)
        btn_add_files.pack(side="left", padx=10, pady=5)

        self.lbl_files_count = tk.Label(frame_source, text=f"Đã chọn: {len(self.source_files)} tệp nguồn", font=("Arial", 9))
        self.lbl_files_count.pack(side="left", padx=10)

        btn_clear_files = tk.Button(frame_source, text="🗑️ Xóa Nguồn", font=("Arial", 9), command=self.clear_source_files)
        btn_clear_files.pack(side="right", padx=10, pady=5)

        # --- KHUNG 2: Ô NHẬP LIỆU & TÌM KIẾM ---
        frame_input = tk.LabelFrame(root, text=" 2. Tìm Kiếm & Nhập Lịch Sử (Tên, Thời gian, Bệnh lý) ", font=("Arial", 10, "bold"))
        frame_input.pack(fill="x", padx=15, pady=3)

        tk.Label(frame_input, text="Tìm Tên:", font=("Arial", 9)).grid(row=0, column=0, sticky="w", padx=8, pady=4)
        self.entry_name = tk.Entry(frame_input, width=22, font=("Arial", 9))
        self.entry_name.grid(row=0, column=1, sticky="w", padx=8, pady=4)

        tk.Label(frame_input, text="Thời Điểm (YYYY-MM-DD):", font=("Arial", 9)).grid(row=0, column=2, sticky="w", padx=8, pady=4)
        self.entry_time = tk.Entry(frame_input, width=18, font=("Arial", 9))
        self.entry_time.grid(row=0, column=3, sticky="w", padx=8, pady=4)
        self.entry_time.insert(0, datetime.now().strftime("%Y-%m-%d"))

        tk.Label(frame_input, text="Bệnh Bị Mắc:", font=("Arial", 9)).grid(row=1, column=0, sticky="w", padx=8, pady=4)
        self.entry_disease = tk.Entry(frame_input, width=30, font=("Arial", 9))
        self.entry_disease.grid(row=1, column=1, columnspan=2, sticky="w", padx=8, pady=4)

        btn_save_history = tk.Button(frame_input, text="💾 Lưu Vào Bảng Mẫu TXT", bg="orange", font=("Arial", 9, "bold"), command=self.save_to_txt_history)
        btn_save_history.grid(row=1, column=3, padx=8, pady=4, sticky="ew")

        # --- KHUNG 3: BẢNG HIỂN THỊ KẾT QUẢ TÍNH TOÁN TRỰC TIẾP (TREEVIEW) ---
        frame_table = tk.LabelFrame(root, text=" 3. Bảng Kết Quả Tính Toán & Dò Tìm Dữ Liệu ", font=("Arial", 10, "bold"))
        frame_table.pack(fill="both", expand=True, padx=15, pady=3)

        # Tạo bảng Treeview hiển thị dữ liệu tính toán
        columns = ("col_name", "col_metric", "col_val", "col_div", "col_code", "col_disease")
        self.tree = ttk.Treeview(frame_table, columns=columns, show="headings", height=8)
        
        self.tree.heading("col_name", text="Họ Tên")
        self.tree.heading("col_metric", text="Hệ Số / Chỉ Số")
        self.tree.heading("col_val", text="Giá Trị (Ngày/Tháng...)")
        self.tree.heading("col_div", text="Định Mức (Div)")
        self.tree.heading("col_code", text="Mã Dò (Code)")
        self.tree.heading("col_disease", text="Bệnh / Trạng Thái")

        self.tree.column("col_name", width=120)
        self.tree.column("col_metric", width=120)
        self.tree.column("col_val", width=100)
        self.tree.column("col_div", width=80)
        self.tree.column("col_code", width=80)
        self.tree.column("col_disease", width=180)

        scrollbar = ttk.Scrollbar(frame_table, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        scrollbar.pack(side="right", fill="y", pady=5)

        # --- KHUNG 4: NÚT TÍNH TOÁN & XUẤT JSON ---
        frame_action = tk.Frame(root)
        frame_action.pack(pady=8)

        btn_calc = tk.Button(frame_action, text="⚡ Chạy Tính Toán & Hiển Thị", bg="#28A745", fg="white", font=("Arial", 10, "bold"), command=self.run_calculation_ui)
        btn_calc.grid(row=0, column=0, padx=8)

        btn_export = tk.Button(frame_action, text="📥 Xuất JSON (Hộp Thoại Động)", bg="#17A2B8", fg="white", font=("Arial", 10, "bold"), command=self.export_json_dialog)
        btn_export.grid(row=0, column=1, padx=8)

        btn_exit = tk.Button(frame_action, text="❌ Thoát", font=("Arial", 9), command=root.quit)
        btn_exit.grid(row=0, column=2, padx=8)

        # Tự động chạy tính toán lần đầu khi mở app nếu có dữ liệu sẵn
        self.run_calculation_ui()

    def add_source_files(self):
        files = filedialog.askopenfilenames(title="Chọn các tệp nguồn TXT", filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])
        if files:
            for f in files:
                if f not in self.source_files:
                    self.source_files.append(f)
            self.config_data["source_files"] = self.source_files
            save_config(self.config_data)
            self.lbl_files_count.config(text=f"Đã chọn: {len(self.source_files)} tệp nguồn")
            self.run_calculation_ui()

    def clear_source_files(self):
        self.source_files = []
        self.config_data["source_files"] = []
        save_config(self.config_data)
        self.lbl_files_count.config(text="Đã chọn: 0 tệp nguồn")
        self.run_calculation_ui()

    def save_to_txt_history(self):
        name = self.entry_name.get().strip()
        time_val = self.entry_time.get().strip()
        disease = self.entry_disease.get().strip()

        if not name or not disease:
            messagebox.showwarning("Cảnh báo", "Vui lòng nhập đầy đủ Tên và Bệnh bị mắc!")
            return

        record_line = f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\tTên: {name}\tThời điểm: {time_val}\tBệnh: {disease}\n"
        try:
            with open(HISTORY_TXT_FILE, "a", encoding="utf-8") as f:
                f.write(record_line)
            messagebox.showinfo("Thành công", f"Đã lưu lịch sử vào tệp mẫu:\n{HISTORY_TXT_FILE}")
            self.run_calculation_ui() # Cập nhật lại bảng
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể lưu file: {e}")

    def run_calculation_ui(self):
        """Thực hiện tính toán và đổ trực tiếp kết quả lên bảng Treeview trên giao diện"""
        for row in self.tree.get_children():
            self.tree.delete(row)

        people = []
        ref_numbers = [123, 456, 789] # Giá trị mẫu mặc định nếu chưa có bảng tham chiếu

        # 1. Đọc dữ liệu từ các file nguồn TXT đã chọn hoặc file lịch sử
        files_to_read = self.source_files.copy()
        if os.path.exists(HISTORY_TXT_FILE):
            files_to_read.append(HISTORY_TXT_FILE)

        # Thêm file mẫu DULIEUSK.txt nếu có trong thư mục
        default_dulieu = os.path.join(BASE_DIR, "DULIEUSK.txt")
        if os.path.exists(default_dulieu) and default_dulieu not in files_to_read:
            files_to_read.append(default_dulieu)

        for filepath in files_to_read:
            if os.path.exists(filepath):
                try:
                    with open(filepath, "r", encoding="utf-8-sig") as f:
                        for line in f:
                            line = line.strip()
                            if not line:
                                continue
                            parts = line.split("\t")
                            if len(parts) >= 2:
                                name = parts[0].replace("Tên:", "").strip()
                                dob_str = parts[1].replace("Thời điểm:", "").replace("Đường dẫn:", "").strip()
                                disease = parts[3] if len(parts) > 3 else (parts[2] if len(parts) > 2 else "Khám sức khỏe định kỳ")
                                people.append({"name": name, "dob": dob_str, "disease": disease})
                except:
                    pass

        # Nếu chưa có dữ liệu nào, tạo dòng mẫu trực quan
        if not people:
            people = [{"name": "Nguyễn Văn A", "dob": "1990-01-01", "disease": "Huyết áp ổn định"}]

        # 2. Xử lý tính toán thời gian và thêm vào bảng hiển thị
        ref_dt = datetime.now()
        for p in people:
            dob = parse_date_safe(p["dob"])
            if not dob:
                delta_days = 3650 # Giá trị giả định mặc định
            else:
                delta = ref_dt - dob
                delta_days = abs(delta.days)

            # Tính toán các mốc thời gian theo yêu cầu
            metrics = {
                "Năm (Nguyên)": delta_days // 365,
                "Tháng (Nguyên)": delta_days // 30,
                "Ngày (Tổng)": delta_days
            }

            for m_name, val in metrics.items():
                div = 23
                ng, du = val // div, val % div
                code_str = f"{du:03d}"
                
                # Thêm dòng vào bảng Treeview
                self.tree.insert("", "end", values=(
                    p["name"],
                    m_name,
                    val,
                    div,
                    code_str,
                    p.get("disease", "Theo dõi sức khỏe")
                ))

    def export_json_dialog(self):
        """Mở hộp thoại asksaveasfilename để lưu tệp JSON động chuẩn cấu trúc"""
        folder_name_clean = os.path.basename(BASE_DIR) or "Root"
        file_time_suffix = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_filename = f"{PYTHON_SCRIPT_NAME}_{folder_name_clean}_{file_time_suffix}.json"

        last_dir = self.config_data.get("last_export_dir", BASE_DIR)
        
        save_path = filedialog.asksaveasfilename(
            initialdir=last_dir,
            initialfile=default_filename,
            defaultextension=".json",
            filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")]
        )

        if not save_path:
            return

        self.config_data["last_export_dir"] = os.path.dirname(save_path)
        save_config(self.config_data)

        now_dt = datetime.now()
        export_data = {
            "metadata": {
                "script_su_dung": PYTHON_SCRIPT_RAW,
                "source_folder_name": folder_name_clean,
                "source_folder_path": BASE_DIR,
                "source_files_read": self.source_files,
                "timestamp": now_dt.strftime("%Y-%m-%d %H:%M:%S")
            },
            "people": [{"name": self.entry_name.get().strip(), "disease": self.entry_disease.get().strip()}],
            "custom_tabs": {"DULIEU": {"links": self.source_files}}
        }

        try:
            with open(save_path, "w", encoding="utf-8") as f:
                json.dump(export_data, f, ensure_ascii=False, indent=4)
            messagebox.showinfo("Thành công", f"Đã xuất tệp JSON hoàn tất tại:\n{save_path}")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể ghi tệp JSON: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = AdvancedAppGUI(root)
    root.mainloop()
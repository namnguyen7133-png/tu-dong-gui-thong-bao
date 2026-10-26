from datetime import datetime, timedelta
import json
import os
import sys
import tkinter as ttk_lib  # Tránh xung đột tên
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

# Lấy tên tệp script hiện tại (bỏ phần mở rộng .py) để làm định danh cấu hình riêng biệt
SCRIPT_NAME = os.path.splitext(os.path.basename(__file__))[0]
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Cấu hình và Index tự động gắn liền với tên tệp Python (tránh đè lẫn khi đổi thư mục)
CONFIG_FILE = os.path.join(BASE_DIR, f"config_{SCRIPT_NAME}.json")
INDEX_FILE = os.path.join(BASE_DIR, f"index_{SCRIPT_NAME}.json")
TXT_DATA_TABLE = os.path.join(BASE_DIR, f"bang_mau_{SCRIPT_NAME}.txt")

# Dữ liệu cung hoàng đạo và món ăn
ZODIAC_DATA = [
    {
        "name": "Bạch Dương",
        "start": (3, 21),
        "end": (4, 19),
        "food": "Món nướng BBQ bốc lửa, vị cay nồng",
        "drink": "Bia tươi lạnh sâu / Nước ép táo gừng",
        "element": "Hỏa",
    },
    {
        "name": "Kim Ngưu",
        "start": (4, 20),
        "end": (5, 20),
        "food": "Bít tết bò Mỹ sốt nấm kiểu Âu sang trọng",
        "drink": "Rượu vang đỏ / Mocktail trái cây đậm vị",
        "element": "Thổ",
    },
    {
        "name": "Song Tử",
        "start": (5, 21),
        "end": (6, 21),
        "food": "Buffet lẩu nhiều vị, các món ăn vặt đa dạng",
        "drink": "Trà sữa trân châu / Trà trái cây nhiệt đới",
        "element": "Khí",
    },
    {
        "name": "Cự Giải",
        "start": (6, 22),
        "end": (7, 22),
        "food": "Cơm gia đình chuẩn vị cua đồng, cá kho tộ",
        "drink": "Nước sắn dây / Trà atiso thanh mát",
        "element": "Thủy",
    },
    {
        "name": "Sư Tử",
        "start": (7, 23),
        "end": (8, 22),
        "food": "Hải sản cao cấp, tôm hùm sốt bơ tỏi",
        "drink": "Rượu vang trắng / Cocktail sủi tăm sang trọng",
        "element": "Hỏa",
    },
    {
        "name": "Xử Nữ",
        "start": (8, 23),
        "end": (9, 22),
        "food": "Món ăn thực dưỡng Clean-eating, Salad ức gà",
        "drink": "Nước ép cần tây táo xanh / Detox chanh sả",
        "element": "Thổ",
    },
    {
        "name": "Thiên Bình",
        "start": (9, 23),
        "end": (10, 23),
        "food": "Mỳ Ý sốt kem, bánh ngọt bài trí tinh tế",
        "drink": "Trà Earl Grey ấm / Rượu vang hồng (Rosé)",
        "element": "Khí",
    },
    {
        "name": "Bọ Cạp",
        "start": (10, 24),
        "end": (11, 21),
        "food": "Lẩu Thái hải sản chua cay đậm vị, lẩu Tứ Xuyên",
        "drink": "Trà đào cam sả / Nước ngọt có ga lạnh",
        "element": "Thủy",
    },
    {
        "name": "Nhân Mã",
        "start": (11, 22),
        "end": (12, 21),
        "food": "Ẩm thực đường phố thế giới, Gà rán Hàn Quốc",
        "drink": "Bia trái cây / Nước mía hoặc soda chanh tươi",
        "element": "Hỏa",
    },
    {
        "name": "Ma Kết",
        "start": (12, 22),
        "end": (1, 19),
        "food": "Món hầm truyền thống, đuôi bò hầm thuốc bắc",
        "drink": "Trà thảo mộc ấm / Rượu mạnh pha nhẹ",
        "element": "Thổ",
    },
    {
        "name": "Bảo Bình",
        "start": (1, 20),
        "end": (2, 18),
        "food": "Món ăn biến tấu mới lạ, Sushi băng chuyền Nhật Bản",
        "drink": "Trà xanh gạo lứt (Genmaicha) / Sake lạnh",
        "element": "Khí",
    },
    {
        "name": "Song Ngư",
        "start": (2, 19),
        "end": (3, 20),
        "food": "Súp cá hồi, các món ăn thanh nhẹ lãng mạn",
        "drink": "Vang trắng ngọt / Trà hoa cúc mật ong ấm",
        "element": "Thủy",
    },
]


def get_zodiac(day, month):
  for z in ZODIAC_DATA:
    s_m, s_d = z["start"]
    e_m, e_d = z["end"]
    if s_m > e_m:
      if (month == s_m and day >= s_d) or (month == e_m and day <= e_d):
        return z
    else:
      if (month == s_m and day >= s_d) or (
          month == e_m and day <= e_d
      ) or (s_m < month < e_m):
        return z
  return ZODIAC_DATA[0]


class OptimizedZodiacApp:

  def __init__(self, root, headless=False):
    self.root = root
    self.paths = self.load_config()

    if headless:
      self.run_background_task(is_headless=True)
      return

    self.root.title(
        f"Hệ Thống Quản Lý & Xuất JSON Chuẩn ({SCRIPT_NAME}.py)"
    )
    self.root.geometry("1200x800")

    self.notebook = ttk.Notebook(root)
    self.notebook.pack(fill="both", expand=True, padx=5, pady=5)

    self.tab_chinh = ttk.Frame(self.notebook)
    self.tab_monan = ttk.Frame(self.notebook)
    self.tab_cantrong = ttk.Frame(self.notebook)
    self.tab_timkiem = ttk.Frame(self.notebook)  # Tab tra cứu và lịch sử mới

    self.notebook.add(self.tab_chinh, text="Quản Lý & Dữ Liệu")
    self.notebook.add(self.tab_monan, text="Món Ăn Theo Cung (Tách Biệt)")
    self.notebook.add(
        self.tab_cantrong, text="So Sánh, Cẩn Trọng & Xuất JSON"
    )
    self.notebook.add(
        self.tab_timkiem, text="Tìm Kiếm, Tra Cứu & Lịch Sử"
    )

    self.setup_tab_chinh()
    self.setup_tab_monan()
    self.setup_tab_cantrong()
    self.setup_tab_timkiem()

  def load_config(self):
    default_paths = {
        "ten_nguon": SCRIPT_NAME,
        "ds_nguoi_nha": r"G:\My Drive\DANHSACHPHATVIDEO\KET_QUA_JSON\DU_LIEU_GOC\DSNGUOINHA.txt",
        "ds_nguoi_mat": r"G:\My Drive\DANHSACHPHATVIDEO\KET_QUA_JSON\DU_LIEU_GOC\DANHSACHAHCM.txt",
        "ds_video": r"G:\My Drive\DANHSACHPHATVIDEO\KET_QUA_JSON\DU_LIEU_GOC\linkvideo.txt",
        "file_phu_tro": r"G:\My Drive\DANHSACHPHATVIDEO\KET_QUA_JSON\DU_LIEU_GOC\tailieu.html",
    }
    if os.path.exists(CONFIG_FILE):
      try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
          data = json.load(f)
          for k, v in default_paths.items():
            if k not in data:
              data[k] = v
          return data
      except Exception:
        pass
    return default_paths

  def save_config(self):
    try:
      os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
      with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(self.paths, f, ensure_ascii=False, indent=4)
    except Exception as e:
      print(f"Lỗi lưu cấu hình: {e}")

  def setup_tab_chinh(self):
    frame = tk.LabelFrame(
        self.tab_chinh,
        text=f" Cấu Hình Riêng Cho Script: {SCRIPT_NAME} ",
        font=("Arial", 10, "bold"),
    )
    frame.pack(fill="x", padx=10, pady=10)

    self.lbl_nha = tk.Label(
        frame,
        text=f"DS Người Nhà (.txt): {self.paths['ds_nguoi_nha']}",
        font=("Arial", 9),
    )
    self.lbl_nha.pack(anchor="w", padx=10, pady=2)
    tk.Button(
        frame,
        text="Chọn DS Người Nhà (.txt)",
        command=lambda: self.select_path(
            "ds_nguoi_nha",
            self.lbl_nha,
            [("Text Files", "*.txt"), ("All Files", "*.*")],
        ),
    ).pack(anchor="w", padx=10, pady=2)

    self.lbl_mat = tk.Label(
        frame,
        text=f"DS Người Mất (.txt): {self.paths['ds_nguoi_mat']}",
        font=("Arial", 9),
    )
    self.lbl_mat.pack(anchor="w", padx=10, pady=2)
    tk.Button(
        frame,
        text="Chọn DS Người Mất (.txt)",
        command=lambda: self.select_path(
            "ds_nguoi_mat",
            self.lbl_mat,
            [("Text Files", "*.txt"), ("All Files", "*.*")],
        ),
    ).pack(anchor="w", padx=10, pady=2)

    self.lbl_vid = tk.Label(
        frame,
        text=f"DS Link Video / VTT: {self.paths['ds_video']}",
        font=("Arial", 9),
    )
    self.lbl_vid.pack(anchor="w", padx=10, pady=2)
    tk.Button(
        frame,
        text="Chọn Tệp Link / VTT (.txt, .vtt)",
        command=lambda: self.select_path(
            "ds_video",
            self.lbl_vid,
            [("Text/VTT Files", "*.txt;*.vtt"), ("All Files", "*.*")],
        ),
    ).pack(anchor="w", padx=10, pady=2)

    self.lbl_phu = tk.Label(
        frame,
        text=f"File Nguồn Phụ (.html/.txt/.vtt): {self.paths.get('file_phu_tro', '')}",
        font=("Arial", 9),
    )
    self.lbl_phu.pack(anchor="w", padx=10, pady=2)
    tk.Button(
        frame,
        text="Chọn File Nguồn Phụ (.html, .txt, .vtt)",
        command=lambda: self.select_path(
            "file_phu_tro",
            self.lbl_phu,
            [
                ("Supported Files", "*.txt;*.html;*.vtt"),
                ("All Files", "*.*"),
            ],
        ),
    ).pack(anchor="w", padx=10, pady=2)

    tk.Button(
        frame,
        text="🚀 Chạy Tự Động & Xuất JSON (Hộp Thoại Động)",
        bg="#4CAF50",
        fg="white",
        font=("Arial", 10, "bold"),
        command=lambda: self.run_background_task(is_headless=False),
    ).pack(anchor="w", padx=10, pady=10)

  def select_path(self, key, label_widget, filetypes):
    path = filedialog.askopenfilename(title="Chọn tệp nguồn", filetypes=filetypes)
    if path:
      self.paths[key] = path
      label_widget.config(text=f"{key.upper()}: {path}")
      self.save_config()
      messagebox.showinfo(
          "Thành công", "Đã lưu đường dẫn vào tệp config riêng của script!"
      )

  def setup_tab_monan(self):
    self.tree_monan = ttk.Treeview(
        self.tab_monan,
        columns=("Zodiac", "Food", "Drink", "Element"),
        show="headings",
    )
    headers = [
        "Cung Hoàng Đạo",
        "Món Ăn Gợi Ý (Tách Biệt)",
        "Thức Uống Gợi Ý",
        "Nguyên Tố",
    ]
    widths = [150, 300, 300, 100]
    for col, head, w in zip(("Zodiac", "Food", "Drink", "Element"), headers, widths):
      self.tree_monan.heading(col, text=head)
      self.tree_monan.column(col, width=w, anchor="w")

    self.tree_monan.pack(side="left", fill="both", expand=True, padx=10, pady=10)
    for z in ZODIAC_DATA:
      self.tree_monan.insert(
          "",
          "end",
          values=(z["name"], z["food"], z["drink"], z.get("element", "")),
      )

  def setup_tab_cantrong(self):
    tk.Label(
        self.tab_cantrong,
        text=(
            "Tab này dùng để xuất báo cáo JSON chuẩn cho Script B lọc ngày"
            " (±7 ngày) với hộp thoại tùy chọn nơi lưu."
        ),
        font=("Arial", 11),
    ).pack(padx=20, pady=20)
    tk.Button(
        self.tab_cantrong,
        text="💾 Xuất JSON Chuẩn Kèm Metadata (Chọn Thư Mục Lưu)",
        bg="#9C27B0",
        fg="white",
        font=("Arial", 10, "bold"),
        command=lambda: self.run_background_task(is_headless=False),
    ).pack(padx=20, pady=10)

  def setup_tab_timkiem(self):
    """Xây dựng giao diện tìm kiếm nâng cao theo tên, thời gian, bệnh lý và lưu file .txt"""
    frame_form = tk.LabelFrame(
        self.tab_timkiem,
        text=" Bộ Lọc & Tìm Kiếm Dữ Liệu ",
        font=("Arial", 10, "bold"),
    )
    frame_form.pack(fill="x", padx=10, pady=10)

    # Ô tìm kiếm tên
    tk.Label(frame_form, text="Tìm tên trong danh sách:", font=("Arial", 9)).grid(
        row=0, column=0, sticky="w", padx=5, pady=5
    )
    self.ent_ten = tk.Entry(frame_form, width=30, font=("Arial", 9))
    self.ent_ten.grid(row=0, column=1, padx=5, pady=5)

    # Ô tìm kiếm ngày tháng năm
    tk.Label(frame_form, text="Nhập Ngày (DD/MM/YYYY):", font=("Arial", 9)).grid(
        row=1, column=0, sticky="w", padx=5, pady=5
    )
    self.ent_ngay = tk.Entry(frame_form, width=30, font=("Arial", 9))
    self.ent_ngay.grid(row=1, column=1, padx=5, pady=5)

    # Ô tìm kiếm quý
    tk.Label(frame_form, text="Nhập Quý (VD: Q1, Q2...):", font=("Arial", 9)).grid(
        row=2, column=0, sticky="w", padx=5, pady=5
    )
    self.ent_quy = tk.Entry(frame_form, width=30, font=("Arial", 9))
    self.ent_quy.grid(row=2, column=1, padx=5, pady=5)

    # Ô tìm kiếm tháng
    tk.Label(frame_form, text="Nhập Tháng (MM):", font=("Arial", 9)).grid(
        row=3, column=0, sticky="w", padx=5, pady=5
    )
    self.ent_thang = tk.Entry(frame_form, width=30, font=("Arial", 9))
    self.ent_thang.grid(row=3, column=1, padx=5, pady=5)

    # Ô tìm kiếm tuần
    tk.Label(frame_form, text="Nhập Tuần (Tuần số):", font=("Arial", 9)).grid(
        row=4, column=0, sticky="w", padx=5, pady=5
    )
    self.ent_tuan = tk.Entry(frame_form, width=30, font=("Arial", 9))
    self.ent_tuan.grid(row=4, column=1, padx=5, pady=5)

    # Ô tìm kiếm giờ, phút
    tk.Label(frame_form, text="Nhập Giờ, Phút (HH:MM):", font=("Arial", 9)).grid(
        row=5, column=0, sticky="w", padx=5, pady=5
    )
    self.ent_gio = tk.Entry(frame_form, width=30, font=("Arial", 9))
    self.ent_gio.grid(row=5, column=1, padx=5, pady=5)

    # Ô nhập bệnh bị mắc
    tk.Label(frame_form, text="Nhập Bệnh Bị Mắc:", font=("Arial", 9)).grid(
        row=6, column=0, sticky="w", padx=5, pady=5
    )
    self.ent_benh = tk.Entry(frame_form, width=30, font=("Arial", 9))
    self.ent_benh.grid(row=6, column=1, padx=5, pady=5)

    # Nút bấm lưu lại lịch sử vào bảng mẫu txt
    btn_luu_ls = tk.Button(
        frame_form,
        text="💾 Lưu Lịch Sử Vào Bảng Mẫu Txt",
        bg="#2196F3",
        fg="white",
        font=("Arial", 9, "bold"),
        command=self.luu_lich_su_vao_bang_txt,
    )
    btn_luu_ls.grid(row=7, column=0, columnspan=2, pady=10)

    # Khu vực hiển thị bảng dò tìm dữ liệu tương ứng
    frame_table = tk.LabelField = tk.LabelFrame(
        self.tab_timkiem,
        text=" Dữ Liệu Dò Tìm Giống Các Dữ Liệu Trong Bảng (.txt) ",
        font=("Arial", 10, "bold"),
    )
    frame_table.pack(fill="both", expand=True, padx=10, pady=10)

    self.txt_hien_thi = tk.Text(frame_table, wrap="word", font=("Courier", 9))
    self.txt_hien_thi.pack(side="left", fill="both", expand=True, padx=5, pady=5)
    
    scrollbar = ttk.Scrollbar(frame_table, orient="vertical", command=self.txt_hien_thi.yview)
    scrollbar.pack(side="right", fill="y")
    self.txt_hien_thi.configure(yscrollcommand=scrollbar.set)

    self.tai_va_hien_thi_bang_txt()

  def luu_lich_su_vao_bang_txt(self):
    """Thu thập thông tin từ các ô nhập liệu và ghi nối tiếp vào tệp mẫu txt để làm dữ liệu dò tìm"""
    ten = self.ent_ten.get().strip()
    ngay = self.ent_ngay.get().strip()
    quy = self.ent_quy.get().strip()
    thang = self.ent_thang.get().strip()
    tuan = self.ent_tuan.get().strip()
    gio = self.ent_gio.get().strip()
    benh = self.ent_benh.get().strip()
    thoi_gian_tao = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    dong_du_lieu = f"[{thoi_gian_tao}] | Tên: {ten} | Ngày: {ngay} | Quý: {quy} | Tháng: {thang} | Tuần: {tuan} | Giờ: {gio} | Bệnh: {benh}\n"

    try:
      with open(TXT_DATA_TABLE, "a", encoding="utf-8") as f:
        f.write(dong_du_lieu)
      messagebox.showinfo("Thành công", f"Đã lưu lịch sử dò tìm vào bảng mẫu:\n{TXT_DATA_TABLE}")
      self.tai_va_hien_thi_bang_txt()
    except Exception as e:
      messagebox.showerror("Lỗi", f"Không thể lưu dữ liệu vào tệp txt: {e}")

  def tai_va_hien_thi_bang_txt(self):
    """Tải nội dung từ bảng mẫu txt để hiển thị lên giao diện giúp dò tìm gióng dữ liệu"""
    self.txt_hien_thi.delete("1.0", tk.END)
    if os.path.exists(TXT_DATA_TABLE):
      try:
        with open(TXT_DATA_TABLE, "r", encoding="utf-8") as f:
          noi_dung = f.read()
          self.txt_hien_thi.insert(tk.END, noi_dung)
      except Exception as e:
        self.txt_hien_thi.insert(tk.END, f"Lỗi đọc bảng dữ liệu mẫu: {e}")
    else:
      self.txt_hien_thi.insert(tk.END, "(Chưa có dữ liệu lịch sử nào được lưu trong bảng mẫu txt.)")

  def ghi_nhan_index_json(self, thong_tin_xuat):
    danh_sach = []
    if os.path.exists(INDEX_FILE):
      try:
        with open(INDEX_FILE, "r", encoding="utf-8") as f:
          danh_sach = json.load(f)
      except Exception:
        danh_sach = []

    danh_sach.append(thong_tin_xuat)
    try:
      os.makedirs(os.path.dirname(INDEX_FILE), exist_ok=True)
      with open(INDEX_FILE, "w", encoding="utf-8") as f:
        json.dump(danh_sach, f, ensure_ascii=False, indent=4)
    except Exception as e:
      print(f"Lỗi ghi index tổng hợp: {e}")

  def run_background_task(self, is_headless=False):
    try:
      nguoi_nha = []
      path_nha = self.paths.get("ds_nguoi_nha", "")
      if os.path.exists(path_nha):
        with open(path_nha, "r", encoding="utf-8") as f:
          for line in f:
            parts = [p.strip() for p in line.strip().split("|")]
            if len(parts) >= 4:
              try:
                dt = datetime.strptime(parts[1], "%d/%m/%Y")
                z_info = get_zodiac(dt.day, dt.month)
                nguoi_nha.append({
                    "ten": parts[0],
                    "ngay_sinh": parts[1],
                    "gio_sinh": parts[2],
                    "gioi_tinh": parts[3],
                    "cung_sinh": z_info["name"],
                    "nguyen_to": z_info.get("element", ""),
                })
              except Exception:
                pass

      nguoi_mat = []
      path_mat = self.paths.get("ds_nguoi_mat", "")
      if os.path.exists(path_mat):
        with open(path_mat, "r", encoding="utf-8") as f:
          for line in f:
            parts = [p.strip() for p in line.strip().split("|")]
            if len(parts) >= 4:
              try:
                dt_b = datetime.strptime(parts[1], "%d/%m/%Y")
                dt_d = datetime.strptime(parts[2], "%d/%m/%Y")
                nguoi_mat.append({
                    "ten": parts[0],
                    "ngay_sinh": parts[1],
                    "ngay_mat": parts[2],
                    "gio_mat": parts[3],
                    "cung_sinh": get_zodiac(dt_b.day, dt_b.month)["name"],
                    "cung_mat": get_zodiac(dt_d.day, dt_d.month)["name"],
                })
              except Exception:
                pass

      video_links = []
      path_vid = self.paths.get("ds_video", "")
      if os.path.exists(path_vid):
        with open(path_vid, "r", encoding="utf-8") as f:
          video_links = [l.strip() for l in f if l.strip()]

      path_phu = self.paths.get("file_phu_tro", "")

      current_year = datetime.now().year
      h = (current_year // 24) % 24
      m = current_year % 60
      if not (9 <= h <= 16):
        h = 9 + (h % 8)
      broadcast_time = f"{h:02d}:{m:02d}"

      link_idx = 0
      for item in nguoi_nha:
        item["gio_phat_video"] = broadcast_time
        item["link_video"] = (
            video_links[link_idx % len(video_links)] if video_links else ""
        )
        link_idx += 1

      for item in nguoi_mat:
        item["gio_phat_video"] = broadcast_time
        item["link_video"] = (
            video_links[link_idx % len(video_links)] if video_links else ""
        )
        link_idx += 1

      now = datetime.now()
      date_from = (now - timedelta(days=7)).strftime("%Y-%m-%d %H:%M:%S")
      date_to = (now + timedelta(days=7)).strftime("%Y-%m-%d %H:%M:%S")

      thoi_gian_str = now.strftime("%Y%m%d_%H%M%S")
      
      # Tên thư mục nguồn mặc định lấy từ đường dẫn DS người nhà hoặc tên tệp script
      ten_thu_muc_nguon = "DU_LIEU_GOC"
      default_filename = f"{SCRIPT_NAME}_{ten_thu_muc_nguon}_{thoi_gian_str}.json"

      if is_headless:
        output_dir = r"G:\My Drive\DANHSACHPHATVIDEO\KET_QUA_JSON"
        os.makedirs(output_dir, exist_ok=True)
        out_path = os.path.join(output_dir, default_filename)
      else:
        # Mở trực tiếp hộp thoại lưu file (asksaveasfilename) đặt sẵn tên động chuẩn theo công thức yêu cầu
        f_types = [("JSON Files", "*.json"), ("All Files", "*.*")]
        out_path = filedialog.asksaveasfilename(
            title="Lưu tệp JSON đầu ra",
            initialfile=default_filename,
            defaultextension=".json",
            filetypes=f_types
        )
        if not out_path:
          return  # Người dùng bấm hủy

      payload = {
          "metadata": {
              "script_su_dung": f"{SCRIPT_NAME}.py",
              "timestamp": now.strftime("%Y-%m-%d %H:%M:%S"),
              "date_minus_7_days": date_from[:10],
              "date_plus_7_days": date_to[:10],
              "thu_muc_nguon": r"G:\My Drive\DANHSACHPHATVIDEO\KET_QUA_JSON\DU_LIEU_GOC",
              "file_nguon_quet": [path_nha, path_mat, path_vid, path_phu],
          },
          "people": {
              "nhom_nguoi_nha": nguoi_nha,
              "nhom_nguoi_mat": nguoi_mat,
          },
          "ref_numbers": [len(nguoi_nha), len(nguoi_mat), len(video_links)],
          "custom_tabs": {
              "danh_sach_link_youtube": video_links,
          },
      }

      os.makedirs(os.path.dirname(out_path), exist_ok=True)
      with open(out_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=4)

      self.ghi_nhan_index_json({
          "script_tao": f"{SCRIPT_NAME}.py",
          "file_json_gan_nhap_nhat": out_path,
          "thoi_gian": now.strftime("%Y-%m-%d %H:%M:%S"),
          "danh_sach_file_nguon": [path_nha, path_mat, path_vid, path_phu],
      })

      if is_headless:
        print(f"[{SCRIPT_NAME}.py] Đã xuất tệp JSON chuẩn tại: {out_path}")
      else:
        messagebox.showinfo(
            "Thành công", f"Đã xuất và lưu tệp JSON thành công tại:\n{out_path}"
        )
    except Exception as e:
      if is_headless:
        print(f"[{SCRIPT_NAME}.py] Lỗi chạy ngầm: {e}")
        sys.exit(1)
      else:
        messagebox.showerror("Lỗi", f"Lỗi thực thi: {e}")


if __name__ == "__main__":
  if len(sys.argv) > 1 and sys.argv[1] == "--gui":
    goc = tk.Tk()
    app = OptimizedZodiacApp(goc, headless=False)
    goc.mainloop()
  else:
    print(f"[{SCRIPT_NAME}.py] Đang chạy ngầm tự động xử lý dữ liệu...")
    root_ao = tk.Tk()
    root_ao.withdraw()
    OptimizedZodiacApp(root_ao, headless=True)
    root_ao.destroy()
    print(f"[{SCRIPT_NAME}.py] Hoàn tất!")
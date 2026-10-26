from datetime import datetime
import json
import os
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog, ttk
import urllib.request

# Dữ liệu cung hoàng đạo, thời gian, món ăn và món uống
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


class FullZodiacApp:

  def __init__(self, root):
    self.root = root
    self.root.title("Hệ Thống Quản Lý Cung Hoàng Đạo, Ẩm Thực & So Sánh")
    self.root.geometry("1100x700")

    self.nguoi_nha_data = []
    self.nguoi_mat_data = []
    self.video_links = []

    # Sử dụng Notebook để tạo các Tab
    self.notebook = ttk.Notebook(root)
    self.notebook.pack(fill="both", expand=True, padx=5, pady=5)

    # Khởi tạo các Tab theo yêu cầu
    self.tab_chinh = ttk.Frame(self.notebook)
    self.tab_nguoinha = ttk.Frame(self.notebook)
    self.tab_nguoimat = ttk.Frame(self.notebook)
    self.tab_monan = ttk.Frame(self.notebook)
    self.tab_cantrong = ttk.Frame(self.notebook)

    self.notebook.add(self.tab_chinh, text="Quản Lý & Thông Báo")
    self.notebook.add(self.tab_nguoinha, text="DS Người Nhà (.txt)")
    self.notebook.add(self.tab_nguoimat, text="DS Người Mất (.txt)")
    self.notebook.add(self.tab_monan, text="Món Ăn Theo Ngày Hiện Tại & Sắp Tới")
    self.notebook.add(
        self.tab_cantrong, text="So Sánh, Cẩn Trọng & Xuất JSON"
    )

    self.setup_tab_chinh()
    self.setup_tab_nguoinha()
    self.setup_tab_nguoimat()
    self.setup_tab_monan()
    self.setup_tab_cantrong()

  # --- TAB 1: Giao diện chính cũ (Giữ nguyên) ---
  def setup_tab_chinh(self):
    input_frame = tk.LabelFrame(
        self.tab_chinh, text=" Thông tin người dùng ", font=("Arial", 11, "bold")
    )
    input_frame.pack(fill="x", padx=10, pady=10)

    tk.Label(input_frame, text="Họ tên:", font=("Arial", 10)).grid(
        row=0, column=0, sticky="w", padx=5, pady=5
    )
    self.ent_name = tk.Entry(input_frame, font=("Arial", 10), width=18)
    self.ent_name.grid(row=0, column=1, padx=5, pady=5)

    tk.Label(
        input_frame, text="Ngày sinh (DD/MM/YYYY):", font=("Arial", 10)
    ).grid(row=0, column=2, sticky="w", padx=5, pady=5)
    self.ent_dob = tk.Entry(input_frame, font=("Arial", 10), width=12)
    self.ent_dob.grid(row=0, column=3, padx=5, pady=5)

    tk.Label(input_frame, text="Giới tính:", font=("Arial", 10)).grid(
        row=0, column=4, sticky="w", padx=5, pady=5
    )
    self.cb_gender = ttk.Combobox(
        input_frame,
        values=["Nam", "Nữ", "Khác"],
        font=("Arial", 10),
        width=8,
        state="readonly",
    )
    self.cb_gender.grid(row=0, column=5, padx=5, pady=5)
    self.cb_gender.current(0)

    btn_frame = tk.Frame(self.tab_chinh)
    btn_frame.pack(fill="x", padx=10, pady=5)

    tk.Button(
        btn_frame,
        text="Thêm người",
        bg="#4CAF50",
        fg="white",
        font=("Arial", 9, "bold"),
        command=self.add_person,
    ).pack(side="left", padx=3)
    tk.Button(
        btn_frame,
        text="Xóa đã chọn",
        bg="#f44336",
        fg="white",
        font=("Arial", 9, "bold"),
        command=self.delete_person,
    ).pack(side="left", padx=3)
    tk.Button(
        btn_frame,
        text="📥 Nhập từ Google Sheet",
        bg="#0F9D58",
        fg="white",
        font=("Arial", 9, "bold"),
        command=self.import_from_google_sheet,
    ).pack(side="left", padx=3)
    tk.Button(
        btn_frame,
        text="Mở tệp .txt Link Video",
        bg="#2196F3",
        fg="white",
        font=("Arial", 9, "bold"),
        command=self.load_video_file,
    ).pack(side="left", padx=3)
    tk.Button(
        btn_frame,
        text="Kiểm tra thông báo & Video",
        bg="#FF9800",
        fg="white",
        font=("Arial", 9, "bold"),
        command=self.check_notifications,
    ).pack(side="left", padx=3)

    table_frame = tk.Frame(self.tab_chinh)
    table_frame.pack(fill="both", expand=True, padx=10, pady=10)

    columns = (
        "Name",
        "Gender",
        "DOB",
        "Zodiac",
        "Food",
        "Drink",
        "Status/Alert",
    )
    self.tree_chinh = ttk.Treeview(
        table_frame, columns=columns, show="headings"
    )

    headers = [
        "Họ tên",
        "Giới tính",
        "Ngày sinh",
        "Cung",
        "Món ăn gợi ý",
        "Món uống đi kèm",
        "Trạng thái / Thông báo",
    ]
    widths = [120, 70, 90, 100, 180, 180, 170]

    for col, head, width in zip(columns, headers, widths):
        self.tree_chinh.heading(col, text=head)
        self.tree_chinh.column(col, width=width, anchor="w")

    scrollbar = ttk.Scrollbar(
        table_frame, orient="vertical", command=self.tree_chinh.yview
    )
    self.tree_chinh.configure(yscrollcommand=scrollbar.set)
    self.tree_chinh.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

  # --- TAB 2: Danh sách Người Nhà ---
  def setup_tab_nguoinha(self):
    frame_top = tk.Frame(self.tab_nguoinha)
    frame_top.pack(fill="x", padx=10, pady=10)

    tk.Button(
        frame_top,
        text="Nhập DS Người Nhà từ TXT",
        bg="#4CAF50",
        fg="white",
        font=("Arial", 10, "bold"),
        command=self.load_nguoi_nha_file,
    ).pack(side="left", padx=5)

    self.tree_nguoinha = ttk.Treeview(
        self.tab_nguoinha,
        columns=("Name", "DOB", "Hour", "Gender", "Zodiac"),
        show="headings",
    )
    headers = ["Họ Tên", "Ngày Sinh", "Giờ Sinh", "Giới Tính (T/G)", "Cung Sinh"]
    widths = [200, 120, 100, 120, 150]
    for col, head, w in zip(
        ("Name", "DOB", "Hour", "Gender", "Zodiac"), headers, widths
    ):
      self.tree_nguoinha.heading(col, text=head)
      self.tree_nguoinha.column(col, width=w, anchor="w")

    scrollbar = ttk.Scrollbar(
        self.tab_nguoinha, orient="vertical", command=self.tree_nguoinha.yview
    )
    self.tree_nguoinha.configure(yscrollcommand=scrollbar.set)
    self.tree_nguoinha.pack(
        side="left", fill="both", expand=True, padx=(10, 0), pady=10
    )
    scrollbar.pack(side="right", fill="y", pady=10, padx=(0, 10))

  # --- TAB 3: Danh sách Người Mất ---
  def setup_tab_nguoimat(self):
    frame_top = tk.Frame(self.tab_nguoimat)
    frame_top.pack(fill="x", padx=10, pady=10)

    tk.Button(
        frame_top,
        text="Nhập DS Người Mất từ TXT",
        bg="#FF9800",
        fg="white",
        font=("Arial", 10, "bold"),
        command=self.load_nguoi_mat_file,
    ).pack(side="left", padx=5)

    self.tree_nguoimat = ttk.Treeview(
        self.tab_nguoimat,
        columns=("Name", "DOB", "DOD", "DOD_Hour", "Z_Birth", "Z_Death"),
        show="headings",
    )
    headers = [
        "Họ Tên",
        "Ngày Sinh",
        "Ngày Mất",
        "Giờ Mất",
        "Cung Sinh",
        "Cung Mất",
    ]
    widths = [180, 110, 110, 90, 130, 130]
    for col, head, w in zip(
        ("Name", "DOB", "DOD", "DOD_Hour", "Z_Birth", "Z_Death"), headers, widths
    ):
      self.tree_nguoimat.heading(col, text=head)
      self.tree_nguoimat.column(col, width=w, anchor="w")

    scrollbar = ttk.Scrollbar(
        self.tab_nguoimat, orient="vertical", command=self.tree_nguoimat.yview
    )
    self.tree_nguoimat.configure(yscrollcommand=scrollbar.set)
    self.tree_nguoimat.pack(
        side="left", fill="both", expand=True, padx=(10, 0), pady=10
    )
    scrollbar.pack(side="right", fill="y", pady=10, padx=(0, 10))

  # --- TAB 4: Món ăn theo ngày hiện tại và sắp tới ---
  def setup_tab_monan(self):
    frame_top = tk.Frame(self.tab_monan)
    frame_top.pack(fill="x", padx=10, pady=10)

    tk.Button(
        frame_top,
        text="🔄 Cập Nhật Món Ăn Hiện Tại & Sắp Tới",
        bg="#3F51B5",
        fg="white",
        font=("Arial", 10, "bold"),
        command=self.update_food_view,
    ).pack(side="left", padx=5)

    self.tree_monan = ttk.Treeview(
        self.tab_monan,
        columns=("Zodiac", "Period", "Food", "Drink", "Element"),
        show="headings",
    )
    headers = [
        "Cung Hoàng Đạo",
        "Trạng Thái Thời Gian",
        "Món Ăn Gợi Ý",
        "Thức Uống Gợi Ý",
        "Nguyên Tố",
    ]
    widths = [150, 180, 250, 250, 100]
    for col, head, w in zip(
        ("Zodiac", "Period", "Food", "Drink", "Element"), headers, widths
    ):
      self.tree_monan.heading(col, text=head)
      self.tree_monan.column(col, width=w, anchor="w")

    scrollbar = ttk.Scrollbar(
        self.tab_monan, orient="vertical", command=self.tree_monan.yview
    )
    self.tree_monan.configure(yscrollcommand=scrollbar.set)
    self.tree_monan.pack(
        side="left", fill="both", expand=True, padx=(10, 0), pady=10
    )
    scrollbar.pack(side="right", fill="y", pady=10, padx=(0, 10))

    # Tự động nạp lần đầu
    self.update_food_view()

  def update_food_view(self):
    for row in self.tree_monan.get_children():
      self.tree_monan.delete(row)

    today = datetime.now()
    current_zodiac = get_zodiac(today.day, today.month)

    for z in ZODIAC_DATA:
      status = "Bình thường"
      if z["name"] == current_zodiac["name"]:
        status = "✨ Cung hiện tại (Hôm nay)"
      else:
        # Kiểm tra xem có sắp tới không (trong vòng 10 ngày tới)
        try:
          s_m, s_d = z["start"]
          z_date = datetime(today.year, s_m, s_d)
          delta = (z_date - today).days
          if 0 <= delta <= 10:
            status = f"⚠️ Sắp tới ({delta} ngày nữa)"
        except Exception:
          pass

      self.tree_monan.insert(
          "",
          "end",
          values=(
              z["name"],
              status,
              z["food"],
              z["drink"],
              z.get("element", ""),
          ),
      )

  # --- TAB 5: So sánh, Cẩn trọng & Xuất JSON ---
  def setup_tab_cantrong(self):
    frame_top = tk.Frame(self.tab_cantrong)
    frame_top.pack(fill="x", padx=10, pady=10)

    tk.Button(
        frame_top,
        text="🔄 Cập Nhật Đối Chiếu",
        bg="#009688",
        fg="white",
        font=("Arial", 10, "bold"),
        command=self.update_caution_view,
    ).pack(side="left", padx=5)
    tk.Button(
        frame_top,
        text="💾 Xuất File JSON Tùy Chọn",
        bg="#9C27B0",
        fg="white",
        font=("Arial", 10, "bold"),
        command=self.export_json_file,
    ).pack(side="left", padx=5)

    self.tree_cantrong = ttk.Treeview(
        self.tab_cantrong,
        columns=("Name", "Zodiac", "Element", "Warning", "VideoTime", "Link"),
        show="headings",
    )
    headers = [
        "Họ Tên Người Nhà",
        "Cung Sinh",
        "Nguyên Tố",
        "Dự Đoán Cẩn Trọng (So Với Người Mất)",
        "Giờ Phát",
        "Link Video",
    ]
    widths = [150, 100, 90, 300, 100, 200]
    for col, head, w in zip(
        ("Name", "Zodiac", "Element", "Warning", "VideoTime", "Link"),
        headers,
        widths,
    ):
      self.tree_cantrong.heading(col, text=head)
      self.tree_cantrong.column(col, width=w, anchor="w")

    scrollbar = ttk.Scrollbar(
        self.tab_cantrong, orient="vertical", command=self.tree_cantrong.yview
    )
    self.tree_cantrong.configure(yscrollcommand=scrollbar.set)
    self.tree_cantrong.pack(
        side="left", fill="both", expand=True, padx=(10, 0), pady=10
    )
    scrollbar.pack(side="right", fill="y", pady=10, padx=(0, 10))

  # --- Các hàm xử lý nghiệp vụ ---
  def insert_to_table_chinh(self, name, gender, dob_str):
    try:
      dob = datetime.strptime(dob_str.strip(), "%d/%m/%Y")
    except ValueError:
      return False

    zodiac = get_zodiac(dob.day, dob.month)
    current_year = datetime.now().year
    s_m, s_d = zodiac["start"]
    try:
      zodiac_start_date = datetime(current_year, s_m, s_d)
    except ValueError:
      zodiac_start_date = datetime(current_year, s_m, 28)

    today = datetime.now()
    delta = (zodiac_start_date - today).days

    status = "Bình thường"
    if 0 <= delta <= 3:
      status = f"⚠️ Sắp tới cung ({delta} ngày nữa)"
    elif delta < 0 and delta >= -30:
      status = "✨ Đang trong mùa cung"

    self.tree_chinh.insert(
        "",
        "end",
        values=(
            name.strip(),
            gender.strip(),
            dob_str.strip(),
            zodiac["name"],
            zodiac["food"],
            zodiac["drink"],
            status,
        ),
    )
    return True

  def add_person(self):
    name = self.ent_name.get().strip()
    dob_str = self.ent_dob.get().strip()
    gender = self.cb_gender.get()

    if not name or not dob_str:
      messagebox.showerror(
          "Lỗi", "Vui lòng nhập đầy đủ Họ tên và Ngày sinh!"
      )
      return

    success = self.insert_to_table_chinh(name, gender, dob_str)
    if not success:
      messagebox.showerror(
          "Lỗi định dạng", "Ngày sinh phải có định dạng DD/MM/YYYY (VD: 25/05/2000)"
      )
      return

    self.ent_name.delete(0, tk.END)
    self.ent_dob.delete(0, tk.END)
    messagebox.showinfo("Thành công", f"Đã thêm {name} vào danh sách chính!")

  def delete_person(self):
    selected_items = self.tree_chinh.selection()
    if not selected_items:
      messagebox.showwarning(
          "Cảnh báo", "Vui lòng chọn dòng cần xóa trong bảng chính!"
      )
      return
    for item in selected_items:
      self.tree_chinh.delete(item)
    messagebox.showinfo("Thành công", "Đã xóa người được chọn.")

  def import_from_google_sheet(self):
    sheet_url = simpledialog.askstring(
        "Nhập từ Google Sheet",
        "Dán đường dẫn xuất CSV của Google Sheet vào đây:\n(Ví dụ: https://docs.google.com/spreadsheets/d/.../export?format=csv)",
    )
    if not sheet_url:
      return
    try:
      req = urllib.request.Request(
          sheet_url, headers={"User-Agent": "Mozilla/5.0"}
      )
      with urllib.request.urlopen(req) as response:
        csv_data = response.read().decode("utf-8")

      lines = csv_data.splitlines()
      count = 0
      for line in lines[1:]:
        parts = [p.strip() for p in line.split(",")]
        if len(parts) >= 3:
          if self.insert_to_table_chinh(parts[0], parts[2], parts[1]):
            count += 1
      messagebox.showinfo(
          "Thành công", f"Đã nhập thành công {count} bản ghi từ Google Sheet!"
      )
    except Exception as e:
      messagebox.showerror("Lỗi", f"Không thể đọc dữ liệu: {e}")

  def load_video_file(self):
    file_path = filedialog.askopenfilename(
        initialdir=r"G:\My Drive\DANHSACHPHATVIDEO\KET_QUA_JSON",
        title="Chọn tệp txt chứa link video",
        filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")],
    )
    if file_path:
      try:
        with open(file_path, "r", encoding="utf-8") as f:
          self.video_links = [
              line.strip() for line in f.readlines() if line.strip()
          ]
        messagebox.showinfo(
            "Thành công",
            f"Đã tải thành công {len(self.video_links)} link video!",
        )
        self.update_caution_view()
      except Exception as e:
        messagebox.showerror("Lỗi", f"Không thể đọc tệp: {e}")

  def check_notifications(self):
    notif_msg = "--- THÔNG BÁO SỰ KIỆN & VIDEO --- \n\n"
    has_alert = False

    for child in self.tree_chinh.get_children():
      vals = self.tree_chinh.item(child, "values")
      name, status = vals[0], vals[6]
      if "Sắp tới" in status or "Đang trong mùa" in status:
        has_alert = True
        notif_msg += f"👤 {name}: {status}\n"

    if has_alert:
      notif_msg += "\n🎬 Danh sách link video đã lưu:\n" + (
          "\n".join(self.video_links)
          if self.video_links
          else "(Chưa có link video)"
      )
    else:
      notif_msg += (
          "Hiện không có ai sắp tới ngày cung hoàng đạo trong vòng 3 ngày tới.\n"
      )
      if self.video_links:
        notif_msg += "\n🎬 Các video đã nạp sẵn:\n" + "\n".join(
            self.video_links
        )

    top = tk.Toplevel(self.root)
    top.title("Thông báo chi tiết")
    top.geometry("500x400")
    txt_box = tk.Text(top, wrap="word", font=("Arial", 10))
    txt_box.pack(fill="both", expand=True, padx=10, pady=10)
    txt_box.insert("1.0", notif_msg)
    txt_box.config(state="disabled")

  def load_nguoi_nha_file(self):
    path = filedialog.askopenfilename(
        initialdir=r"G:\My Drive\DANHSACHPHATVIDEO\KET_QUA_JSON",
        title="Chọn tệp DSNGUOINHA.txt",
        filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")],
    )
    if not path:
      return
    try:
      with open(path, "r", encoding="utf-8") as f:
        lines = f.readlines()
      self.nguoi_nhà_data.clear()
      for row in self.tree_nguoinha.get_children():
        self.tree_nguoinha.delete(row)

      for line in lines:
        parts = [p.strip() for p in line.strip().split("|")]
        if len(parts) >= 4:
          name, dob_str, hour, gender = parts[0], parts[1], parts[2], parts[3]
          try:
            dt = datetime.strptime(dob_str, "%d/%m/%Y")
            z_info = get_zodiac(dt.day, dt.month)
            zodiac = z_info["name"]
            element = z_info.get("element", "")
          except Exception:
            zodiac = "Không rõ"
            element = ""

          self.nguoi_nhà_data.append({
              "name": name,
              "dob": dob_str,
              "hour": hour,
              "gender": gender,
              "zodiac": zodiac,
              "element": element,
          })
          self.tree_nguoinha.insert(
              "",
              "end",
              values=(
                  name,
                  dob_str,
                  hour,
                  "Nam (T)" if gender == "T" else "Nữ (G)",
                  zodiac,
              ),
          )
      messagebox.showinfo(
          "Thành công",
          f"Đã nạp {len(self.nguoi_nhà_data)} bản ghi người nhà!",
      )
      self.update_caution_view()
    except Exception as e:
      messagebox.showerror("Lỗi", f"Không đọc được tệp: {e}")

  def load_nguoi_mat_file(self):
    path = filedialog.askopenfilename(
        initialdir=r"G:\My Drive\DANHSACHPHATVIDEO\KET_QUA_JSON",
        title="Chọn tệp DANHSACHAHCM.txt",
        filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")],
    )
    if not path:
      return
    try:
      with open(path, "r", encoding="utf-8") as f:
        lines = f.readlines()
      self.nguoi_mat_data.clear()
      for row in self.tree_nguoimat.get_children():
        self.tree_nguoimat.delete(row)

      for line in lines:
        parts = [p.strip() for p in line.strip().split("|")]
        if len(parts) >= 4:
          name, dob_str, dod_str, dod_hour = (
              parts[0],
              parts[1],
              parts[2],
              parts[3],
          )
          try:
            dt_b = datetime.strptime(dob_str, "%d/%m/%Y")
            z_birth = get_zodiac(dt_b.day, dt_b.month)["name"]
          except Exception:
            z_birth = "Không rõ"

          try:
            dt_d = datetime.strptime(dod_str, "%d/%m/%Y")
            z_death = get_zodiac(dt_d.day, dt_d.month)["name"]
          except Exception:
            z_death = "Không rõ"

          self.nguoi_mat_data.append({
              "name": name,
              "dob": dob_str,
              "dod": dod_str,
              "dod_hour": dod_hour,
              "z_birth": z_birth,
              "z_death": z_death,
          })
          self.tree_nguoimat.insert(
              "",
              "end",
              values=(name, dob_str, dod_str, dod_hour, z_birth, z_death),
          )
      messagebox.showinfo(
          "Thành công",
          f"Đã nạp {len(self.nguoi_mat_data)} bản ghi người mất!",
      )
      self.update_caution_view()
    except Exception as e:
      messagebox.showerror("Lỗi", f"Không đọc được tệp: {e}")

  def calculate_broadcast_time(self):
    current_year = 2026
    h = (current_year // 24) % 24
    m = current_year % 60
    if m >= 60:
      m = 59
    # Khung giờ đẹp 9h đến 16h
    if not (9 <= h <= 16):
      h = 9 + (h % 8)
    return f"{h:02d}:{m:02d}"

  def evaluate_caution_logic(self, member_zodiac, member_element):
    if not self.nguoi_mat_data:
      return "Chưa có dữ liệu người mất để đối chiếu."
    warnings = []
    for m in self.nguoi_mat_data:
      m_name = m["name"]
      z_death = m["z_death"]
      death_element = ""
      for z in ZODIAC_DATA:
        if z["name"] == z_death:
          death_element = z.get("element", "")
          break

      if member_zodiac == z_death:
        warnings.append(
            f"⚠️ Trùng cung mất với {m_name} ({z_death}): Cẩn trọng sức khỏe."
        )
      elif member_element == death_element and member_element:
        warnings.append(
            f"✨ Cùng nguyên tố ({member_element}) với cung mất của {m_name}."
        )

    if not warnings:
      return "Bình ổn, không xung khắc trực tiếp."
    return " | ".join(warnings)

  def update_caution_view(self):
    for row in self.tree_cantrong.get_children():
      self.tree_cantrong.delete(row)

    link_idx = 0
    calculated_time = self.calculate_broadcast_time()

    for item in self.nguoi_nhà_data:
      link = (
          self.video_links[link_idx % len(self.video_links)]
          if self.video_links
          else "Chưa có link"
      )
      link_idx += 1
      warning_text = self.evaluate_caution_logic(
          item["zodiac"], item["element"]
      )
      self.tree_cantrong.insert(
          "",
          "end",
          values=(
              item["name"],
              item["zodiac"],
              item["element"],
              warning_text,
              calculated_time,
              link,
          ),
      )

  def export_json_file(self):
    if not self.nguoi_nhà_data and not self.nguoi_mat_data:
      messagebox.showwarning(
          "Cảnh báo", "Chưa có dữ liệu để xuất file JSON!"
      )
      return

    file_path = filedialog.asksaveasfilename(
        initialdir=r"G:\My Drive\DANHSACHPHATVIDEO\KET_QUA_JSON",
        title="Lưu tệp JSON kết quả",
        defaultextension=".json",
        filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")],
    )
    if not file_path:
      return

    calculated_time = self.calculate_broadcast_time()
    link_idx = 0

    nhom_1_payload = []
    for item in self.nguoi_nhà_data:
      link = (
          self.video_links[link_idx % len(self.video_links)]
          if self.video_links
          else ""
      )
      link_idx += 1
      warning_text = self.evaluate_caution_logic(
          item["zodiac"], item["element"]
      )
      nhom_1_payload.append({
          "ten": item["name"],
          "ngay_sinh": item["dob"],
          "gio_sinh": item["hour"],
          "gioi_tinh": item["gender"],
          "cung_sinh": item["zodiac"],
          "nguyen_to": item["element"],
          "du_doan_can_trong": warning_text,
          "gio_phat_video": calculated_time,
          "link_video": link,
      })

    nhom_2_payload = []
    for item in self.nguoi_mat_data:
      link = (
          self.video_links[link_idx % len(self.video_links)]
          if self.video_links
          else ""
      )
      link_idx += 1
      nhom_2_payload.append({
          "ten": item["name"],
          "ngay_sinh": item["dob"],
          "ngay_mat": item["dod"],
          "gio_mat": item["dod_hour"],
          "cung_sinh": item["z_birth"],
          "cung_mat": item["z_death"],
          "gio_phat_video": calculated_time,
          "link_video": link,
      })

    export_payload = {
        "export_timestamp": datetime.now().isoformat(),
        "status": "success",
        "data": {"nhom_nguoi_nha": nhom_1_payload, "nhom_nguoi_mat": nhom_2_payload},
    }

    try:
      os.makedirs(os.path.dirname(file_path), exist_ok=True)
      with open(file_path, "w", encoding="utf-8") as f:
        json.dump(export_payload, f, ensure_ascii=False, indent=4)
      messagebox.showinfo(
          "Thành công", f"Đã lưu tệp JSON thành công tại:\n{file_path}"
      )
    except Exception as e:
      messagebox.showerror("Lỗi", f"Không thể lưu file: {e}")


if __name__ == "__main__":
  root = tk.Tk()
  app = FullZodiacApp(root)
  root.mainloop()
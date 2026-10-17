import glob
import json
import os
import subprocess

def main():
    results = []
    # Quét toàn bộ file .py có sẵn trong thư mục scripts của GitHub
    python_files = sorted(glob.glob("scripts/*.py"))

    if not python_files:
        print("⚠️ Chưa có tệp Python nào trong thư mục scripts/. Hãy thêm tệp vào đây.")

    for py_file in python_files:
        base_name = os.path.splitext(os.path.basename(py_file))[0]
        json_file = f"data/{base_name}.json"

        print(f"🚀 Đang chạy: {py_file}...")

        try:
            process = subprocess.run(
                ["python", py_file], capture_output=True, text=True, timeout=300
            )

            status = "Thành công" if process.returncode == 0 else "Thất bại"

            file_data = {}
            if os.path.exists(json_file):
                with open(json_file, "r", encoding="utf-8") as f:
                    file_data = json.load(f)

            results.append({
                "task": base_name,
                "status": status,
                "output": file_data
            })

        except Exception as e:
            print(f"❌ Lỗi: {e}")
            results.append({"task": base_name, "status": "Lỗi", "error": str(e)})

    # Xuất file kết quả ra trang web
    with open("aggregated_output.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=4)

    print("🎉 Hoàn tất!")

if __name__ == "__main__":
    main()

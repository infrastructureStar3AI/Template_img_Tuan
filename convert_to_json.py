import os
import json
import re

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RAW_PROMPT_DIR = os.path.join(BASE_DIR, "raw_prompts")
TEMPLATE_DIR = os.path.join(BASE_DIR, "templates")
INDEX_FILE = os.path.join(BASE_DIR, "template_index.json")

template_index = []

def parse_prompt_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    blocks = re.findall(r"\[(.*?)\](:)?\s*(.*?)(?=\n\[|$)", content, re.DOTALL)

    data = {}
    for key, colon, value in blocks:
        cleaned_key = key.strip().lower().replace(" ", "_")
        cleaned_value = value.strip().replace("\n", " ")
        data[cleaned_key] = cleaned_value

    main_color, accent_color = "#CCCCCC", "#FF0000"
    if "dominant_color" in data:
        main_match = re.search(r"Main:\s.*?(#\w+)", data["dominant_color"])
        accent_match = re.search(r"Accent:\s.*?(#\w+)", data["dominant_color"])
        if main_match: main_color = main_match.group(1)
        if accent_match: accent_color = accent_match.group(1)

    return data, main_color, accent_color

def convert_all():
    for root, dirs, files in os.walk(RAW_PROMPT_DIR):
        for filename in files:
            if not filename.endswith(".txt"):
                continue

            file_path = os.path.join(root, filename)
            rel_path = os.path.relpath(file_path, RAW_PROMPT_DIR)
            parts = rel_path.split(os.sep)

            if len(parts) != 3:
                print(f"⚠️  Bỏ qua file không đúng cấp thư mục: {rel_path}")
                continue

            category, product_type, txt_file = parts
            template_name = txt_file.replace(".txt", "")

            try:
                print(f"🔄 Đang xử lý: {category}/{product_type}/{template_name}")
                data, main_color, accent_color = parse_prompt_file(file_path)

                output_data = {
                    "name": template_name,
                    "category": category,
                    "product_type": product_type,
                    "style_tag": [],
                    "prompt_base": " ".join([
                        data.get("overall_atmosphere", ""),
                        data.get("general_environment", ""),
                        data.get("model_pose", ""),
                        data.get("product_placement", ""),
                        data.get("supporting_elements", ""),
                        data.get("detailed_product_description", "")
                    ]),
                    "negative_prompt": data.get("negative_prompt", ""),
                    "model": "imagen4",
                    "dominant_colors": {
                        "main": main_color,
                        "accent": accent_color
                    },
                    "overlay": {
                        "text": {
                            "headline": {
                                "text_key": "main_text",
                                "font": "Futura-Bold.ttf",
                                "size": 28,
                                "color": accent_color,
                                "x": 100,
                                "y": 100
                            },
                            "cta": {
                                "text_key": "cta",
                                "font": "Futura-Regular.ttf",
                                "size": 20,
                                "color": main_color,
                                "x": 100,
                                "y": 150
                            }
                        },
                        "logo": {
                            "x": 1400,
                            "y": 1300,
                            "width": 150,
                            "height": 50
                        }
                    }
                }

                out_dir = os.path.join(TEMPLATE_DIR, category, product_type)
                os.makedirs(out_dir, exist_ok=True)

                out_path = os.path.join(out_dir, f"{template_name}.json")
                with open(out_path, "w", encoding="utf-8") as f:
                    json.dump(output_data, f, indent=2, ensure_ascii=False)

                template_index.append({
                    "name": template_name,
                    "category": category,
                    "product_type": product_type,
                    "path": f"{category}/{product_type}/{template_name}.json"
                })

                print(f"✅ Đã tạo: {out_path}")

            except Exception as e:
                print(f"❌ Lỗi khi xử lý {filename}: {str(e)}")

    with open(INDEX_FILE, "w", encoding="utf-8") as f:
        json.dump(template_index, f, indent=2, ensure_ascii=False)
    print(f"📦 Đã tạo file index: {INDEX_FILE}")

if __name__ == "__main__":
    convert_all()

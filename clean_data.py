import json
import re
import os

def clean_text(text):
    text = re.sub(r'<[^>]+>', '', text)
    text = re.sub(r'!\[.*?\]\(.*?\)', '', text)
    text = re.sub(r'\[([^\]]+)\]\([^)]*\)', r'\1', text)
    text = re.sub(r'``````', '', text, flags=re.DOTALL)
    text = re.sub(r'`([^`]*)`', r'\1', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def clean_data(input_file, output_file):
    if not os.path.exists(input_file):
        print(f"ERROR: {input_file} not found. Please add your raw data file.")
        return
    with open(input_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    seen = set()
    cleaned = []
    for item in data:
        txt = clean_text(item.get('text', ''))
        if not txt or txt in seen:
            continue
        seen.add(txt)
        if "section_title" in item:
            item["section_title"] = clean_text(item["section_title"])
        if "topic_title" in item:
            item["topic_title"] = clean_text(item["topic_title"])
        item['text'] = txt
        cleaned.append(item)
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(cleaned, f, indent=2)
    print(f"Cleaned {len(cleaned)} items from {input_file} -> {output_file}")

if __name__ == "__main__":
    clean_data("raw_course.json", "cleaned_course.json")
    clean_data("raw_discourse.json", "cleaned_discourse.json")

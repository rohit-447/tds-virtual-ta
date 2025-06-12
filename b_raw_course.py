import os
import json
import re

def extract_title_and_url(filename):
    # Example filename: '15._Containers__Docker,_Podman.md'
    base = os.path.splitext(os.path.basename(filename))[0]
    # Remove leading numbers and underscores
    section_title = re.sub(r'^\d+[_\.]*', '', base).replace('_', ' ').replace(',', ', ')
    slug = base.lower()
    slug = re.sub(r'[\W_]+', '-', slug)
    slug = re.sub(r'-+', '-', slug).strip('-')
    url = f"https://tds.s-anand.net/#/{slug}"
    return section_title.strip(), url

course_dir = "tds_pages_md"
output = []
for fname in os.listdir(course_dir):
    if fname.endswith(".md"):
        with open(os.path.join(course_dir, fname), encoding="utf-8") as f:
            text = f.read()
        section_title, url = extract_title_and_url(fname)
        output.append({
            "text": text,
            "section_title": section_title,
            "url": url,
            "source": "course"
        })
with open("raw_course.json", "w", encoding="utf-8") as f:
    json.dump(output, f, indent=2)
print(f"Wrote {len(output)} course pages to raw_course.json")

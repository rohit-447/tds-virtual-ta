import json
import re

def canonicalize_course_url(url):
    slug = url.split('/#/')[-1]
    slug = slug.lower()
    slug = re.sub(r'[\W_]+', '-', slug)
    slug = re.sub(r'-+', '-', slug).strip('-')
    if 'docker' in slug or 'podman' in slug:
        return "https://tds.s-anand.net/#/docker"
    return f"https://tds.s-anand.net/#/{slug}"

def canonicalize_discourse_url(item):
    if "topic_slug" in item and "topic_id" in item:
        return f"https://discourse.onlinedegree.iitm.ac.in/t/{item['topic_slug']}/{item['topic_id']}"
    return item.get("url", "")

def split_text(text, chunk_size=512, chunk_overlap=64):
    sentences = re.split(r'(?<=[.!?]) +', text)
    chunks = []
    current = ""
    for sent in sentences:
        if len(current) + len(sent) <= chunk_size:
            current += " " + sent
        else:
            chunks.append(current.strip())
            overlap = current[-chunk_overlap:] if chunk_overlap < len(current) else current
            current = overlap + " " + sent
    if current.strip():
        chunks.append(current.strip())
    return chunks

def chunk_data(input_file, output_file, is_course=False, is_discourse=False, chunk_size=512, chunk_overlap=64):
    with open(input_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    all_chunks = []
    for item in data:
        chunks = split_text(item["text"], chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        for chunk in chunks:
            chunk_data = {
                "text": chunk,
                "source": item["source"]
            }
            if is_course:
                chunk_data["url"] = canonicalize_course_url(item["url"])
            elif is_discourse:
                chunk_data["url"] = canonicalize_discourse_url(item)
            else:
                chunk_data["url"] = item.get("url", "")
            if "section_title" in item:
                chunk_data["section_title"] = item["section_title"]
            if "topic_title" in item:
                chunk_data["topic_title"] = item["topic_title"]
            all_chunks.append(chunk_data)
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(all_chunks, f, indent=2)

if __name__ == "__main__":
    chunk_data("cleaned_course.json", "chunked_course.json", is_course=True)
    chunk_data("cleaned_discourse.json", "chunked_discourse.json", is_discourse=True)
    with open("chunked_course.json", "r", encoding="utf-8") as f:
        course = json.load(f)
    with open("chunked_discourse.json", "r", encoding="utf-8") as f:
        discourse = json.load(f)
    all_chunks = course + discourse
    with open("all_chunks.json", "w", encoding="utf-8") as f:
        json.dump(all_chunks, f, indent=2)

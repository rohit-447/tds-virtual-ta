import os
import json

input_dir = "TDS-Project1-Data-main/TDS-Project1-Data-main/discourse_json"
output_file = "discourse_posts.json"

all_threads = []
for fname in os.listdir(input_dir):
    if fname.endswith(".json"):
        with open(os.path.join(input_dir, fname), encoding="utf-8") as f:
            thread = json.load(f)
        all_threads.append(thread)

with open(output_file, "w", encoding="utf-8") as f:
    json.dump(all_threads, f, indent=2)

print(f"Combined {len(all_threads)} threads into {output_file}")

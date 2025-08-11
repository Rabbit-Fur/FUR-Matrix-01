import os, json

def autofill_missing_keys(master_lang='en'):
    base = f"translations/{master_lang}.json"
    with open(base, "r", encoding="utf-8") as f:
        master_keys = set(json.load(f).keys())
    for lang_file in os.listdir("translations"):
        if lang_file.endswith(".json") and not lang_file.startswith(master_lang):
            path = f"translations/{lang_file}"
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            missing = master_keys - data.keys()
            for key in missing:
                data[key] = f"[{key}]"
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
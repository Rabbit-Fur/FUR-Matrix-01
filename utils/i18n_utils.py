import os

def get_supported_languages():
    path = os.path.join(os.path.dirname(__file__), "../translations")
    langs = [f[:-5] for f in os.listdir(path) if f.endswith(".json")]
    return langs
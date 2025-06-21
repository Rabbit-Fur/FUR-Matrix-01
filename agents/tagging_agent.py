"""
TaggingAgent – generiert automatische Hashtags, Meta-Tags und PvP-Kategorien
"""


class TaggingAgent:
    def __init__(self):
        self.tags = []

    def generate_tags(self, text):
        base = text.lower()
        self.tags = [f"#{w}" for w in base.split() if len(w) > 3]
        return self.tags

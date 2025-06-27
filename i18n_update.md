# ❓ TASK: Kannst du das i18n-System überarbeiten, sodass nur Sprachen mit vorhandenen Übersetzungsdateien im Dropdown erscheinen und dabei die passenden Flaggen angezeigt werden?

## Hintergrund:
- Unser System verwendet Flask, Jinja2 und `flask_babel_next` für die Internationalisierung.
- Die Übersetzungen liegen in `/translations/{lang}.json` vor.
- Flaggen sind vollständig vorhanden unter `/static/flags/{lang}.png` (ISO-3166-1 alpha-2).
- Aktuell wird im Dropdown **jede Flagge angezeigt**, obwohl es für viele Sprachen **gar keine Übersetzungsdatei** gibt.

---

## Ziel:

1. **Nur Sprachen anzeigen**, für die auch eine gültige JSON-Übersetzung existiert.
2. Die dazugehörige **Flagge** soll jeweils neben dem Sprachkürzel im Dropdown angezeigt werden.
3. Die Dropdown-Auswahl soll bei Änderung die Flagge **dynamisch aktualisieren**.
4. Wenn kein Sprachwert in der Session gesetzt ist, soll `request.accept_languages` genutzt werden.
5. Fehlende Übersetzungen sollen immer auf **Englisch zurückfallen**.
6. Optional: Logge eine Warnung, wenn für eine vorhandene Flagge keine Übersetzung existiert (z. B. `Warnung: Flagge 'br.png' gefunden, aber keine br.json`).

---

## Technische Anforderungen:

### 🔍 Backend (Python)

- Scanne `/translations/` zur Laufzeit und extrahiere alle `.json`-Dateien:
```python
import os

TRANSLATIONS_PATH = os.path.join(os.path.dirname(__file__), "../translations")

def get_supported_languages():
    return [
        f[:-5] for f in os.listdir(TRANSLATIONS_PATH)
        if f.endswith(".json")
    ]
Verwende diese Liste im Jinja2-Dropdown und für die Sprachlogik.

Implementiere oder überarbeite current_lang() und t(key) mit sauberem Fallback auf en.

🌐 Frontend (Jinja2 + JavaScript)
html
Kopieren
Bearbeiten
<select id="language-select" onchange="changeLanguage(this.value)">
  {% for lang in get_supported_languages() %}
    <option value="{{ lang }}" {% if current_lang() == lang %}selected{% endif %}>
      {{ lang.upper() }}
    </option>
  {% endfor %}
</select>

<img id="flag-icon" src="/static/flags/{{ current_lang() }}.png" alt="Flagge" width="24" />

<script>
  function changeLanguage(langCode) {
    fetch(`/set_language?lang=${langCode}`).then(() => location.reload());
  }

  document.getElementById('language-select').addEventListener('change', function () {
    document.getElementById('flag-icon').src = `/static/flags/${this.value}.png`;
  });
</script>
🔄 Zusatzroute:
python
Kopieren
Bearbeiten
@app.route("/set_language")
def set_language():
    lang = request.args.get("lang")
    if lang in get_supported_languages():
        session["lang"] = lang
    return "", 204
Ergebnis:
Das Dropdown zeigt nur gültige Sprachen.

Flaggen erscheinen korrekt im Menü.

Fehlende JSON-Dateien blockieren die Sprache im Dropdown.

Fallback-Sprache ist Englisch.

Das System bleibt dynamisch und wartbar.


## 2025-06-27 Update
- Ran extract_i18n_keys.py to rebuild translation_keys.json.
- Compared keys with en.json and de.json.
- Added 75 missing entries with English translations and German defaults.


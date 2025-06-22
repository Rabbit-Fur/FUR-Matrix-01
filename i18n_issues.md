# 🔧 TASK: Fix i18n rendering and re-enable flag-based language selection

## Current Issues:

1. The website currently renders raw translation keys like `welcome_message`, `portal_intro`, `login_with_discord` instead of localized strings.
2. The language selector dropdown (`<select>`) shows only language codes (e.g., EN, DE, VI), but no country flags.
3. Although the directory `/static/flags/` contains all `*.png` flag images (named by ISO codes like `de.png`, `vi.png`), they are not used in the UI.

## Requirements:

- Fix the i18n system to load `translations/{lang}.json` and apply them correctly via `t("...")`.
- Ensure `current_lang()` or request-based detection works.
- Render all `t()` keys correctly (with fallback to "en" if translation is missing).
- Enhance the language selector to show flags, e.g.:

```html
<option value="de">
  <img src="/static/flags/de.png" style="width: 18px;"> Deutsch
</option>
Or use an alternative like select2 to support images inside dropdowns.

Resources available:
/translations/*.json

/static/flags/*.png (full flagset)

Language codes: ISO 3166 alpha-2

Example Bug Context:
URL: https://fur-martix.up.railway.app/

Current dropdown shows: EN, DE, VI, etc.

Rendered keys instead of translations appear throughout the dashboard and public pages.

yaml
Kopieren
Bearbeiten

---

## ✅ **2. Alternativ: Technische Dokumentation in Git oder Markdown**

Wenn du Codex in ein Build-Script oder Repository integrierst, kannst du stattdessen eine Markdown-Datei wie `i18n_issues.md` mit folgendem Inhalt speichern:

```markdown
# Multilang Bug Report

## Problem
- Translations not applied (`t("key")` is shown literally)
- Language dropdown has no flags
- JSON files exist but are not rendered

## Flags available
Location: `/static/flags/*.png`

## Desired Behavior
- Render correct translations based on selected language
- Show flag images beside each language option

## Optional
- Fallback to English if a key is missing

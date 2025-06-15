# 🔧 Merge-Helfer für FUR Codex

Dieser Helfer unterstützt dich beim Auflösen der aktuellen Git-Rebase-Konflikte.

## 🧠 Option A – Konflikte lösen & Rebase abschließen

1. Öffne alle Dateien mit `<<<<<<<`, `=======`, `>>>>>>>`
2. Entscheide dich für die gewünschte Version oder kombiniere sie manuell
3. Danach im Projektverzeichnis ausführen:

```bash
bash merge_helper.sh
```

## 🛑 Option B – Rebase abbrechen

Wenn du abbrechen möchtest:

```bash
bash abort_merge.sh
```

## ⚠️ Hinweis

Wenn du stattdessen deine lokale Version durchsetzen willst (mit Risiko):

```bash
git push origin main --force
```

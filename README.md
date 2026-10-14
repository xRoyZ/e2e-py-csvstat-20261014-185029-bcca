# csvstat

`csvstat` ist ein kleines, pragmatisches Kommandozeilenwerkzeug in Python, das
eine CSV-Datei mit Kopfzeile einliest und pro Spalte Statistiken ausgibt: für
jede numerische Spalte Anzahl, Minimum, Maximum, Mittelwert und Anzahl
fehlender Werte, für jede Textspalte die Anzahl der eindeutigen Werte. Die
Steuerung erfolgt über `argparse` mit den Optionen `--delimiter`, `--columns`
und `--json`. Fehlende, unlesbare oder leere Dateien werden mit einer klaren
einzeiligen Meldung auf stderr und dem Exit-Code 2 abgefangen — nie mit einem
Traceback.

> Hinweis: Dieses Repository enthält aktuell das lauffähige CLI-Gerüst. Das
> eigentliche Einlesen der CSV-Datei, die Statistikberechnung und die
> Text-/JSON-Ausgabe sind als Module mit den vereinbarten Signaturen angelegt
> und werden von den Folgetickets dieser Sprint-Planung implementiert.

## Tech-Stack

- **Sprache**: Python 3.9+
- **Laufzeit-Abhängigkeiten**: ausschließlich die Standardbibliothek
  (`argparse`, `csv`, `json`, `os`, `pathlib`)
- **Tests**: pytest (nur Entwicklungsabhängigkeit)
- **Paketierung**: `pyproject.toml` mit dem Konsolen-Einstiegspunkt `csvstat`

## Installation

```bash
pip install -e .
```

Für die Entwicklung mit Tests zusätzlich die Dev-Abhängigkeit installieren:

```bash
pip install -e ".[dev]"
```

## Ausführen (Entwicklung)

Nach der Installation steht der Konsolen-Befehl `csvstat` bereit:

```bash
csvstat --help
```

Alternativ lässt sich das Paket direkt als Modul starten:

```bash
python -m csvstat --help
```

Es gibt keinen Build-Schritt: das Werkzeug läuft direkt aus dem Quellcode bzw.
aus der installierten Konsolen-Skript-Datei.

## Verwendung

```
csvstat <file> [--delimiter CHAR] [--columns NAME[,NAME...]] [--json]
```

- `<file>` — Pfad zur CSV-Datei mit Kopfzeile.
- `--delimiter CHAR` — Trennzeichen; standardmäßig `,`. Die
  Zwei-Zeichen-Sequenz `\t` wird als Tabulator interpretiert:
  `csvstat --delimiter '\t' data.tsv`.
- `--columns NAME[,NAME...]` — Beschränkt die Ausgabe auf die genannten
  Spalten in der angegebenen Reihenfolge. Ein unbekannter Spaltenname führt zu
  einer Meldung auf stderr und Exit-Code 2.
- `--json` — Gibt den Bericht als genau ein JSON-Objekt auf stdout aus
  (statt der Textausgabe).

Beispiele:

```bash
csvstat data.csv
csvstat --delimiter ';' data.csv
csvstat --columns name,age data.csv
csvstat --json data.csv
```

### Exit-Codes

| Code | Bedeutung |
| ---- | --------- |
| `0`  | Erfolg — das Ergebnis steht auf stdout |
| `2`  | Jeder Fehler: Argumentfehler, fehlender/ungültiger/unlesbarer Pfad, leere Datei, reine Kopfzeilen-Datei, unbekannte Spalte u. a. |

Bei jedem Fehler erscheint genau eine Zeile auf stderr mit dem Präfix
`csvstat: `; stdout bleibt in diesem Fall leer.

## Tests

```bash
pytest
```

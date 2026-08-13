# PM-ZERT Prüfungssimulator

Eine inoffizielle, schlanke Übungsplattform für das **GPM Basiszertifikat im
Projektmanagement (PM-ZERT)**. Nachgebaut nach der UI-Beschreibung im
"Anleitung zur Nutzung des Zertifizierungsportals" (Kap. 6, S. 19–24) und
befüllt mit den Fragen/Antworten aus der bereitgestellten Tabelle.

**Die gesamte App ist eine einzige Datei: [`index.html`](index.html).**
Kein Server, kein Build-Schritt, keine Abhängigkeiten — alle 1035 Fragen sind
direkt eingebettet.

## Lokal öffnen

Einfach `index.html` doppelklicken, oder:

```bash
python -m http.server 8000
```

und dann `http://localhost:8000` aufrufen.

## Hosten (jede Option reicht — eine Datei genügt)

- **GitHub Pages**: `index.html` in ein Repo pushen, Pages auf den Branch zeigen lassen.
- **Netlify Drop**: [app.netlify.com/drop](https://app.netlify.com/drop) — den Projektordner reinziehen, fertig.
- **Cloudflare Pages / Vercel**: Repo verbinden, kein Build-Command nötig (Output-Verzeichnis = `/`).
- **Beliebiger Webspace**: `index.html` per FTP hochladen.

## Funktionsumfang

Nachgebildet aus der Anleitung (Kap. 6.2–6.9):

- Timer mit konfigurierbarer Bearbeitungszeit (Standard: 90 Min. lt. Prüfungsordnung)
- Linke Übersichtsspalte mit nummerierten Kreisen, gruppiert nach den drei
  ICB4-Kompetenzbereichen (Kontext / Persönliches und Soziales / Methoden und
  Technisches), Farbcodierung (grün = beantwortet, grau = offen, hellblau =
  Lesezeichen, dunkelblau = aktuelle Frage)
- Navigation per Pfeiltasten in der Kopfzeile oder durch Klick auf die Kreise
- Lesezeichen setzen/entfernen
- Freitext-Antwortfeld mit einfacher Rich-Text-Toolbar (fett/kursiv/unterstrichen/Listen)
  sowie Multiple-Choice-Fragen mit auswählbaren Antwortoptionen
- Abschlussansicht mit Bestätigungsdialog ("kann nicht fortgesetzt werden")
- Auswertung nach der echten Bestehensregel der Prüfungsordnung: **11 von 14
  Kompetenzelementen müssen auf dem geforderten Niveau (≥ 50 % der Fragen
  richtig) nachgewiesen werden.** Multiple-Choice wird automatisch ausgewertet;
  offene Fragen werden im Review mit Musterantwort angezeigt und lassen sich
  selbst als richtig/falsch markieren — optional auch per KI (siehe unten).

## KI-Bewertung offener Fragen (optional)

Freitext-Antworten lassen sich nicht automatisch exakt abgleichen. Wer im
Konfigurator einen kostenlosen **Google Gemini API-Key** hinterlegt (erstellbar
auf [aistudio.google.com/api-keys](https://aistudio.google.com/api-keys), kein
Zahlungsmittel nötig), bekommt im Review-Modus zusätzlich einen "✨ Mit KI
bewerten"-Button pro offener Frage sowie einen Sammel-Button für alle offenen
Fragen auf einmal. Die KI vergleicht Antwort und Musterantwort inhaltlich,
liefert eine kurze Begründung und setzt automatisch richtig/falsch — das
fließt direkt in die Kompetenzelement-Auswertung ein.

Technisch bleibt die App dabei ein reines Static File: Der Key wird nur lokal
im Browser (`localStorage`) gespeichert und der Request geht direkt vom
Browser an `generativelanguage.googleapis.com` — es gibt keinen Server, der
den Key oder die Antworten sieht. Ohne Key funktioniert alles wie zuvor rein
manuell.

## Konfigurator (Startseite)

- Fragen je Kompetenzelement (Standard: 2)
- Bearbeitungszeit in Minuten
- Auswahl, welche der 14 offiziellen Kompetenzelemente (+ "Sonstige"-Zusatzfragen)
  einbezogen werden

**Hinweis zur Fragenanzahl:** PM-ZERT veröffentlicht keine genaue Gesamtzahl an
Prüfungsfragen. Offiziell dokumentiert sind nur: 90 Minuten Bearbeitungszeit,
14 Kompetenzelemente, 11 davon müssen bestanden werden. Mehrere unabhängige
Quellen beschreiben übereinstimmend eine "etwa gleich große" Mischung aus
Multiple-Choice- und offenen Fragen — die Fragenauswahl je Kompetenzelement
zieht daher standardmäßig zu gleichen Teilen aus beiden Typen.

## Daten aktualisieren

Der Fragenpool steht in [`data/questions.csv`](data/questions.csv) (Export der
bereitgestellten Tabelle). Nach Änderungen an der CSV:

```bash
python tools/build.py
```

baut `index.html` neu (liest `tools/template.html` + `data/questions.csv`,
schreibt die fertige Single-File-App).

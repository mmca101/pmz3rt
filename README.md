# SÍM-C3RT Prüfungssimulator

Eine inoffizielle, schlanke Übungsplattform für das **GPM Basiszertifikat im
Projektmanagement**. Nachgebaut nach der UI-Beschreibung im "Anleitung zur
Nutzung des Zertifizierungsportals" (Kap. 6, S. 19–24).

**Die gesamte App ist eine einzige Datei: [`index.html`](index.html).**
Kein Build-Schritt, keine Abhängigkeiten. Der Fragenpool wird bei jedem
Seitenaufruf live aus einem konfigurierbaren Google Sheet geladen (Standard-
URL ist im Konfigurator hinterlegt) — es gibt keine im Repo gespeicherte
Kopie der Fragen mehr.

## Lokal öffnen

Einfach `index.html` doppelklicken, oder:

```bash
python -m http.server 8000
```

und dann `http://localhost:8000` aufrufen. Da die Fragen live per `fetch()`
geladen werden, ist eine Internetverbindung nötig; die App funktioniert nicht
mehr offline.

## Hosten (jede Option reicht — eine Datei genügt)

- **GitHub Pages**: `index.html` in ein Repo pushen, Pages auf den Branch zeigen lassen.
- **Netlify Drop**: [app.netlify.com/drop](https://app.netlify.com/drop) — den Projektordner reinziehen, fertig.
- **Cloudflare Pages / Vercel**: Repo verbinden, kein Build-Command nötig (Output-Verzeichnis = `/`).
- **Beliebiger Webspace**: `index.html` per FTP hochladen.

## Fragenquelle

Im Konfigurator (unterste Karte "Fragenquelle") lässt sich die Google-Sheet-URL
einsehen und ändern. Es wird immer nur das **erste Tabellenblatt** (`gid=0`)
gelesen. Erwartete Spalten: `Kompetenzelement`, `Frage`, `Antwortmöglichkeit`,
`Ergänzende Informationen`.

Das Sheet muss auf **"Jeder mit dem Link kann ansehen"** freigegeben sein,
sonst schlägt das Laden fehl (Fehlermeldung erscheint direkt im Konfigurator,
mit "Fragen neu laden"-Button zum Wiederholen).

Multiple-Choice-Fragen werden anhand von Antwortmarkierungen im Fragetext
erkannt — unterstützt werden `A)`, `a)`, `A.`, `1)` und `1.` (beliebig
gemischt, wird intern auf A–F normalisiert). Alles andere gilt als offene
Frage.

## Funktionsumfang

Nachgebildet aus der Anleitung (Kap. 6.2–6.9):

- Timer mit konfigurierbarer Bearbeitungszeit (Standard: 90 Min. lt. Prüfungsordnung)
- Linke Übersichtsspalte mit nummerierten Kreisen, gruppiert nach den drei
  ICB4-Kompetenzbereichen (Kontext / Persönliches und Soziales / Methoden und
  Technisches), Farbcodierung (grün = beantwortet, grau = nie geöffnet, lila =
  geöffnet aber nicht beantwortet, gelb = Lesezeichen, dunkelblau = aktuelle Frage)
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
  Unbeantwortete Fragen (egal ob Multiple-Choice oder offen) zählen sofort als
  falsch, ohne dass eine Bewertung nötig ist.

## KI-Bewertung offener Fragen (optional)

Freitext-Antworten lassen sich nicht automatisch exakt abgleichen. Wer im
Konfigurator einen kostenlosen **Google Gemini API-Key** hinterlegt (erstellbar
auf [aistudio.google.com/api-keys](https://aistudio.google.com/api-keys), kein
Zahlungsmittel nötig, über "Speichern & testen" wird der Key sofort geprüft),
bekommt im Review-Modus automatisch nach Prüfungsende sowie zusätzlich per
"✨ Mit KI bewerten"-Button pro offener Frage eine KI-Einschätzung. Die KI
vergleicht Antwort und Musterantwort inhaltlich, liefert eine kurze Begründung
und setzt automatisch richtig/falsch — das fließt direkt in die
Kompetenzelement-Auswertung ein.

Technisch bleibt die App dabei ein reines Static File: Der Key wird nur lokal
im Browser (`localStorage`) gespeichert und der Request geht direkt vom
Browser an `generativelanguage.googleapis.com` — es gibt keinen Server, der
den Key oder die Antworten sieht. Eine Content-Security-Policy beschränkt
Netzwerkzugriffe der Seite auf sich selbst, Google Sheets und die Gemini-API,
sodass ein gespeicherter Key selbst bei einem hypothetischen künftigen
XSS-Bug nicht an Dritte gesendet werden könnte. Ohne Key funktioniert alles
wie zuvor rein manuell.

## Konfigurator (Startseite)

- Fragen gesamt (Standard: 61 — lt. Kursleitung die tatsächliche Anzahl in
  der echten Prüfung; wird per Round-Robin gleichmäßig auf die ausgewählten
  Kompetenzelemente verteilt)
- Bearbeitungszeit in Minuten
- Auswahl, welche der 14 offiziellen Kompetenzelemente (+ "Sonstige"-Zusatzfragen)
  einbezogen werden, inkl. Schnellfilter je ICB4-Kompetenzbereich
- "Fokus-Typ"-Regler (reine Übungsfunktion): Anteil Multiple-Choice vs.
  Freitext, Standard ≈19 % (laut Kursleitung üblicherweise 11–12 von 61
  Fragen Multiple-Choice)
- "Multiple/Single-Choice-Fragen zuerst" (Standard: an): bündelt alle
  Multiple-/Single-Choice-Fragen an den Anfang der Prüfung, wie im echten
  Portal; abwählen mischt beide Fragetypen zufällig für abwechslungsreicheres Üben

**Hinweis zur Fragenanzahl:** Die Zertifizierungsstelle veröffentlicht selbst
keine genaue Gesamtzahl an Prüfungsfragen. Offiziell dokumentiert sind nur: 90
Minuten Bearbeitungszeit, 14 Kompetenzelemente, 11 davon müssen bestanden
werden. Die Angaben zu 61 Fragen und ~11–12 Multiple-Choice-Fragen stammen von
der Kursleitung, nicht von der Zertifizierungsstelle selbst.

# SiM-C3RT Prüfungssimulator

Eine inoffizielle, schlanke Übungsplattform für das **GPM Basiszertifikat im
Projektmanagement**. Nachgebaut nach der UI-Beschreibung im "Anleitung zur
Nutzung des Zertifizierungsportals" (Kap. 6, S. 19–24).

**Die gesamte App ist im Kern eine einzige Datei: [`index.html`](index.html).**
Kein Build-Schritt, keine Abhängigkeiten. Der Fragenpool wird bei jedem
Seitenaufruf live aus einem konfigurierbaren Google Sheet geladen — es gibt
keine im Repo gespeicherte Kopie der Fragen und auch keine im Code
hinterlegte Standard-Quelle mehr; die Sheet-URL wird manuell eingetragen
oder per Link mitgegeben (siehe [Fragenquelle](#fragenquelle) unten).
[`404.html`](404.html) ist eine reine Kopie von `index.html` und existiert
ausschließlich, damit GitHub Pages auch Deep-Links mit einer eingebetteten
Sheet-URL im Pfad ausliefert (siehe unten) — es ist keine eigenständige Seite.
Für die Installierbarkeit als PWA (siehe [unten](#installierbar-pwa)) kommen
vier kleine Begleitdateien dazu (`manifest.webmanifest`, `sw.js`,
`icon-192.png`, `icon-512.png`) — die eigentliche Anwendungslogik bleibt
vollständig in `index.html`.

## Lokal öffnen

Einfach `index.html` doppelklicken, oder:

```bash
python -m http.server 8000
```

und dann `http://localhost:8000` aufrufen. Die Fragen werden live per
`fetch()` aus dem Google Sheet geladen, dafür ist beim ersten Laden eine
Internetverbindung nötig. Der Service Worker cached danach nur die
App-Hülle (siehe [Installierbar (PWA)](#installierbar-pwa)) — ein bereits
geladener Fragenkatalog bleibt offline nutzbar, ein neuer oder aktualisierter
Katalog braucht weiterhin eine Verbindung.

## Hosten (jede Option reicht)

- **GitHub Pages**: Repo pushen, Pages auf den Branch zeigen lassen.
- **Netlify Drop**: [app.netlify.com/drop](https://app.netlify.com/drop) — den Projektordner reinziehen, fertig.
- **Cloudflare Pages / Vercel**: Repo verbinden, kein Build-Command nötig (Output-Verzeichnis = `/`).
- **Beliebiger Webspace**: alle Dateien im Projektordner per FTP hochladen.

## Installierbar (PWA)

Die App lässt sich über den Browser als eigenständige App installieren
("Zum Startbildschirm hinzufügen" / Install-Icon in der Adressleiste) —
`manifest.webmanifest` liefert Name, Icons und Theme-Farbe, `sw.js` ist ein
minimaler Service Worker, der ausschließlich die App-Hülle selbst
(`index.html`, Manifest, Icons) cached. Die Sheet-Abfrage und alle
Gemini-Aufrufe laufen weiterhin immer live — der Service Worker greift nur
bei GET-Requests auf die eigene Domain ein, nie bei Cross-Origin-Requests.

Da eine installierte App immer auf der festen `start_url` (`/`, ohne
`?sheet=`) startet, merkt sich die App zusätzlich die zuletzt erfolgreich
geladene Sheet-URL in `localStorage` (`simc3rt_last_sheet`) und lädt sie
automatisch nach, wenn kein `?sheet=`-Parameter in der Adresse steht — das
gilt genauso für einen normalen Browser-Aufruf der nackten Domain.

## Fragenquelle

Im Konfigurator (Karte "Fragenquelle") lässt sich die Google-Sheet-URL
eintragen. Es wird immer nur das **erste Tabellenblatt** (`gid=0`) gelesen.
Erwartete Spalten: `Kompetenzelement`, `Frage`, `Antwortmöglichkeit`,
`Ergänzende Informationen`. Optional zusätzlich eine Spalte `ID` (Kopfzeile
`ID`, `Frage-ID` oder `Fragen-ID`, Position egal) mit einer je Frage
eindeutigen, über Sheet-Bearbeitungen hinweg stabilen Kennung — erst damit
lässt sich das [Lerngedächtnis](#lerngedächtnis--fortschrittsanzeige) nutzen.
Fehlt die Spalte oder ist eine ID leer/doppelt, fällt die App sheet-weit auf
eine reine Zeilenposition als Kennung zurück und das Lerngedächtnis bleibt
deaktiviert, statt mit einer instabilen ID falsche Ergebnisse zu speichern.
Es gibt keine im Code hinterlegte Standard-URL —
ohne eingetragene oder per Link mitgegebene Sheet-URL zeigt der Konfigurator
"Keine Quelle gefunden" und die Prüfung lässt sich nicht starten.

Das Sheet muss auf **"Jeder mit dem Link kann ansehen"** freigegeben sein,
sonst schlägt das Laden fehl (Fehlermeldung erscheint direkt im Konfigurator,
mit "Fragen neu laden"-Button zum Wiederholen).

Checkbox-Fragen (Multiple/Single-Choice) werden anhand von Antwortmarkierungen
im Fragetext erkannt — unterstützt werden `A)`, `a)`, `A.`, `1)` und `1.`
(beliebig gemischt, wird intern auf A–F normalisiert). Alles andere gilt als
offene Frage.

### Fragenquelle per Link mitgeben

Die Sheet-URL (oder nur deren ID) lässt sich direkt in den Seitenlink
einbetten, damit die App sofort mit dieser Quelle startet, ohne manuelles
Eintragen:

```
https://<domain>/?sheet=<Sheet-ID>
https://<domain>/?sheet=<Google-Sheet-URL>
https://<domain>/<Google-Sheet-URL>
```

Alle drei Formen sind gleichwertig — der Rest der Google-Sheet-URL ist
ohnehin immer derselbe, daher genügt die reine Sheet-ID nach `?sheet=`; die
Konfigurator-Karte "Fragenquelle" normalisiert eine eingetragene volle URL
beim Laden automatisch auf die kurze ID-Form in der Adresszeile. Es gibt
keine im Repo gespeicherte Beispiel- oder Standard-Sheet-URL. Die dritte Form
(URL direkt nach der Domain, ohne `?sheet=`) funktioniert nur dank
[`404.html`](404.html): GitHub Pages ist ein reiner Static-File-Host ohne
serverseitiges Routing, liefert aber für jeden nicht existierenden Pfad
automatisch `404.html` aus (Standard-Trick für Client-seitiges Routing auf
statischen Hosts) — und die ist eine 1:1-Kopie von `index.html`, sodass die
App auch dann lädt und die eingebettete URL aus `location.pathname` auslesen
kann.

## Funktionsumfang

Nachgebildet aus der Anleitung (Kap. 6.2–6.9):

- Timer mit konfigurierbarer Bearbeitungszeit (Standard: 90 Min. lt. Prüfungsordnung)
- Linke Übersichtsspalte mit nummerierten Kreisen, gruppiert nach den drei
  ICB4-Kompetenzbereichen (Kontext / Persönliches und Soziales / Methoden und
  Technisches), Farbcodierung (grün = beantwortet, grau = nie geöffnet, lila =
  geöffnet aber nicht beantwortet, gelb = Lesezeichen, dunkelblau = aktuelle Frage)
- Navigation per Pfeiltasten in der Kopfzeile oder durch Klick auf die Kreise
- Lesezeichen setzen/entfernen
- Fragen vorlesen lassen (Play/Pause + Geschwindigkeit, unten rechts als
  Overlay): nutzt die im Browser eingebaute Web-Speech-API — kein API-Key,
  keine Internetverbindung nötig, funktioniert offline
- Freitext-Antwortfeld mit einfacher Rich-Text-Toolbar (fett/kursiv/unterstrichen/Listen)
  sowie Checkbox-Fragen (Multiple/Single-Choice) mit auswählbaren Antwortoptionen
- Abschlussansicht mit Bestätigungsdialog ("kann nicht fortgesetzt werden")
- Auswertung nach der echten Bestehensregel der Prüfungsordnung: **11 von 14
  Kompetenzelementen müssen auf dem geforderten Niveau (≥ 50 % der Fragen
  richtig) nachgewiesen werden.** Checkbox-Fragen werden automatisch
  ausgewertet; offene Fragen werden im Review mit Musterantwort angezeigt und
  lassen sich selbst als richtig/falsch markieren — optional auch per KI
  (siehe unten). Musterantwort, Zusatzinfo und KI-Einschätzung werden dabei
  als einfaches Markdown gerendert (fett, Listen, Überschriften), statt
  rohen Text mit sichtbaren `**`/`-`/`#`-Zeichen anzuzeigen. Ist ein
  Gemini-Key hinterlegt, wird die Musterantwort beim ersten Aufklappen einer
  Frage zusätzlich einmalig per KI in besser lesbares Markdown umformatiert
  (Inhalt bleibt unverändert, nur Struktur/Formatierung) — das Ergebnis wird
  lokal im Browser zwischengespeichert (`localStorage`, geschlüsselt über den
  Quelltext selbst), sodass dieselbe Frage nicht erneut angefragt wird,
  solange sich ihr Text im Sheet nicht ändert. Unbeantwortete Fragen (egal ob
  Checkbox oder offen) zählen sofort als falsch, ohne dass eine Bewertung
  nötig ist.
- Ergebnisse als CSV exportierbar (Kompetenzelement, Frage, eigene Antwort,
  Musterantwort, Zusatzinfo, Bewertung, KI-Begründung)
- Übungs-Modus (Cheat-Modus, optional, Standard: aus): zeigt Musterantwort
  bzw. richtige Antwort direkt auf jeder Fragenseite während der Prüfung
  statt erst im Review — inkl. Vorlese-Button für die Musterantwort (gleiche
  Web-Speech-API wie beim Vorlesen der Frage) und optionaler KI-Bewertung
  direkt vor Ort, sobald ein Gemini-Key hinterlegt ist

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

Sind Haupt- und Fallback-Modell gleichzeitig überlastet/limitiert (beide
Google-eigene Retries bereits ausgeschöpft), steht im Übungs-Modus zusätzlich
zum "Erneut versuchen"-Button auch die manuelle Selbsteinschätzung zur
Verfügung, statt die Frage bis zum nächsten Kontingent-Reset unbewertbar zu
lassen.

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
- "Checkboxfragenanteil"-Regler (reine Übungsfunktion): Anteil Checkbox- vs.
  Freitext-Fragen, Standard ≈19 % (laut Kursleitung üblicherweise 11–12 von
  61 Fragen Checkbox-Fragen)
- "Checkbox-Fragen zuerst" (Standard: an): bündelt alle Checkbox-Fragen an
  den Anfang der gesamten Prüfung (über alle Kompetenzbereiche hinweg), wie
  im echten Portal; abwählen mischt beide Fragetypen zufällig je
  Kompetenzbereich für abwechslungsreicheres Üben — die linke Übersichtsspalte
  spiegelt das: mit aktiver Bündelung erscheint "Checkboxfragen" als eigene
  Gruppe vor den vier Kompetenzbereichs-Gruppen, sonst sind beide Fragetypen
  innerhalb der Kompetenzbereiche gemischt

**Hinweis zur Fragenanzahl:** Die Zertifizierungsstelle veröffentlicht selbst
keine genaue Gesamtzahl an Prüfungsfragen. Offiziell dokumentiert sind nur: 90
Minuten Bearbeitungszeit, 14 Kompetenzelemente, 11 davon müssen bestanden
werden. Die Angaben zu 61 Fragen und ~11–12 Checkbox-Fragen stammen von der
Kursleitung, nicht von der Zertifizierungsstelle selbst.

## Lerngedächtnis & Fortschrittsanzeige

Enthält das geladene Sheet eine gültige `ID`-Spalte (siehe
[Fragenquelle](#fragenquelle)), merkt sich die App geräteübergreifend in
`localStorage`, welche Fragen bereits gesehen, beantwortet und richtig oder
falsch gelöst wurden — über beliebig viele Übungsdurchläufe hinweg, nicht
nur innerhalb einer Prüfung. Steuerbar über die Checkbox "Lerngedächtnis und
Fortschritttracking" in der Konfigurator-Karte "Fragenkatalogquelle"
(Standard: an, sobald eine gültige ID-Spalte erkannt wird; ohne gültige IDs
bleibt die Checkbox deaktiviert).

Ist das Lerngedächtnis aktiv, priorisiert die Fragenauswahl gezielt: nie
gelernte Fragen zuerst, dann zuletzt falsch beantwortete, dann gesehene aber
übersprungene, dann noch nie gesehene als Auffüller — bereits gemeisterte
Fragen (siehe unten) haben die niedrigste Priorität. So wiederholt sich der
Fragenpool bei regelmäßigem Üben nicht ständig selbst, sondern konzentriert
sich zunehmend auf tatsächliche Wissenslücken.

Ein Fortschrittsbalken visualisiert den Lernstand über den gesamten aktuell
geladenen Fragenkatalog als Farbverlauf: **grau** = nie gesehen, **orange** =
gesehen, aber noch nicht bewertet, **rot** = zuletzt falsch beantwortet,
**grün** = einmal richtig beantwortet, **gold** (mit Glanzeffekt) = zweimal
richtig beantwortet ("gelernt" — nach dem in deutschen
Fahrschul-Lern-Apps üblichen Zwei-mal-richtig-Prinzip). Eine bereits
gemeisterte Frage wird bei einer erneut falschen Antwort nur um eine Stufe
zurückgestuft (gold → grün → rot), nicht komplett zurückgesetzt. Eine
aufklappbare Legende unter dem Balken zeigt die genauen Anteile in Prozent.

Der Balken erscheint standardmäßig kompakt direkt in der Konfigurator-Karte
"Fragenkatalogquelle" sowie am Ende jeder Prüfung auf der Ergebnisseite. Über
die zusätzliche Checkbox "Fortschritt auf Startseite anzeigen" (ebenfalls
Standard: an) lässt er sich stattdessen prominent zwischen Konfigurator und
Fußzeile auf der Startseite anzeigen, statt in der Karte versteckt zu sein —
beide Checkboxen merken sich ihren Zustand geräteübergreifend.

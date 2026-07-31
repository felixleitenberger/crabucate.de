# App-Store-Texte

Stand: 30.07.2026 · App-Name: **Lehrer Arbeitszeit Tracker** (26 von 30 Zeichen)
Keine Lokalisierung — Primärsprache Deutsch.

---

## Was die Suche überhaupt findet

Apple indexiert für die App-Store-Suche nur:

- **App-Name**
- **Untertitel**
- **Keywords-Feld**
- Entwicklername, Namen von In-App-Käufen

**Die Beschreibung wird nicht indexiert.** Sie ist reine Überzeugungsarbeit —
Schlüsselwörter dort zu stapeln bringt nichts und liest sich schlecht.

Der Name deckt bereits `Lehrer`, `Arbeitszeit` und `Tracker` ab. Diese Begriffe
tauchen deshalb bewusst weder im Untertitel noch in den Keywords auf.

---

## Untertitel (max. 30 Zeichen)

```
Zeiterfassung für Lehrkräfte
```

28 Zeichen. Bringt die beiden wertvollsten Begriffe, die im Namen fehlen:
*Zeiterfassung* (das Hauptsuchwort) und *Lehrkräfte* (eigenes Token neben „Lehrer").

---

## Keywords (max. 100 Zeichen)

```
Stundenplan,Deputat,Überstunden,Unterricht,Dienstzeit,Mehrarbeit,Referendar,Zeitkonto,Schule
```

91 Zeichen.

Regeln, die hier eingehalten sind:
- **Keine Leerzeichen** nach den Kommas — die zählen mit
- Keine Wiederholung aus Name und Untertitel
- Kein „App", keine Plural-Dubletten

`Referendar` ist eine Wette: kleine, sehr passende Zielgruppe mit wenig
Konkurrenz. Alternativen mit mehr Breite: `Grundschule`, `Gymnasium`.

---

## Werbetext (max. 170 Zeichen)

Jederzeit änderbar, ohne neue Version. Steht über der Beschreibung.

```
Trage deine Unterrichtsstunden nicht mehr von Hand nach: Die App erfasst sie automatisch aus deinem Stundenplan – Ferien und Feiertage deines Bundeslandes inklusive.
```

---

## Beschreibung (max. 4000 Zeichen)

```
Wie viel arbeitest du wirklich?

Lehrkräfte arbeiten oft deutlich mehr als vertraglich vorgesehen – abends, am Wochenende, in den Ferien. Sichtbar wird das erst, wenn man es aufschreibt.

DREI WEGE ZUR ARBEITSZEIT

Automatisch aus dem Stundenplan
Trage deinen Stundenplan einmal ein. Unterrichtsstunden und Pausenaufsichten werden an Schultagen von selbst erfasst – Ferien und Feiertage deines Bundeslandes bleiben ausgenommen.

Live mitlaufen lassen
Für Vorbereitung, Korrekturen oder eine Vertretung startest du einen Timer. Er läuft auf dem Sperrbildschirm weiter und lässt sich dort auch wieder beenden.

Nachträglich eintragen
Was du vergessen hast, ergänzt du hinterher mit Datum und Dauer.

DEINE AUSWERTUNG

• Heute, diese Woche, dieser Monat – jeweils mit Hochrechnung
• Jahresverlauf als Diagramm, Monat für Monat
• Soll- und Ist-Stunden des Schuljahres gegenübergestellt
• Verteilung nach Kategorien: Unterricht, Vorbereitung, Korrektur, Besprechungen, Verwaltung, Fortbildung

FÜR DEINE SITUATION

• Alle 16 Bundesländer mit Ferien- und Feiertagsterminen
• Teilzeit mit eigenem Deputat
• Ferientermine bis zum Schuljahr 2029/30 hinterlegt

AUF ALLEN DEINEN GERÄTEN

Einträge, Stundenplan und Einstellungen gleichen sich über iCloud zwischen iPhone und iPad ab. Startest du einen Timer auf dem einen Gerät, siehst du ihn auf dem anderen.

DEINE DATEN BLEIBEN DEINE

Kein Konto, keine Anmeldung, keine Werbung, keine Analyse-Dienste. Deine Einträge liegen auf deinem Gerät und in deiner privaten iCloud – niemand sonst hat Zugriff darauf. Außer iCloud stellt die App keine Verbindung ins Internet her: Ferien- und Feiertagstermine sind mitgeliefert.

HINWEIS ZUR BERECHNUNG

Die Soll-Arbeitszeit rechnet mit einer 40-Stunden-Woche, 30 Urlaubstagen und den gesetzlichen Feiertagen deines Bundeslandes; das Schuljahr läuft vom 1. August bis zum 31. Juli. Die Zahlen sind eine Orientierung für dich, keine dienstrechtlich verbindliche Auskunft.
```

Den letzten Absatz drinlassen: Er kostet nichts an Überzeugungskraft, dämpft aber
Erwartungen, die die App nicht einlösen kann. Dieselbe Vereinfachung steht schon
in den Einstellungen der App.

---

## Neuerungen dieser Version

```
Erste Version.
```

---

## EULA und rechtliche Pflichtangaben

**Kein EULA-Link in der Beschreibung nötig.** Die Pflicht, Nutzungsbedingungen
(EULA) in den Metadaten zu verlinken, gilt nach Richtlinie 3.1.2 nur für Apps mit
**automatisch verlängerbaren Abos**. Diese App hat keine In-App-Käufe — Apples
Standard-EULA gilt automatisch, ohne Zutun.

Pflicht ist dagegen für **jede** App, unabhängig von Käufen:

- [ ] **Datenschutzrichtlinie-URL** — Feld unter *App-Informationen*, nicht in der
      Beschreibung. Häufiger Ablehnungsgrund, wenn sie fehlt oder ins Leere führt.
- [ ] **Support-URL** — muss erreichbar sein und einen Kontaktweg bieten.

Inhaltlich muss die Datenschutzerklärung hier nur iCloud/CloudKit abdecken. Die
App stellt keine sonstigen Netzwerkverbindungen her; Ferien- und Feiertagstermine
sind mitgeliefert.

Quelle: [App Review Guidelines](https://developer.apple.com/app-store/review/guidelines/)

---

## Weitere Felder in App Store Connect

- **Kategorie:** Produktivität (primär), Bildung (sekundär)
- **Altersfreigabe:** 4+
- **App-Datenschutz:** „Es werden keine Daten erfasst" — die private
  CloudKit-Datenbank zählt nicht als Erfassung durch den Entwickler
- **Verfügbarkeit:** Erwägenswert, auf **Deutschland** zu begrenzen. Die Ferien-
  und Feiertagsdaten gelten nur für Deutschland; außerhalb wäre die App nutzlos,
  was schlechte Bewertungen einbringen kann. Jederzeit erweiterbar.
- **Review-Notes:** deutsche Lehrerarbeitszeit, kein Login nötig, keine
  Serveranbindung außer iCloud

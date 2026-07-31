# App Store Release — Checkliste

Stand: 30.07.2026 · Ziel: Version 1.0 · Plattformen: iPhone + iPad (`TARGETED_DEVICE_FAMILY = "1,2"`)

> iPad bleibt bewusst drin — ohne iPad ergibt der iCloud-Sync als Kernfeature keinen Sinn.
> Das heißt aber auch: iPad-Screenshots sind Pflicht und das iPad-Layout muss getestet sein.

---

## Bereits erledigt

Im Code/Projekt schon umgesetzt, hier nur zur Übersicht — nichts mehr zu tun:

- [x] Privacy Manifest (`PrivacyInfo.xcprivacy`) für App **und** Widget-Extension — UserDefaults / `CA92.1`
- [x] `ITSAppUsesNonExemptEncryption = NO` in der Info.plist
- [x] Plattform-Scope auf iOS begrenzt (macOS/visionOS entfernt, Widget-Target passt jetzt dazu)
- [x] `CFBundleDevelopmentRegion = de`
- [x] Doppelter `aps-environment`-Key aus den Entitlements entfernt
- [x] Kritische Bugs behoben (iCloud-Löschungen, Pausenaufsichten löschbar, vergessener Timer)
- [x] Ferien- und Feiertags-APIs entfernt — Feiertage berechnet, Schulferien mitgeliefert
- [x] Laufender Timer und Einstellungen von `NSUbiquitousKeyValueStore` auf CloudKit umgestellt
- [x] Zwei-Geräte-Sync durchgetestet: Einträge, Timer, Stundenplan, Zurücksetzen
- [x] Stopp-Knopf der Live Activity — lag daran, dass ein `LiveActivityIntent` im
      App-Target liegen muss, nicht nur in der Extension
- [x] Build ohne Warnungen, 81/81 Unit-Tests grün

---

## Phase 0 — Sofort

- [ ] Änderungen committen (Branch `fix/projekt-review`) — vorher `git diff` überfliegen
- [ ] Einmal auf **echtem Gerät** starten; Live Activities, Push und CloudKit verhalten sich im Simulator anders

---

## Phase 1 — Die zwei echten Blocker

### CloudKit-Schema nach Production deployen

CloudKit Console → Container `iCloud.de.crabucate.Lehrer-Arbeitszeit` → Schema → **Deploy Schema Changes** → Production.

Alle drei Record-Typen liegen in der Zone `Arbeitseintraege`:

- [ ] `Arbeitseintrag` — `datum` (Date/Time), `stunden` (Double), `kategorie` (String), `notiz` (String)
- [ ] `LaufenderTimer` — `id` (String), `startzeit` (Date/Time), `kategorie` (String), `titel` (String), `notiz` (String)
- [ ] `Einstellung` — `wert` (Bytes)
- [ ] Deploy nach Production ausgeführt

Über CloudKit läuft **alles**: Einträge, der laufende Timer und die Einstellungen
(Stundenplan, Bundesland, Deputat, Erinnerung, Onboarding-Status). Der
`NSUbiquitousKeyValueStore` ist nicht mehr im Einsatz — er hatte keine
Latenzzusage und meldete Änderungen unzuverlässig.

**Der Klassiker, an dem Launches scheitern.** Development-Schema ≠ Production-Schema. Ohne Deploy
synchronisiert die Release-App bei *keinem* Nutzer — und das fällt erst nach dem Review auf.

### Archive-Entitlements verifizieren

Nach `Product → Archive`:

```sh
codesign -d --entitlements - "<Pfad>/Lehrer Arbeitszeit.app"
```

- [ ] `aps-environment` = **production** (nicht `development`)
- [ ] `com.apple.security.application-groups` = `group.de.crabucate.Lehrer-Arbeitszeit`
- [ ] `com.apple.developer.icloud-container-identifiers` gesetzt
- [ ] `com.apple.developer.icloud-services` = `CloudKit`

Der Schlüssel `ubiquity-kvstore-identifier` ist entfallen, seit die Einstellungen
über CloudKit laufen.

---

## Phase 2 — Testrunde

### Kern — ohne das nicht einreichen

- [x] **Zwei-Geräte-Sync iPhone ↔ iPad:** Eintrag anlegen / bearbeiten / löschen
- [x] **Timer auf Gerät A starten, auf Gerät B stoppen**
- [x] **Stundenplan auf A ändern** → kommt auf B an
- [x] **„Alle Daten löschen" auf A** → B wird ebenfalls leer
- [x] **Pausenaufsicht anlegen und löschen**
- [x] **Timer stoppen** — mit korrigierter und mit unveränderter Dauer
- [ ] **Erststart im Flugmodus:** Onboarding, Auto-Erfassung, Ferien (liegen in der App, sollte durchlaufen)
- [ ] **iCloud abgemeldet** — App darf nicht hängen oder abstürzen

### iPad

- [ ] Layout in Hoch- **und** Querformat (alle vier Orientierungen sind deklariert)
- [ ] **Split View / Slide Over** — die App erlaubt mehrere Fenster
      (`UIApplicationSupportsMultipleScenes`); zwei Fenster teilen sich `EintragStore.shared`
      und den laufenden Timer. Ungetestet.
- [x] **Live-Activity-Stopp** — geprüft mit App im Hintergrund und kalt gestartet
- [ ] Verhalten der Live Activity auf dem iPad prüfen
- [ ] **Live Activity auf dem Zweitgerät:** Timer auf A starten, während die App auf B
      offen ist → B zieht eine eigene Live Activity nach. Ist B im Hintergrund oder
      geschlossen, passiert nichts: Das System erlaubt `Activity.request()` nur im
      Vordergrund. Für den Hintergrundfall bräuchte es Push-to-Start mit eigenem Server.

### Weiteres

- [ ] Schuljahreswechsel (Systemdatum auf 1. August stellen)
- [ ] VoiceOver-Durchlauf — Labels sind ergänzt, aber nicht mit VoiceOver getestet
- [ ] Dynamic Type XXL — die 48-pt-Zahlen in den Dashboard-Karten brechen vermutlich
- [ ] Dark Mode
- [ ] App löschen + neu installieren bei vorhandenen iCloud-Daten

---

## Phase 3 — Screenshots

### Pflichtgrößen

- [ ] **iPhone 6.9"** — 1320 × 2868 px (iPhone 16/17 Pro Max)
- [ ] **iPad 13"** — 2064 × 2752 px (iPad Pro 13")

### Vorbereitung

- [ ] Realistischen Demo-Datensatz anlegen (plausibles Schuljahr, keine Fake-Notizen)
- [ ] Statusleiste säubern:

```sh
xcrun simctl status_bar <UDID> override \
  --time "9:41" --batteryState charged --batteryLevel 100 \
  --wifiBars 3 --cellularBars 4
```

### Motive (Reihenfolge = Priorität, die ersten zwei sind in der Suche sichtbar)

1. [ ] Tracker mit laufendem Timer
2. [ ] Analyse-Tab mit gefülltem Jahresverlauf
3. [ ] Jahresarbeitszeit-Karte (Soll vs. Ist) — das Alleinstellungsmerkmal
4. [ ] Stundenplan-Raster → „erfasst sich automatisch"
5. [ ] Live Activity auf dem Lock Screen

---

## Phase 4 — App Store Connect

- [ ] App-Eintrag anlegen, Bundle-ID `de.crabucate.Lehrer-Arbeitszeit`, **Primärsprache Deutsch**
- [ ] **Namen vereinheitlichen** — Projekt heißt „Lehrer Arbeitszeit", das Icon „Zeiterfassung Lehrer"
- [ ] Untertitel (max. 30 Zeichen)
- [ ] Keywords (max. 100 Zeichen), Vorschlag:
      `Lehrer, Zeiterfassung, Arbeitszeit, Schule, Deputat, Unterricht, Stundenplan, Überstunden`
- [ ] Beschreibung + Werbetext (max. 170 Zeichen)
- [ ] Kategorie: Produktivität (primär), Bildung (sekundär)
- [ ] Altersfreigabe: 4+
- [ ] **Support-URL** (Pflicht)
- [ ] **Datenschutzrichtlinie-URL** (Pflicht) — muss nur noch iCloud/CloudKit nennen. Die App
      stellt keine sonstigen Netzwerkverbindungen her: Ferien und Feiertage liegen in der App.
- [ ] App-Datenschutz-Fragebogen: „Es werden keine Daten erfasst"
      (die private CloudKit-Datenbank zählt nicht als Erfassung durch den Entwickler)
- [ ] Review-Notes: deutsche Lehrerarbeitszeit, kein Login nötig, keine Serveranbindung außer iCloud

---

## Phase 5 — Einreichen

- [ ] TestFlight-Build hochladen und intern testen — **nicht direkt einreichen**
- [ ] `CURRENT_PROJECT_VERSION` bei jedem Upload hochzählen (`MARKETING_VERSION` bleibt `1.0`)
- [ ] Zur Prüfung einreichen

---

## Wenn du nur eine Sache zuerst machst

**Phase 1, CloudKit Production.** Alles andere lässt sich nachträglich korrigieren — ein fehlendes
Production-Schema nicht: Dann liegt eine kaputte App im Store und du wartest auf den nächsten Review.

---

## Offene Punkte fürs nächste Release

Kein Blocker für 1.0, aber notiert:

- **`ferien.json` deckt die Schuljahre 2024/25–2029/30 ab** (alle 16 Bundesländer). Danach wertet
  die Auto-Erfassung jeden Tag als frei. Die Termine müssen nachgepflegt werden, sobald die
  Kultusministerien weitere Jahre beschließen — `LokaleFerienDatenTests` schlägt an, sobald der
  Vorlauf unter zwei Schuljahre fällt. Die **Feiertage** sind berechnet und brauchen keine Pflege.
- Für **Mecklenburg-Vorpommern** sind die Termine der *allgemein bildenden* Schulen hinterlegt.
  MV hat abweichende Termine für berufliche Schulen (Sommerferien bis zu eine Woche länger);
  Berufsschullehrkräfte dort müssten Einträge in der Differenzwoche manuell ergänzen.
- Kein Datenexport (CSV/PDF) — für eine Arbeitszeit-App ein naheliegender Nutzerwunsch
- `Double.toTimeString` formatiert negative Werte falsch; aktuell nicht erreichbar, aber fragil,
  falls irgendwann ein Saldo/Überstunden-Wert angezeigt wird

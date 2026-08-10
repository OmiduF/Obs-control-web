# PRD — OBS Auto Switch: Play → Main

## Problem statement (original)
Utilizatorul vrea ca atunci când un material media din scena **Play** se termină, OBS să comute automat pe scena **Main**.

## Context / mediu
- OBS Studio 32.2.1, Windows + macOS.
- Utilizatorul folosește plugin-urile **Aitum Vertical Canvas** și **Aitum Multistream**.
- OBS WebSocket este activat.

## Soluții livrate
1. `auto_switch_play_to_main.py` — script nativ OBS (obspython, Tools → Scripts).
   - Fix aplicat pentru crash pe OBS 32.x: callback `media_ended` doar setează un flag; comutarea reală se face în `script_tick` (thread principal).
   - Notă: rămâne fragil în combinație cu plugin-urile Aitum (rulează în procesul OBS).
2. `obs_autoswitch_ws.py` — **script EXTERN prin OBS WebSocket (recomandat)**.
   - Rulează în alt proces → nu poate face crash la OBS, imun la conflicte cu Aitum Vertical/Multistream.
   - Folosește `obsws-python`, ascultă evenimentul `MediaInputPlaybackEnded` și apelează `set_current_program_scene`.
   - Config: HOST/PORT/PASSWORD + PLAY_SCENE/MAIN_SCENE/MEDIA_SOURCE (constante sau variabile de mediu).
   - Opțiune `ONLY_WHEN_PLAY_ACTIVE`, reconectare automată.

## Fișiere
- `obs_autoswitch_ws.py`, `requirements-ws.txt`
- `auto_switch_play_to_main.py`
- `README.md`, `LICENSE`

## Status
- Varianta externă: validată static (import lib, semnături metode, mapare eveniment `on_media_input_playback_ended`). Rularea live în OBS nu e posibilă în acest mediu — necesită testul utilizatorului.

3. **Pagină web** (`frontend/src/App.js` + `App.css`) — panou de control în browser.
   - Se conectează direct la OBS WebSocket din browser folosind `obs-websocket-js` (v5.0.8).
   - Formular conexiune (host/port/parolă), dropdown-uri populate din OBS (scene + surse media ffmpeg/vlc), toggle „doar când Play e live”, delay configurabil, buton Arm/Pornire, log de activitate, contor comutări. Setări persistate în localStorage.
   - Ascultă `MediaInputPlaybackEnded`, verifică sursa/scena, apoi `SetCurrentProgramScene(Main)`.
   - Frontend-only (fără backend/DB). Nu testat runtime cu OBS live (mediu fără OBS); UI validat prin screenshot.

3. **Panou web unificat cu tab-uri** (`frontend/src`) — „OBS Control Deck".
   - Conexiune unică partajată (`obs/ObsProvider.js`): host/port/parolă, suport **IP din rețea**, dispecer central pentru evenimentul `MediaInputPlaybackEnded`, log partajat, refresh scene/surse.
   - **Tab Auto Switch** (`components/AutoSwitchTab.js`): mai multe reguli „sursă media → scenă" (adaugă/șterge), buton Arm.
   - **Tab Timer** (`components/TimerTab.js`): countdown MM:SS, opțional scrie în sursă text OBS; la final → scena INTRO; când media din INTRO se termină → MAIN.
   - **Tab Materiale** (`components/MaterialsTab.js`): media din scena MATERIALE se termină → MAIN; buton „Start material" (comută pe MATERIALE + restart media prin `TriggerMediaInputAction`); opțiune „doar când MATERIALE e live".
   - `components/ConnectionBar.js`, `components/LogPanel.js`. Toate setările persistate în localStorage.
   - Frontend-only. Compilează curat; UI validat prin screenshot. Interacțiunea reală cu OBS necesită testul utilizatorului (mediu fără OBS).

## Backlog / next
- Delay configurabil înainte de comutare.
- Suport pentru mai multe surse media / scene Play.
- Împachetare ca executabil (.exe / .app) ca să nu fie nevoie de Python instalat.

## Update - server local (obs_control_server.py)
- Utilizatorul vrea sa ruleze panoul local pe PC (localhost), nu pe Emergent.
- Livrat `obs_control_server.py`: server Python cu HTML embed (vanilla JS, client OBS WebSocket v5 implementat manual: Hello/Identify cu auth SHA256 via crypto.subtle, Request/Response, event MediaInputPlaybackEnded).
- Ruleaza pe http://localhost:8080 (port configurabil ca argument), deschide browserul automat. Contine toate 3 tab-urile (Auto Switch multi-reguli, Timer countdown->INTRO->MAIN, Materiale->MAIN). Persistenta in localStorage.
- Testat: HTTP 200, 23KB, markeri prezenti. Conexiunea reala la OBS necesita test la utilizator.
- Exista si `obs_control.html` (varianta file://) si varianta React pe preview Emergent.

## Update - Timer overlay (Browser Source pt OBS)
- Adaugat in obs_control_server.py: stare timer partajata pe server (TIMER + lock), rute GET /overlay (pagina transparenta care afiseaza countdown), GET/POST /api/timer (sincronizare intre panoul de control si OBS Browser Source, procese/browsere separate).
- Server trecut pe ThreadingHTTPServer (polling + control concurent). Overlay poll la 300ms; parametri optionali ?color=&size=&hide=1.
- Panoul Timer: la Start/Stop/Reset trimite POST /api/timer; afiseaza si linkul overlay (location.origin + /overlay).
- Verificat via curl: rutele, start/stop, scaderea numaratorii (10->7 in 3s). Randarea in OBS Browser Source = test la utilizator.
- Materiale lasate ca inainte (la cererea utilizatorului "restul sunt ok").

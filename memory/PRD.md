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

## Backlog / next
- Delay configurabil înainte de comutare.
- Suport pentru mai multe surse media / scene Play.
- Împachetare ca executabil (.exe / .app) ca să nu fie nevoie de Python instalat.

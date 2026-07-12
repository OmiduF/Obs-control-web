# OBS Auto Switch: Play → Main

Script pentru **OBS Studio** care comută automat pe scena **Main** atunci când un fișier media (video/audio) din scena **Play** ajunge la final.

Funcționează pe **Windows** și **macOS** (și Linux), nativ prin API-ul de scripting Python al OBS — fără WebSocket.

## Funcționalități

- Detectează când un material media se termină în scena aleasă și comută automat pe scena principală.
- Suportă atât **Media Source** (`ffmpeg_source`) cât și **VLC Video Source** (`vlc_source`).
- Nume de scene configurabile din interfața OBS (liste derulante).
- Opțiune: comută doar când scena „Play” este cea live.
- Buton pentru reîncărcarea surselor media.
- Se reconectează automat când se schimbă lista de scene sau colecția.

## Cerințe

- OBS Studio (cu suport Python).
- Python 3 instalat (Python 3.6+ recomandat).

## Instalare

1. Descarcă fișierul [`auto_switch_play_to_main.py`](auto_switch_play_to_main.py).
2. În OBS: **Tools → Scripts**.
3. Tab **Python Settings** → setează calea către instalarea Python (o singură dată).
4. Tab **Scripts** → apasă **„+”** și selectează `auto_switch_play_to_main.py`.
5. În panoul din dreapta:
   - **Scena Play (sursa)** → alege scena cu materialul media.
   - **Scena Main (destinație)** → alege scena principală.
   - Opțional: bifează *„Comută doar când Play este live”*.

## Utilizare

Redă un material media în scena **Play**. Când acesta se termină, OBS comută automat pe scena **Main**.

Dacă adaugi sau schimbi surse media în scena Play, apasă butonul **„Reîncarcă sursele media”**.

## Depanare

Deschide **Tools → Scripts → Script Log** pentru a vedea ce surse media sunt monitorizate și eventuale avertismente (ex. scenă negăsită).

## Licență

[MIT](LICENSE)

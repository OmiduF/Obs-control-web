# OBS Control Web

### OBS Studio automation tools for live production and streaming

A collection of automation tools for **OBS Studio**, focused on reliable scene switching and media playback workflows.

The project includes both a **native OBS Python script** and an **external OBS WebSocket implementation**, allowing automatic switching from a `Play` scene back to a `Main` scene when a media file finishes playing.

It was created for practical live-production workflows where media playback needs to be followed automatically by a return to the main production scene.

---

## 🎬 OBS Auto Switch: Play → Main

The main tool automatically switches OBS from a **Play** scene to a **Main** scene when the media currently playing reaches the end.

It supports:

- Media Source (`ffmpeg_source`)
- VLC Video Source (`vlc_source`)
- Configurable Play and Main scenes
- Optional switching only when the Play scene is live
- Media source reload
- Automatic reconnection when scenes or collections change

---

## 🐍 Native OBS Python Script

The native version runs directly inside OBS Studio using its Python scripting support.

### Installation

1. Download `auto_switch_play_to_main.py`.
2. Open **OBS Studio → Tools → Scripts**.
3. Go to **Python Settings** and select your Python installation.
4. Go to **Scripts** and press `+`.
5. Select `auto_switch_play_to_main.py`.
6. Configure the Play and Main scenes from the script interface.

### Usage

Play a media file in the configured Play scene.

When the media finishes, OBS automatically switches to the configured Main scene.

If media sources are added or changed, use the **Reload Media Sources** button.

---

## 🌐 External OBS WebSocket Version

An alternative implementation is available as:

`obs_autoswitch_ws.py`

This version runs **outside OBS Studio** and communicates through the OBS WebSocket API.

This approach can be useful when running OBS with additional plugins such as **Aitum Vertical** or multistreaming setups.

Because the automation runs externally, it is isolated from the OBS scripting environment and can reconnect automatically if the WebSocket connection is interrupted.

### Requirements

- OBS Studio
- OBS WebSocket server enabled
- Python 3
- `obsws-python`

Install the Python library:

```bash
pip install obsws-python
```

### Configuration

Configure the following values in `obs_autoswitch_ws.py`:

- `PORT`
- `PASSWORD`
- `PLAY_SCENE`
- `MAIN_SCENE`
- `MEDIA_SOURCE`

Alternatively, environment variables can be used:

```text
OBS_PORT
OBS_PASSWORD
OBS_PLAY_SCENE
OBS_MAIN_SCENE
OBS_MEDIA_SOURCE
```

### Run

```bash
python obs_autoswitch_ws.py
```

Leave the application running while OBS is being used. The script automatically reconnects if the connection is interrupted.

---

## 🖥️ Supported Platforms

The native OBS Python implementation is designed to work with:

- Windows
- macOS
- Linux

The external WebSocket implementation can run on any platform supported by Python and OBS WebSocket.

---

## 🎥 Typical Production Workflow

A typical workflow looks like this:

```text
                 OBS Studio
                     │
                     ▼
              ┌─────────────┐
              │    PLAY     │
              │    SCENE    │
              └──────┬──────┘
                     │
                Media plays
                     │
                     ▼
                Media ends
                     │
                     ▼
              ┌─────────────┐
              │    MAIN     │
              │    SCENE    │
              └─────────────┘
```

This is particularly useful for:

- Live streaming
- Sports production
- Broadcast automation
- Studio production
- Playout workflows
- Aitum Vertical workflows
- Multistreaming

---

## 🤖 Development

The project was developed from a practical live-production requirement and with assistance from **Emergent**, an AI-assisted development environment.

The focus is on simple automation that can be integrated into existing OBS workflows without requiring a large production system.

---

## 📁 Project Structure

```text
Obs-control-web/
├── backend/
├── frontend/
├── tests/
├── test_reports/
├── auto_switch_play_to_main.py
├── obs_autoswitch_ws.py
├── obs_control.html
├── obs_control_server.py
├── requirements-ws.txt
├── start_windows.bat
├── README.md
└── test_result.md
```

---

## 📜 License

This project is released under the **MIT License**.

---

## 👤 Author

**OmiduF**

Built for real-world OBS Studio and live-production workflows.

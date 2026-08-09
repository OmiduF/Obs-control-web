"""
OBS Auto Switch: Play -> Main  (versiune EXTERNA, prin OBS WebSocket)
====================================================================

Ce face:
  Se conecteaza la OBS prin WebSocket si asculta evenimentul de final
  al unei surse media. Cand sursa media aleasa (din scena Play) se termina,
  comuta automat OBS pe scena Main.

De ce extern:
  Ruleaza in ALT proces, deci NU poate face crash la OBS. Functioneaza
  chiar daca ai Aitum Vertical Canvas / Multistream instalate.

Cerinte in OBS:
  Tools -> WebSocket Server Settings -> bifat "Enable WebSocket server".
  De acolo iei portul si parola (buton "Show Connect Info").

Cum rulezi:
  1. Instaleaza libraria (o singura data):
        pip install obsws-python
  2. Completeaza setarile de mai jos (PORT, PAROLA, nume scene, sursa media).
     Optional le poti pune si ca variabile de mediu (vezi mai jos).
  3. Ruleaza:
        python obs_autoswitch_ws.py
  Lasa fereastra deschisa cat timp streamezi.
"""

import os
import time

import obsws_python as obs

# ============================================================
#  SETARI  — editeaza aici (sau foloseste variabile de mediu)
# ============================================================
HOST = os.environ.get("OBS_HOST", "localhost")
PORT = int(os.environ.get("OBS_PORT", "4455"))
PASSWORD = os.environ.get("OBS_PASSWORD", "PUNE_PAROLA_AICI")

PLAY_SCENE = os.environ.get("OBS_PLAY_SCENE", "Play")   # scena sursa
MAIN_SCENE = os.environ.get("OBS_MAIN_SCENE", "Main")   # scena destinatie
MEDIA_SOURCE = os.environ.get("OBS_MEDIA_SOURCE", "media")  # numele sursei media

# Comuta doar daca scena Play este cea live in momentul terminarii.
ONLY_WHEN_PLAY_ACTIVE = os.environ.get("OBS_ONLY_WHEN_PLAY_ACTIVE", "1") == "1"
# ============================================================


def log(msg):
    print("[auto-switch] %s" % msg, flush=True)


def get_current_scene_name(req):
    resp = req.get_current_program_scene()
    # numele campului difera intre versiuni ale bibliotecii
    for attr in ("current_program_scene_name", "scene_name", "current_program_scene"):
        name = getattr(resp, attr, None)
        if name:
            return name
    return None


def make_on_media_ended(req):
    def on_media_input_playback_ended(data):
        ended_source = getattr(data, "input_name", None)
        log("Media terminata: %s" % ended_source)

        # ne intereseaza doar sursa media aleasa
        if MEDIA_SOURCE and ended_source != MEDIA_SOURCE:
            return

        try:
            if ONLY_WHEN_PLAY_ACTIVE:
                current = get_current_scene_name(req)
                if current != PLAY_SCENE:
                    log("Scena live este '%s', nu '%s' -> nu comut." % (current, PLAY_SCENE))
                    return

            req.set_current_program_scene(MAIN_SCENE)
            log("Am comutat pe scena '%s'." % MAIN_SCENE)
        except Exception as e:
            log("Eroare la comutare: %s" % e)

    return on_media_input_playback_ended


def run():
    if PASSWORD == "PUNE_PAROLA_AICI":
        log("ATENTIE: nu ai setat parola WebSocket. Editeaza PASSWORD in script "
            "sau seteaza variabila de mediu OBS_PASSWORD.")

    while True:
        try:
            log("Ma conectez la OBS %s:%s ..." % (HOST, PORT))
            req = obs.ReqClient(host=HOST, port=PORT, password=PASSWORD, timeout=5)
            ev = obs.EventClient(host=HOST, port=PORT, password=PASSWORD)

            ev.callback.register(make_on_media_ended(req))
            log("Conectat. Ascult finalul sursei media '%s' in scena '%s'. "
                "(Ctrl+C pentru oprire)" % (MEDIA_SOURCE, PLAY_SCENE))

            # tinem procesul viu; evenimentele vin pe thread separat
            while True:
                time.sleep(1)

        except KeyboardInterrupt:
            log("Oprit de utilizator.")
            break
        except Exception as e:
            log("Conexiune pierduta / esuata: %s" % e)
            log("Reincerc in 5 secunde...")
            time.sleep(5)


if __name__ == "__main__":
    run()

"""
Auto Switch: Play -> Main
==========================
Script pentru OBS Studio (Python).

Ce face:
  Cand un fisier media (video/audio) din scena "Play" ajunge la final,
  OBS comuta automat pe scena "Main".

Cum se instaleaza:
  1. In OBS: Tools -> Scripts
  2. Apasa "+" si selecteaza acest fisier (auto_switch_play_to_main.py)
  3. In dreapta, alege scena Play si scena Main din liste
  (Ai nevoie de Python instalat si configurat in OBS: Tools -> Scripts -> tab "Python Settings")
"""

import obspython as obs

# ---- Setari (configurabile din interfata OBS) ----
play_scene_name = "Play"
main_scene_name = "Main"
only_when_play_active = True  # comuta doar daca scena Play e cea live

# lista handler-elor conectate, ca sa le putem deconecta la reload
_connected_handlers = []


# ------------------------------------------------------------------
# Callback apelat cand un media source si-a terminat redarea
# ------------------------------------------------------------------
def on_media_ended(calldata):
    # daca vrem sa comutam doar cand Play e scena curenta
    if only_when_play_active:
        current = obs.obs_frontend_get_current_scene()
        if current is not None:
            current_name = obs.obs_source_get_name(current)
            obs.obs_source_release(current)
            if current_name != play_scene_name:
                return

    # gaseste sursa scenei Main si comuta pe ea
    main_source = obs.obs_get_source_by_name(main_scene_name)
    if main_source is not None:
        obs.obs_frontend_set_current_scene(main_source)
        obs.obs_source_release(main_source)
    else:
        obs.script_log(obs.LOG_WARNING,
                       "Scena '%s' nu a fost gasita." % main_scene_name)


# ------------------------------------------------------------------
# Conecteaza semnalul media_ended pentru sursele media din scena Play
# ------------------------------------------------------------------
def connect_play_media_sources():
    disconnect_all()

    play_source = obs.obs_get_source_by_name(play_scene_name)
    if play_source is None:
        obs.script_log(obs.LOG_WARNING,
                       "Scena '%s' nu a fost gasita." % play_scene_name)
        return

    scene = obs.obs_scene_from_source(play_source)
    items = obs.obs_scene_enum_items(scene)
    if items is not None:
        for item in items:
            source = obs.obs_sceneitem_get_source(item)
            if source is None:
                continue
            source_id = obs.obs_source_get_id(source)
            # sursele media in OBS: ffmpeg_source (Media Source) si vlc_source (VLC)
            if source_id in ("ffmpeg_source", "vlc_source"):
                handler = obs.obs_source_get_signal_handler(source)
                obs.signal_handler_connect(handler, "media_ended", on_media_ended)
                _connected_handlers.append(obs.obs_source_get_name(source))
        obs.sceneitem_list_release(items)

    obs.obs_source_release(play_source)

    if _connected_handlers:
        obs.script_log(obs.LOG_INFO,
                       "Monitorizez %d sursa/e media in scena '%s': %s" %
                       (len(_connected_handlers), play_scene_name,
                        ", ".join(_connected_handlers)))
    else:
        obs.script_log(obs.LOG_WARNING,
                       "Nu am gasit surse media in scena '%s'." % play_scene_name)


def disconnect_all():
    # Deconectam prin re-obtinerea handler-elor din scena curenta.
    play_source = obs.obs_get_source_by_name(play_scene_name)
    if play_source is not None:
        scene = obs.obs_scene_from_source(play_source)
        items = obs.obs_scene_enum_items(scene)
        if items is not None:
            for item in items:
                source = obs.obs_sceneitem_get_source(item)
                if source is None:
                    continue
                source_id = obs.obs_source_get_id(source)
                if source_id in ("ffmpeg_source", "vlc_source"):
                    handler = obs.obs_source_get_signal_handler(source)
                    obs.signal_handler_disconnect(handler, "media_ended", on_media_ended)
            obs.sceneitem_list_release(items)
        obs.obs_source_release(play_source)
    _connected_handlers.clear()


# ------------------------------------------------------------------
# Reconecteaza cand se schimba lista de scene / surse
# ------------------------------------------------------------------
def on_frontend_event(event):
    if event in (obs.OBS_FRONTEND_EVENT_SCENE_LIST_CHANGED,
                 obs.OBS_FRONTEND_EVENT_SCENE_COLLECTION_CHANGED,
                 obs.OBS_FRONTEND_EVENT_FINISHED_LOADING):
        connect_play_media_sources()


# ------------------------------------------------------------------
# Interfata (proprietati) in panoul Scripts
# ------------------------------------------------------------------
def script_description():
    return ("<b>Auto Switch: Play -> Main</b><br>"
            "Cand un material media din scena aleasa se termina, "
            "OBS comuta automat pe scena principala.")


def _populate_scene_list(prop):
    obs.obs_property_list_clear(prop)
    scenes = obs.obs_frontend_get_scenes()
    if scenes is not None:
        for s in scenes:
            name = obs.obs_source_get_name(s)
            obs.obs_property_list_add_string(prop, name, name)
        obs.source_list_release(scenes)


def script_properties():
    props = obs.obs_properties_create()

    p_play = obs.obs_properties_add_list(
        props, "play_scene_name", "Scena Play (sursa)",
        obs.OBS_COMBO_TYPE_EDITABLE, obs.OBS_COMBO_FORMAT_STRING)
    p_main = obs.obs_properties_add_list(
        props, "main_scene_name", "Scena Main (destinatie)",
        obs.OBS_COMBO_TYPE_EDITABLE, obs.OBS_COMBO_FORMAT_STRING)

    _populate_scene_list(p_play)
    _populate_scene_list(p_main)

    obs.obs_properties_add_bool(
        props, "only_when_play_active",
        "Comuta doar cand scena Play este live")

    obs.obs_properties_add_button(
        props, "reconnect_btn", "Reincarca sursele media",
        lambda *args: (connect_play_media_sources() or True))

    return props


def script_defaults(settings):
    obs.obs_data_set_default_string(settings, "play_scene_name", "Play")
    obs.obs_data_set_default_string(settings, "main_scene_name", "Main")
    obs.obs_data_set_default_bool(settings, "only_when_play_active", True)


def script_update(settings):
    global play_scene_name, main_scene_name, only_when_play_active
    play_scene_name = obs.obs_data_get_string(settings, "play_scene_name")
    main_scene_name = obs.obs_data_get_string(settings, "main_scene_name")
    only_when_play_active = obs.obs_data_get_bool(settings, "only_when_play_active")
    connect_play_media_sources()


def script_load(settings):
    obs.obs_frontend_add_event_callback(on_frontend_event)


def script_unload():
    disconnect_all()

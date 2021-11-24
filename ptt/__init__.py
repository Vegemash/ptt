import os
from time import sleep
import typer

from evdev import InputDevice, categorize, ecodes

app = typer.Typer()

F24 = 194
F23 = 193
F22 = 192

# ls your /dev/input/by-id to find your input of choice
# the pure numbers will jump around
KEYBOARD = "/dev/input/by-id/usb-ZSA_Moonlander_Mark_I-event-kbd"

# Get this through `pactl list cards`
CARD_ID = os.environ.get("CARD_ID", "bluez_card.4C_87_5D_2C_E3_BD")

MIC_PROFILE = os.environ.get("MIC_PROFILE", "headset-head-unit")
MUTE_PROFILE = os.environ.get("MIC_PROFILE", "a2dp-sink")
SET_PROFILE = False


def mic_on() -> None:
    if SET_PROFILE:
        os.system(f"pactl set-card-profile {CARD_ID} {MIC_PROFILE}")
    os.system("amixer set Capture cap &> /dev/null")
    os.system("amixer set Capture 100% &> /dev/null")
    os.system("play /opt/chime.mp3 &> /dev/null")


def mic_off() -> None:
    if SET_PROFILE:
        os.system(f"pactl set-card-profile {CARD_ID} {MUTE_PROFILE}")
    os.system("amixer set Capture nocap &> /dev/null")
    os.system("amixer set Capture 0% &> /dev/null")
    os.system("play /opt/chime.mp3 reverse &> /dev/null")


def is_mic_on() -> bool:
    return os.system("amixer get Capture | grep off &> /dev/null") != 0


@app.command()
def main(set_profile: bool):
    global SET_PROFILE
    SET_PROFILE = set_profile
    while True:
        try:
            device = InputDevice(KEYBOARD)
            for event in device.read_loop():
                if event.type == ecodes.EV_KEY:
                    ce = categorize(event)
                    # Push to talk
                    if ce.scancode == F24:
                        if ce.keystate == 1:
                            mic_on()
                        elif ce.keystate == 0:
                            mic_off()
                    # On key
                    if ce.scancode == F23 and ce.keystate == 1 and is_mic_on():
                        mic_off()
                    # Off key
                    if ce.scancode == F22 and ce.keystate == 1 and not is_mic_on():
                        mic_on()

        except OSError:
            sleep(1)
            pass

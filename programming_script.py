from shutil import which
from datetime import datetime, timezone
from pathlib import Path
import subprocess
import time
import board
import neopixel_spi
import digitalio
import os


def show_status(pixel, status):
    if status == "ready":
        pixel.fill([0, 0, 0, 255])
    elif status == "busy":
        pixel.fill([255, 150, 0, 0])
    elif status == "success":
        pixel.fill([0, 255, 0, 0])
    elif status == "error":
        pixel.fill([255, 0, 0, 0])
    elif status == "none":
        pixel.fill([0, 0, 50, 0])
    else:
        raise ValueError("invalid status was given")


# Run counter
run = 0

# Set up GPIOs
led = neopixel_spi.NeoPixel_SPI(
    board.SPI(), 2, pixel_order=neopixel_spi.GRBW, bit0=0b10000000
)
button = digitalio.DigitalInOut(board.D17)
button.direction = digitalio.Direction.INPUT
button.pull = digitalio.Pull.UP

print("Starting Brilliant Monocle Programmer")
show_status(led, "busy")

# Check that the relevant software is installed
if which("nrfjprog") == None:
    print("nRF command line tools not found")
    show_status(led, "error")
    exit(1)

if which("JLinkExe") == None:
    print("J-Link software not found")
    show_status(led, "error")
    exit(1)

if which("openFPGALoader") == None:
    print("Open FPGA Loader not found")
    show_status(led, "error")
    exit(1)

# Disable echos
os.system("stty -echo")

# Forever
while True:
    try:
        print("\nReady. Press button to start programming. Press <Ctrl-C> to exit")
        show_status(led, "ready")

        # Wait until the button is pressed
        while button.value == 1:
            pass

        if subprocess.check_output(["nrfjprog", "-i"]) == b"":
            raise Exception("nRF52 programmer not connected")

        if b"ft232" not in subprocess.check_output(["openFPGALoader", "--scan-usb"]):
            raise Exception("FPGA programmer not connected")

        now = datetime.now(timezone.utc).strftime("%d/%m/%Y, %H:%M:%S")
        run += 1
        print(f"Starting programming. Run {run} at {now}")
        show_status(led, "busy")

        print("Erasing nRF52 to flash temporary binary")
        subprocess.run(["nrfjprog", "--recover", "-q"], check=True)

        print("Flashing temporary nRF52 binary")
        subprocess.run(
            [
                "nrfjprog",
                "--program",
                "monocle_micropython_power_only.hex",
                "--verify",
                "--reset",
                "-q",
            ],
            check=True,
        )

        print("Waiting for rails to stabilize")
        time.sleep(1)

        print("Flashing FPGA image")
        subprocess.run(
            [
                "openFPGALoader",
                "--cable",
                "ft232RL",
                "--fpga-part",
                "0x0100481b",
                "--freq",
                "1000000",
                "--pins=TXD:RXD:DTR:RTS",
                "--write-flash",
                "monocle_fpga_image_latest.fs",
            ],
            check=True,
        )  # , stdout=subprocess.DEVNULL)

        print("Erasing nRF52 to flash final binary")
        subprocess.run(["nrfjprog", "--recover", "-q"], check=True)

        print("Flashing final nRF52 binary")
        subprocess.run(
            [
                "nrfjprog",
                "--program",
                "monocle_micropython_latest.hex",
                "--verify",
                "--reset",
                "-q",
            ],
            check=True,
        )

        print("Sucessfully programmed Monocle")
        show_status(led, "success")
        time.sleep(3)

    except KeyboardInterrupt:
        break

    except Exception as e:
        print(e)
        show_status(led, "error")
        time.sleep(3)
        pass

# Exit
print("Exiting")
show_status(led, "none")
os.system("stty echo")

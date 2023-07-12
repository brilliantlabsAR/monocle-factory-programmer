# Monocle Factory Programming Jig

This is the jig used to program Monocles at the factory. Internally, it contains a Raspberry Pi, J-Link programmer, and FT232 breakout board for programming the FPGA. The interface consists of a button for initiating programming and an LED for displaying the status.

## Operation:

Upon power-on, the jig automatically launches the programming application. Wait for the **Green** LED to illuminate, and then press the button to initiate the programming process.

During programming, the LED will become **Amber**. **DO NOT** remove the Monocle board during this period, otherwise it could damage the FPGA. After some moments, the LED will change color to indicate the status of programming:

- **Green:** The board was successfully programmed.
- **Red:** The board is bad, and could not be programmed.

The Monocle board can now be removed, and another one inserted. Press the button again to start a new programming run.

A **Blue** LED means there was an error with the programming jig. In this case, try to restart it, or check the logs.

![Image of the Monocle factory programming jig](#)

## How it's built:

### Assembly

![Image of the Monocle Programming Jig Wiring Diagram](/images/wiring-diagram.drawio.png)

### Raspberry Pi Setup:

1. Install Raspberry Pi OS Lite (64bit), using the [Raspberry Pi Imager](https://www.raspberrypi.com/software/).

1. Connect to the Raspberry Pi via SSH over your network:

```sh
ssh brilliant@brilliant.local
```

1. Update the Raspberry Pi:

```sh
sudo apt update
sudo apt full-upgrade
sudo apt clean
```

1. Install [openFPGALoader](https://trabucayre.github.io/openFPGALoader/guide/install.html):

```sh
sudo apt install \
  git \
  gzip \
  libftdi1-2 \
  libftdi1-dev \
  libhidapi-hidraw0 \
  libhidapi-dev \
  libudev-dev \
  zlib1g-dev \
  cmake \
  pkg-config \
  make \
  g++

git clone https://github.com/trabucayre/openFPGALoader ~/downloads/openfpgaloader
cd ~/downloads/openfpgaloader
mkdir build
cd build
cmake ..
cmake --build .

sudo make install
```

1. Install the [nRF Command Line Tools](https://www.nordicsemi.com/Products/Development-tools/nRF-Command-Line-Tools/):

```sh
wget -O ~/downloads/nrf_command_line_tools.deb \
  https://nsscprodmedia.blob.core.windows.net/prod/software-and-other-downloads/desktop-software/nrf-command-line-tools/sw/versions-10-x-x/10-22-0/nrf-command-line-tools_10.22.0_arm64.deb

sudo dpkg -i ~/downloads/nrf_command_line_tools.deb

sudo apt install /opt/nrf-command-line-tools/share/JLink_Linux_V780c_arm64.deb --fix-broken

sudo sh -c 'dpkg --fsys-tarfile /opt/nrf-command-line-tools/share/JLink_Linux_V780c_arm64.deb | tar xOf - ./etc/udev/rules.d/99-jlink.rules > /etc/udev/rules.d/99-jlink.rules'

```

1. Install Python libraries:

```sh
sudo apt install python3-pip
sudo pip3 install rpi_ws281x adafruit-circuitpython-neopixel-spi
```

1. Enable SPI via `raspi-config` and enable user group:

```sh
sudo usermod -aG gpio,spi,plugdev <USER>
sudo raspi-config
```

1. Download the latest release files:

```sh
wget -O ~/monocle_micropython_power_only.hex \
  https://raw.githubusercontent.com/brilliantlabsAR/monocle-factory-programmer/main/monocle_micropython_power_only.hex

curl -s https://api.github.com/repos/brilliantlabsAR/monocle-micropython/releases/latest \
  | grep "browser_download_url.*hex" \
  | cut -d : -f 2,3 \
  | tr -d \" \
  | wget -O ~/monocle_micropython_latest.hex -i -

# TODO change this to the latest release, once it's ready
wget -O ~/monocle_fpga_image_latest.fs \
  https://github.com/brilliantlabsAR/monocle-fpga/releases/download/v230117/fpga_proj.fs
```

1. Download the programming script:

```sh
wget -O ~/programming_script.py \
  https://raw.githubusercontent.com/brilliantlabsAR/monocle-factory-programmer/main/programming_script.py
```

1. Configure the user's `.bashrc` to run the script upon power on:

```sh
echo python ~/programming_script.py >> ~/.bashrc
```

1. Open `raspi-config` and enable `Console Autologin` under `System Options` -> `Boot / Auto Login`.

1. Open `raspi-config` and enable `Overlay File System` under `Performance Options`.

1. Restart and hit the button to see if it worked!
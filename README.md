# Monocle Programming Jig

This is the jig which is used to program Monocles at the factory. Internally, it contains a Raspberry Pi, J-Link programmer, and FT232 breakout board to program the FPGA. The interface is simply a button to initiate programming, and an LED to display the status.

## Operation:

Upon power on, the programming jig automatically runs the programming application. Wait for the **White** LED, and press the button to start programming.

- **White:** Ready. Press the button to start programming.
- **Amber:** Busy. The board is being programmed.
- **Green:** Success: The board was successfully programmed.
- **Red:** Failure: The board could not be programmed.

![Image of the Monocle factory programming jig](#)

## How the jig is built:

### Assembly

### Raspberry Pi Setup:

1. Using [Raspberry Pi Imager](https://www.raspberrypi.com/software/), install Raspberry Pi OS Lite (64bit).

1. SSH to the Raspberry Pi over your network:

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
pip3 install rpi_ws281x adafruit-circuitpython-neopixel-spi
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

# TODO change this to the latest, once the final image is ready
wget -O ~/monocle_fpga_image_latest.fs \
  https://github.com/brilliantlabsAR/monocle-fpga/releases/download/v230117/fpga_proj.fs
```

1. Download the programming script:

```sh
wget -O ~/programming_script.py \
  https://raw.githubusercontent.com/brilliantlabsAR/monocle-factory-programmer/main/programming_script.py
```

1. Set up the system to run the file on power on

```sh
```

1. Make the system read only

```sh
```

1. Restart!

```sh
sudo reboot now
```

# Installing airframe on the Pi

Written for a Raspberry Pi Zero 2 W running Raspberry Pi OS Lite (Bookworm or later) with a
Pimoroni Inky Impression 13.3". The paths below match `airframe.service`; change both together
if you install somewhere other than `/opt/airframe`.

## 1. Enable the buses

The panel is driven over SPI and detected over I2C. In `sudo raspi-config` →
*Interface Options*, enable **SPI** and **I2C**, then reboot. Without I2C the EEPROM can't be
read; airframe logs that and drives the 13.3" panel directly, so it still works, but it can no
longer tell you that you plugged in a different Inky.

## 2. Install the code

```bash
sudo adduser --system --group --home /opt/airframe airframe
sudo -u airframe git clone https://github.com/shaurya10n/airframe.git /opt/airframe
cd /opt/airframe
sudo -u airframe python3 -m venv .venv
sudo -u airframe .venv/bin/pip install -e ".[pi]"
```

`.[pi]` pulls in `inky`, which brings numpy, spidev, smbus2 and gpiodevice. On a Zero 2 W this
takes a while; numpy has an aarch64 wheel, so it shouldn't build from source. Don't install the
`analysis` extra here — that tooling is laptop-only and downloads gigabytes.

## 3. Configure

```bash
sudo -u airframe cp config/airframe.example.toml config/airframe.toml
sudo -u airframe nano config/airframe.toml
```

Set the location, and in `[display]`:

```toml
backend = "inky"
rotation = 90   # 90 or 270, depending on which way up the frame hangs
eink_preview = false
```

The poster is portrait (1200 × 1600) and the panel is landscape (1600 × 1200), so the frame is
rotated on the way out. `90` puts the poster's top edge on the panel's left edge. If the frame
comes out upside down for how you've mounted it, use `270`; nothing else changes.

## 4. Seed the aircraft database (optional, but it saves the first boot)

The first update downloads `aircraft.csv.gz` (~10 MB) and indexes it into SQLite, which is
logged as taking about a minute on a Pi. Building it on a laptop and copying it over skips
that, and gets the first frame up sooner:

```bash
# on the laptop, in a checkout with the venv set up
python -m airframe --once
rsync -a data/cache/reference/ airframe-pi:/opt/airframe/data/cache/reference/
```

The Pi refreshes the database by itself when the copy is more than 14 days old.

## 5. Install the service

```bash
sudo cp deploy/airframe.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now airframe
journalctl -u airframe -f
```

`Restart=always` with a 30 s delay covers the ordinary failures: a boot that gets going before
Wi-Fi associates, or an adsb.lol outage while the process is starting. Once the loop is
running, a failed poll is caught and logged and the current frame stays up.

## Checking it by hand

```bash
sudo -u airframe /opt/airframe/.venv/bin/python -m airframe --once -v
```

That does one poll, scores the candidates with their scores logged, and pushes one frame.
A full refresh takes tens of seconds, flashes through several colors, and the driver waits for
the panel's busy line before returning — so it looks like it's hanging when it's working.

## Things to check the first time

- **Colors.** The panel is six colors with dithering. `output/frame-eink.png` from the laptop
  preview simulates it; compare the two and adjust the poster palette in
  `src/airframe/render/theme.py` if the real panel disagrees.
- **Memory.** A render peaks at roughly 190 MB resident with artwork cached, against 512 MB of
  RAM. `systemctl status airframe` reports the peak. If it's tight, lower `maxsize` on the
  artwork cache in `src/airframe/render/aircraft.py`.
- **SD card wear.** The journal is the only thing written regularly. If you want to be careful,
  set `Storage=volatile` in `/etc/systemd/journald.conf`.

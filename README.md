# Sofle

- [English](README.md)
- [中文](README_CN.md)

## Update List

- 2024/12/21
  1. Added support for zmk-studio (just refresh the left hand to use).
- 2024/10/24
  1. Modified power supply mode to reduce power consumption.
  2. Fixed the automatic shut-off feature for RGB power supply.
- 2025/3/30
  1. Added a 1-hour sleep entry time, increased the debounce time, and optimized power consumption while asleep.
- 2025/8/22
  1. update the soft off.When you press the keys Q, S and Z simultaneously and hold them for 2 seconds, the keyboard will enter a deep sleep state and cannot be awakened by pressing the keys. This function can be used when carrying it outside. The activation method is to press the reset switch once.
  2. This month, I also updated the low-profile (choc switch) versions of the sofle and corne cases. The frame and base plate have been thickened, and the opening of the reset switch has been adjusted so that the reset switch can be easily pressed. At present, we are still working out how to design a case with a tented (inclined) bracket. If you look closely at the PCB, you will notice reserved interfaces for expansion IO. I wonder if anyone has been able to make use of them — I will give it a try!
  3. The GIF animations on the right-hand keyboard screen have been removed, which will significantly reduce the power consumption of the right-hand keyboard.

> If your  sofle was updated before 2025/8/22, please update to the latest firmware.
>

## Contact Me

For 3D printed model files or any issues and malfunctions with the keyboard, please contact [380465425@qq.com](mailto:380465425@qq.com)

## Build Locally with Docker

The local builder needs only a running Docker installation. The compiler, Zephyr SDK,
West, and Python dependencies run inside ZMK's official build image.

Build all firmware targets:

```sh
./build.sh
```

Build one target:

```sh
./build.sh eyelash_sofle_right
./build.sh eyelash_sofle_studio_left
./build.sh settings_reset
```

Finished firmware is written to `dist/`. The first build downloads the Docker image and
ZMK dependencies, so it takes longer. Later builds reuse the `zmk-sofle-build-cache`
Docker volume. Set `ZMK_BUILD_IMAGE` or `ZMK_BUILD_CACHE_VOLUME` to override those
defaults. The official image currently uses `linux/amd64`; override
`ZMK_BUILD_PLATFORM` if a native image becomes available for your host.

## Sofle Keymap

![Sofle keymap](keymap-drawer/eyelash_sofle.svg)

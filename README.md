# Multicade-55in1-MAME-Bootleg

Welcome to Multicade 55in1 MAME Bootleg. 55 Classic Arcade Games. Only at MAME4Droid 0.139u1 for Arcade ROMs.

## ROM Information

| Property | Value |
|---|---|
| **ROM Name** | multcade |
| **ROM Clone** | multcade.zip |
| **Rom Parent** | 39in1 (39in1.zip) |
| **System** | MAME4Droid 0.139u1 (MAME 0.139u1) |
| **Hardware** | Bootleg MAME-based arcade PCB (Intel Xscale PXA255 @ 200 MHz) |
| **Status** | MACHINE_NOT_WORKING / MACHINE_IMPERFECT_SOUND |

## ROM Files

### multcade.zip (Clone ROM — 55-in-1)
Contains the individual game ROM data for all 55 games included in the Multicade bootleg. This is the clone ROM that references the parent ROM `39in1.zip` for shared hardware resources (program ROM, flash data, and EEPROM).

### 39in1.zip (Parent ROM)
Contains the hardware-level ROM images shared across the bootleg PCB family:

| File | Size | Description |
|---|---|---|
| `27c4096_plz-v001_ver.300.bin` | 524,288 bytes | Main program ROM (encrypted) |
| `16mflash.bin` | 2,097,152 bytes | Flash data ROM (compressed ROM filesystem, CGC-NP203) |
| `93c66_eeprom.bin` | 512 bytes | EEPROM security data (93C66 16-bit) |

## 55 Classic Arcade Games

| # | Game Title | MAME ROM Set | Year |
|---|---|---|---|
| 1 | Ms. Pac-Man | mspacman | 1982 |
| 2 | Galaga | galaga | 1981 |
| 3 | Frogger | frogger | 1981 |
| 4 | Donkey Kong | dkong | 1981 |
| 5 | Donkey Kong Junior | dkongjr | 1982 |
| 6 | Donkey Kong 3 | dkong3 | 1983 |
| 7 | Galaxian | galaxian | 1979 |
| 8 | Dig Dug | digdug | 1982 |
| 9 | Crush Roller | crush | 1981 |
| 10 | Mr. Do | mrdo | 1982 |
| 11 | Space Invaders | invaders | 1978 |
| 12 | Pac-Man | pacman | 1980 |
| 13 | Galaga 3 | galaga3 | 1984 |
| 14 | Gyruss | gyruss | 1983 |
| 15 | Tank Battalion | tankbatt | 1980 |
| 16 | Ladybug | ladybug | 1981 |
| 17 | Millipede | milliped | 1982 |
| 18 | Burger Time | btime | 1982 |
| 19 | Jr. Pac-Man | jrpacman | 1983 |
| 20 | Mappy | mappy | 1983 |
| 21 | Pengo | pengo | 1982 |
| 22 | 1942 | 1942 | 1984 |
| 23 | Centipede | centiped | 1981 |
| 24 | Phoenix | phoenix | 1980 |
| 25 | Time Pilot | timeplt | 1982 |
| 26 | Super Cobra | scobra | 1981 |
| 27 | Video Hustler | hustler | 1981 |
| 28 | Space Panic | panic | 1980 |
| 29 | Super Breakout | sbrkout | 1978 |
| 30 | New Rally-X | nrallyx | 1981 |
| 31 | Arkanoid | arkanoid | 1986 |
| 32 | Qix | qix | 1981 |
| 33 | Juno First | junofrst | 1983 |
| 34 | Xevious | xevious | 1982 |
| 35 | Mr. Do's Castle | docastle | 1983 |
| 36 | Moon Cresta | mooncrst | 1980 |
| 37 | Pinball Action | pbaction | 1985 |
| 38 | Scramble | scramble | 1981 |
| 39 | Super Pac-Man | superpac | 1982 |
| 40 | Bomb Jack | bombjack | 1983 |
| 41 | Shao-Lin's Road | shaolins | 1985 |
| 42 | King & Balloon | kingball | 1980 |
| 43 | 1943: The Battle of Midway | 1943 | 1987 |
| 44 | Van Van-Car | vanvan | 1983 |
| 45 | Pac-Man Plus | pacplus | 1982 |
| 46 | Dig Dug II | digdug2 | 1985 |
| 47 | Amidar | amidar | 1981 |
| 48 | Zaxxon | zaxxon | 1982 |
| 49 | Pooyan | pooyan | 1982 |
| 50 | Pleiads | pleiads | 1981 |
| 51 | Gun Smoke | gunsmoke | 1985 |
| 52 | The End | theend | 1980 |
| 53 | 1943 Kai: Midway Kaisen | 1943kai | 1987 |
| 54 | Congo Bongo | congo | 1983 |
| 55 | Jumping Jack | jjack | 1983 |

## Usage

1. Place both `multcade.zip` and `39in1.zip` in your MAME4Droid ROMs directory
2. Ensure you are using MAME4Droid 0.139u1 for compatibility
3. The parent ROM (`39in1.zip`) must be present for the clone (`multcade.zip`) to function
4. Launch the multcade ROM from your MAME4Droid game list

## Hardware Notes

The Multicade bootleg PCB is based on an Intel Xscale PXA255 processor running at 200 MHz with ARMv5TE instruction set. The flash ROM contains a compressed filesystem (CGC-NP203 format) with embedded game ROMs, fonts, and graphics. The main program ROM is encrypted with a CPLD-based protection scheme. Individual game ROM files from the 55 included games are provided separately in this repository for reference and use with standard MAME game drivers.

## Repository Contents

- `multcade.zip` — Clone ROM archive (55-in-1 Multicade bootleg)
- `39in1.zip` — Parent ROM archive (39-in-1 MAME bootleg, GNO-V000)
- Individual game ROM ZIP files for each of the 55 arcade titles
- `README.md` — This documentation file

## License

This repository is provided for archival and educational purposes. MAME is licensed under the BSD-3-Clause license. All game titles and ROM data are property of their respective copyright holders.

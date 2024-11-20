# Ambient Sound Mixer

A customizable ambient sound mixer application created by Zavi Quintero (ZaviQ7) that allows you to mix different environmental sounds with volume control and effects.

## Features
- Mix multiple ambient sounds:
  - Rain
  - Coffee Shop
  - White Noise
  - Forest
  - Ocean
- Individual volume control for each sound
- Audio effects with customizable parameters:
  - Reverb
  - 3-band EQ (Low, Mid, High)
- Save and load custom presets
- Category and tag support for preset organization

## Installation

1. Clone this repository:
```bash
git clone https://github.com/ZaviQ7/ambient-mixer.git
cd ambient-mixer
```

2. Install required packages:
```bash
pip install pygame
```

3. Download ambient sound files and place them in the `sounds` directory with the following names:
- rain.mp3
- coffee_shop.mp3
- white_noise.mp3
- forest.mp3
- ocean.mp3

## Project Structure
```
ambient_mixer/
├── src/
│   ├── ambient_mixer_enhanced.py
│   └── presets.json
└── sounds/
    ├── rain.mp3
    ├── coffee_shop.mp3
    ├── white_noise.mp3
    ├── forest.mp3
    └── ocean.mp3
```

## Usage

1. Run the application:
```bash
python src/ambient_mixer_enhanced.py
```

2. Use the interface to:
   - Play/stop individual sounds
   - Adjust volume levels
   - Modify audio effects
   - Save and load presets

## Sound Files

You can download free ambient sounds from:
- [Freesound.org](https://freesound.org)
- [Mixkit.co](https://mixkit.co)
- [Free-stock-music.com](https://free-stock-music.com)

Remember to rename the downloaded files to match the required filenames.

## Author
- **Zavi Quintero** - [ZaviQ7](https://github.com/ZaviQ7)





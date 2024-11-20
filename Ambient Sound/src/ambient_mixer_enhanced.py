import tkinter as tk
from tkinter import ttk, messagebox
import pygame.mixer
import json
import os
from datetime import datetime
from typing import Dict, Optional, List
from dataclasses import dataclass
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

@dataclass
class Sound:
    filename: str
    volume: float = 1.0
    channel: Optional[pygame.mixer.Channel] = None
    is_playing: bool = False
    effects: dict = None
    button: Optional[ttk.Button] = None

    def __post_init__(self):
        if self.effects is None:
            self.effects = {
                "reverb": 0.0,
                "eq_low": 1.0,
                "eq_mid": 1.0,
                "eq_high": 1.0
            }

@dataclass
class Preset:
    name: str
    settings: dict
    category: str
    tags: List[str]
    created_at: str

class AmbientSoundMixer:
    def __init__(self):
        # Initialize the main window
        self.root = tk.Tk()
        self.root.title("Ambient Sound Mixer")
        self.root.geometry("800x600")
        
        # Initialize pygame mixer
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
        
        # Configure sounds
        self.sounds: Dict[str, Sound] = self.initialize_sounds()
        
        # Load sound files
        self.load_sounds()
        
        # Create and load presets
        self.presets: Dict[str, Preset] = self.load_presets()
        
        # Setup UI
        self.setup_ui()

    def initialize_sounds(self) -> Dict[str, Sound]:
        sounds_dir = Path("sounds")
        return {
            "Rain": Sound(str(sounds_dir / "rain.mp3")),
            "Coffee Shop": Sound(str(sounds_dir / "coffee_shop.mp3")),
            "White Noise": Sound(str(sounds_dir / "white_noise.mp3")),
            "Forest": Sound(str(sounds_dir / "forest.mp3")),
            "Ocean": Sound(str(sounds_dir / "ocean.mp3"))
        }

    def load_sounds(self):
        """Load sound files into pygame mixer with error handling"""
        for sound_name, sound in self.sounds.items():
            if not os.path.exists(sound.filename):
                messagebox.showwarning(
                    "File Missing",
                    f"Sound file not found: {sound.filename}"
                )
                continue
            try:
                pygame.mixer.Sound(sound.filename)
            except pygame.error as e:
                messagebox.showerror(
                    "Loading Error",
                    f"Error loading {sound_name}: {str(e)}"
                )

    def setup_ui(self):
        """Create the user interface"""
        # Create main container with notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(expand=True, fill='both', padx=10, pady=5)

        # Main mixer tab
        mixer_frame = ttk.Frame(self.notebook)
        self.notebook.add(mixer_frame, text='Mixer')

        # Effects tab
        effects_frame = ttk.Frame(self.notebook)
        self.notebook.add(effects_frame, text='Effects')

        # Create controls in mixer tab
        self.create_sound_controls(mixer_frame)
        self.create_preset_controls(mixer_frame)

        # Create effects controls
        self.create_effects_controls(effects_frame)

    def create_sound_controls(self, parent):
        """Create controls for each sound"""
        controls_frame = ttk.LabelFrame(parent, text="Sound Controls", padding=10)
        controls_frame.pack(fill='x', padx=5, pady=5)

        for idx, (sound_name, sound) in enumerate(self.sounds.items()):
            frame = ttk.Frame(controls_frame)
            frame.pack(fill='x', pady=2)

            # Label
            ttk.Label(frame, text=sound_name, width=15).pack(side='left', padx=5)

            # Volume slider
            volume_var = tk.DoubleVar(value=sound.volume * 100)
            volume_slider = ttk.Scale(
                frame,
                from_=0,
                to=100,
                orient=tk.HORIZONTAL,
                variable=volume_var,
                command=lambda v, name=sound_name: self.on_volume_change(name, float(v))
            )
            volume_slider.pack(side='left', fill='x', expand=True, padx=5)

            # Play/Stop button
            btn = ttk.Button(
                frame,
                text="Play",
                width=10,
                command=lambda name=sound_name: self.toggle_sound(name)
            )
            btn.pack(side='left', padx=5)
            sound.button = btn

    def create_effects_controls(self, parent):
        """Create controls for audio effects"""
        for sound_name, sound in self.sounds.items():
            frame = ttk.LabelFrame(parent, text=f"Effects: {sound_name}", padding=10)
            frame.pack(fill='x', padx=5, pady=5)

            # Reverb control
            ttk.Label(frame, text="Reverb:").grid(row=0, column=0, padx=5)
            reverb_var = tk.DoubleVar(value=sound.effects["reverb"])
            reverb_slider = ttk.Scale(
                frame,
                from_=0,
                to=1,
                orient=tk.HORIZONTAL,
                variable=reverb_var,
                command=lambda v, name=sound_name: self.update_effect(name, "reverb", float(v))
            )
            reverb_slider.grid(row=0, column=1, sticky='ew', padx=5)

            # EQ controls
            eq_labels = ["Low", "Mid", "High"]
            eq_params = ["eq_low", "eq_mid", "eq_high"]
            
            for i, (label, param) in enumerate(zip(eq_labels, eq_params)):
                ttk.Label(frame, text=f"{label}:").grid(row=i+1, column=0, padx=5)
                eq_var = tk.DoubleVar(value=sound.effects[param])
                eq_slider = ttk.Scale(
                    frame,
                    from_=0,
                    to=2,
                    orient=tk.HORIZONTAL,
                    variable=eq_var,
                    command=lambda v, name=sound_name, p=param: self.update_effect(name, p, float(v))
                )
                eq_slider.grid(row=i+1, column=1, sticky='ew', padx=5)

            frame.columnconfigure(1, weight=1)

    def create_preset_controls(self, parent):
        """Create preset controls"""
        preset_frame = ttk.LabelFrame(parent, text="Presets", padding=10)
        preset_frame.pack(fill='x', padx=5, pady=5)

        # Preset name and category
        entry_frame = ttk.Frame(preset_frame)
        entry_frame.pack(fill='x', pady=5)

        ttk.Label(entry_frame, text="Name:").pack(side='left', padx=5)
        self.preset_name_var = tk.StringVar()
        ttk.Entry(entry_frame, textvariable=self.preset_name_var).pack(side='left', padx=5)

        ttk.Label(entry_frame, text="Category:").pack(side='left', padx=5)
        self.category_var = tk.StringVar()
        ttk.Entry(entry_frame, textvariable=self.category_var).pack(side='left', padx=5)

        # Tags
        tags_frame = ttk.Frame(preset_frame)
        tags_frame.pack(fill='x', pady=5)
        
        ttk.Label(tags_frame, text="Tags:").pack(side='left', padx=5)
        self.tags_var = tk.StringVar()
        ttk.Entry(tags_frame, textvariable=self.tags_var).pack(side='left', padx=5)
        ttk.Label(tags_frame, text="(comma-separated)").pack(side='left', padx=5)

        # Buttons
        button_frame = ttk.Frame(preset_frame)
        button_frame.pack(fill='x', pady=5)

        ttk.Button(
            button_frame,
            text="Save Preset",
            command=self.save_preset
        ).pack(side='left', padx=5)

        self.preset_var = tk.StringVar()
        self.preset_combo = ttk.Combobox(
            button_frame,
            textvariable=self.preset_var,
            values=list(self.presets.keys())
        )
        self.preset_combo.pack(side='left', padx=5)

        ttk.Button(
            button_frame,
            text="Load Preset",
            command=self.load_preset
        ).pack(side='left', padx=5)

    def toggle_sound(self, sound_name: str):
        """Toggle sound playback"""
        sound = self.sounds[sound_name]
        if sound.is_playing:
            self.stop_sound(sound_name)
        else:
            self.play_sound(sound_name)

    def play_sound(self, sound_name: str):
        """Play a sound"""
        try:
            sound = self.sounds[sound_name]
            sound_obj = pygame.mixer.Sound(sound.filename)
            channel = pygame.mixer.find_channel()
            
            if channel is None:
                messagebox.showwarning("Warning", "No available audio channels")
                return
                
            channel.play(sound_obj, loops=-1)
            channel.set_volume(sound.volume)
            
            sound.channel = channel
            sound.is_playing = True
            sound.button.configure(text="Stop")
            
        except Exception as e:
            messagebox.showerror("Playback Error", f"Error playing {sound_name}: {str(e)}")

    def stop_sound(self, sound_name: str):
        """Stop a sound"""
        try:
            sound = self.sounds[sound_name]
            if sound.channel:
                sound.channel.stop()
            sound.is_playing = False
            sound.button.configure(text="Play")
            
        except Exception as e:
            logger.error(f"Error stopping {sound_name}: {e}")

    def update_effect(self, sound_name: str, effect: str, value: float):
        """Update effect settings for a sound"""
        sound = self.sounds[sound_name]
        sound.effects[effect] = value
        
        if sound.is_playing:
            # Restart the sound to apply new effects
            self.stop_sound(sound_name)
            self.play_sound(sound_name)

    def on_volume_change(self, sound_name: str, value: float):
        """Handle volume change for a sound"""
        sound = self.sounds[sound_name]
        sound.volume = value / 100
        if sound.channel:
            sound.channel.set_volume(sound.volume)

    def save_preset(self):
        """Save preset"""
        name = self.preset_name_var.get()
        if not name:
            messagebox.showwarning("Warning", "Please enter a preset name")
            return

        preset_data = {
            sound_name: {
                "volume": sound.volume,
                "is_playing": sound.is_playing,
                "effects": sound.effects.copy()
            }
            for sound_name, sound in self.sounds.items()
        }

        tags = [tag.strip() for tag in self.tags_var.get().split(',') if tag.strip()]
        
        self.presets[name] = Preset(
            name=name,
            settings=preset_data,
            category=self.category_var.get(),
            tags=tags,
            created_at=datetime.now().isoformat()
        )

        self.save_presets_to_file()
        self.update_preset_list()
        messagebox.showinfo("Success", f"Preset '{name}' saved successfully")

    def load_preset(self):
        """Load preset"""
        preset_name = self.preset_var.get()
        if not preset_name or preset_name not in self.presets:
            return

        preset = self.presets[preset_name]
        
        for sound_name, settings in preset.settings.items():
            if sound_name in self.sounds:
                sound = self.sounds[sound_name]
                sound.volume = settings["volume"]
                sound.effects = settings["effects"].copy()
                
                if settings["is_playing"]:
                    self.play_sound(sound_name)
                else:
                    self.stop_sound(sound_name)

    def load_presets(self) -> Dict[str, Preset]:
        """Load presets from file"""
        try:
            with open("presets.json", "r") as f:
                data = json.load(f)
                return {
                    name: Preset(**preset_data)
                    for name, preset_data in data.items()
                }
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def save_presets_to_file(self):
        """Save presets to file"""
        with open("presets.json", "w") as f:
            json.dump(
                {name: preset.__dict__ for name, preset in self.presets.items()},
                f,
                indent=2
            )

    def update_preset_list(self):
        """Update the preset selection dropdown"""
        self.preset_combo['values'] = list(self.presets.keys())

    def run(self):
        """Start the application"""
        self.root.mainloop()

if __name__ == "__main__":
    app = AmbientSoundMixer()
    app.run()
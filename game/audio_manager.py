"""Carga y reproducción de la música y los efectos de sonido."""

from pathlib import Path

import pygame

from game.settings import (
    DEFAULT_AUDIO_VOLUME,
    MUSIC_VOLUME_MULTIPLIER,
)


# Los nombres permiten solicitar un sonido sin depender de su archivo concreto.
SOUND_FILES = {
    "enemy_hit": "enemy_hit.wav",
    "enemy_defeat": "enemy_defeat.wav",
    "player_damage": "player_damage.wav",
    "wave_start": "wave_start.wav",
    "power_up_ready": "power_up_ready.wav",
    "power_up_activate": "power_up_activate.wav",
    "game_start": "game_start.wav",
    "game_over": "game_over.wav",
    "menu_adjust": "menu_adjust.wav",
}

# Cada efecto conserva su intensidad relativa al volumen general.
SOUND_VOLUME_MULTIPLIERS = {
    "enemy_hit": 0.55,
    "enemy_defeat": 0.70,
    "player_damage": 0.85,
    "wave_start": 0.70,
    "power_up_ready": 0.70,
    "power_up_activate": 0.80,
    "game_start": 0.65,
    "game_over": 0.75,
    "menu_adjust": 0.55,
}


class AudioManager:
    """Centraliza el audio y permite que el juego funcione sin sonido."""

    def __init__(self, sounds_directory: Path | None = None) -> None:
        """Prepara Pygame Mixer y carga los recursos disponibles."""

        project_root = Path(__file__).resolve().parent.parent
        self.sounds_directory = (
            sounds_directory
            if sounds_directory is not None
            else project_root / "assets" / "sounds"
        )
        self.volume = DEFAULT_AUDIO_VOLUME
        self.muted = False
        self.is_available = False
        self.sounds: dict[str, pygame.mixer.Sound] = {}

        try:
            # Algunos sistemas no inicializan Mixer al ejecutar pygame.init().
            if pygame.mixer.get_init() is None:
                pygame.mixer.init()

            self._load_sound_effects()
            self.is_available = True
            self._apply_volume()
        except (pygame.error, OSError):
            # La ausencia de un dispositivo de audio no debe cerrar el juego.
            self.sounds.clear()
            self.is_available = False

    def _load_sound_effects(self) -> None:
        """Carga los efectos que existen en la carpeta de recursos."""

        for sound_name, file_name in SOUND_FILES.items():
            sound_path = self.sounds_directory / file_name

            if sound_path.is_file():
                self.sounds[sound_name] = pygame.mixer.Sound(str(sound_path))

    def start_music(self) -> None:
        """Inicia la música ambiental en bucle si está disponible."""

        if not self.is_available:
            return

        music_path = self.sounds_directory / "music_loop.wav"

        if not music_path.is_file():
            return

        try:
            pygame.mixer.music.load(str(music_path))
            pygame.mixer.music.set_volume(self._music_volume)
            pygame.mixer.music.play(loops=-1, fade_ms=800)
        except (pygame.error, OSError):
            # Un archivo musical ausente o incompatible no afecta a la partida.
            return

    def play(self, sound_name: str) -> None:
        """Reproduce un efecto conocido cuando el audio está disponible."""

        if not self.is_available or self.muted:
            return

        sound = self.sounds.get(sound_name)

        if sound is not None:
            sound.play()

    def change_volume(self, amount: float) -> None:
        """Modifica el volumen general y lo mantiene entre cero y uno."""

        self.volume = min(1.0, max(0.0, self.volume + amount))

        # Mover el control de volumen recupera el sonido si estaba silenciado.
        self.muted = False
        self._apply_volume()

    def toggle_mute(self) -> None:
        """Activa o desactiva el silencio conservando el volumen elegido."""

        self.muted = not self.muted
        self._apply_volume()

    def _apply_volume(self) -> None:
        """Aplica el volumen general a la música y a todos los efectos."""

        if not self.is_available:
            return

        master_volume = 0.0 if self.muted else self.volume

        for sound_name, sound in self.sounds.items():
            relative_volume = SOUND_VOLUME_MULTIPLIERS.get(sound_name, 1.0)
            sound.set_volume(master_volume * relative_volume)

        pygame.mixer.music.set_volume(self._music_volume)

    @property
    def _music_volume(self) -> float:
        """Devuelve el volumen musical después de aplicar silencio y mezcla."""

        if self.muted:
            return 0.0
        return self.volume * MUSIC_VOLUME_MULTIPLIER

"""Estadísticas de mecanografía de una partida."""


class TypingStats:
    """Registra velocidad, precisión y errores del jugador."""

    def __init__(self) -> None:
        """Prepara una sesión sin pulsaciones ni tiempo acumulado."""

        self.total_characters = 0
        self.correct_characters = 0
        self.elapsed_seconds = 0.0
        self.is_active = False

    def update(self, delta_time: float) -> None:
        """Acumula tiempo únicamente después de empezar a escribir."""

        if self.is_active:
            self.elapsed_seconds += delta_time

    def register_character(
        self,
        typed_character: str,
        expected_character: str,
    ) -> None:
        """Registra un carácter y comprueba si coincide con el objetivo."""

        # La primera pulsación marca el inicio real de la medición.
        self.is_active = True
        self.total_characters += 1

        if typed_character == expected_character:
            self.correct_characters += 1

    @property
    def errors(self) -> int:
        """Devuelve el número de caracteres escritos incorrectamente."""

        return self.total_characters - self.correct_characters

    @property
    def accuracy(self) -> float:
        """Calcula el porcentaje de caracteres correctos."""

        if self.total_characters == 0:
            return 100.0

        return self.correct_characters / self.total_characters * 100

    @property
    def words_per_minute(self) -> float:
        """Calcula las PPM usando el estándar de cinco caracteres."""

        if self.elapsed_seconds <= 0:
            return 0.0

        typed_words = self.correct_characters / 5
        elapsed_minutes = self.elapsed_seconds / 60
        return typed_words / elapsed_minutes

    def reset(self) -> None:
        """Restablece todos los valores para una partida nueva."""

        self.total_characters = 0
        self.correct_characters = 0
        self.elapsed_seconds = 0.0
        self.is_active = False

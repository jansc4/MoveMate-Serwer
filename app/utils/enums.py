from enum import Enum

class ExerciseType(str, Enum):
    strength = "strength"
    cardio = "cardio"
    flexibility = "flexibility"
    balance = "balance"

class Difficulty(str, Enum):
    easy = "easy"
    medium = "medium"
    hard = "hard"
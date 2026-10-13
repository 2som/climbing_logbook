from enum import StrEnum


class ExerciseUnitEnum(StrEnum):
    KG = "kg"
    SECONDS = "seconds"
    MM = "mm"
    COUNT = "count"


class SessionTypeEnum(StrEnum):
    OPEN = "OPEN"
    STRENGTH_POWER = "STRENGTH_POWER"
    PROJECT = "PROJECT"
    GYM = "GYM"
    ENDURANCE = "ENDURANCE"

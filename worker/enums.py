from enum import Enum


class VacancyModality(str, Enum):
    PRESENCIAL = "presencial"
    HIBRIDO = "hibrido"
    REMOTO_COLOMBIA = "remoto_colombia"
    REMOTO_INTERNACIONAL = "remoto_internacional"
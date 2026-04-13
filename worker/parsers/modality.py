from enums import VacancyModality


def parse_modality(modality_raw: str) -> VacancyModality:
    text = modality_raw.lower().strip()
    if "remoto" in text or "remote" in text:
        return VacancyModality.REMOTO_COLOMBIA
    if "hibrido" in text or "híbrido" in text or "presencial y remoto" in text:
        return VacancyModality.HIBRIDO
    return VacancyModality.PRESENCIAL
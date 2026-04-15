import spacy
from core.logger import log

_nlp = None


def _get_nlp():
    global _nlp
    if _nlp is None:
        _nlp = spacy.load("es_core_news_md")
        log("[ranking] modelo spaCy cargado")
    return _nlp


def score_semantic(cv_text: str, description: str) -> float:
    if not cv_text or not description:
        return 0.0

    nlp = _get_nlp()
    cv_doc = nlp(cv_text[:10000])
    desc_doc = nlp(description[:10000])

    if not cv_doc.has_vector or not desc_doc.has_vector:
        return 0.0

    similarity = cv_doc.similarity(desc_doc)
    return round(float(similarity), 4)
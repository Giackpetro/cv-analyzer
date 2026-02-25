import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Lista "nota" di skill da cercare negli annunci (puoi ampliarla quando vuoi)
# Nota: metti le skill multi-parola prima di quelle singole quando hanno overlap.
KNOWN_SKILLS = [
    "python", "java", "c", "c++", "c#",
    "javascript", "typescript",
    "html", "css",
    "sql", "mysql", "postgresql", "sqlite",
    "git", "github", "gitlab",
    "flask", "django", "fastapi",
    "rest api",  # prima di rest e api
    "api",
    "rest",
    "docker", "kubernetes",
    "linux", "windows",
    "pandas", "numpy", "scikit learn",
    "machine learning", "data analysis",
    "aws", "azure", "gcp",
    "jira", "scrum", "agile",
]

SYNONYMS = {
    "js": "javascript",
    "py": "python",
    "postgres": "postgresql",
    "sklearn": "scikit learn",
}

def normalize(text: str) -> str:
    text = text.lower()
    # tiene anche + e # per c++ / c#
    text = re.sub(r"[^a-z0-9#+]+", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    words = [SYNONYMS.get(w, w) for w in text.split()]
    return " ".join(words)

def remove_overlaps(required: list[str]) -> list[str]:
    """
    Se è presente una skill multi-parola (es. 'rest api'),
    rimuove le skill singole che la compongono (es. 'rest', 'api').
    """
    norm_required = [normalize(s) for s in required]
    multi = [s for s in norm_required if " " in s]

    words_in_multi = set()
    for m in multi:
        for w in m.split():
            words_in_multi.add(w)

    filtered = []
    for orig, n in zip(required, norm_required):
        if " " in n:
            filtered.append((n, orig))
        else:
            if n not in words_in_multi:
                filtered.append((n, orig))

    seen = set()
    out = []
    for n, orig in filtered:
        if n not in seen:
            seen.add(n)
            out.append(orig)
    return out

def find_required_skills(job_text: str) -> list[str]:
    job_norm = normalize(job_text)
    tokens = set(job_norm.split())
    required = []

    for skill in KNOWN_SKILLS:
        s_norm = normalize(skill)

        if " " in s_norm:
            if s_norm in job_norm:
                required.append(skill)
        else:
            if s_norm in tokens:
                required.append(skill)

    # dedup preservando ordine
    seen = set()
    out = []
    for s in required:
        key = normalize(s)
        if key not in seen:
            seen.add(key)
            out.append(s)

    # rimuovi overlap (rest api -> elimina rest + api se presenti)
    out = remove_overlaps(out)
    return out

def split_sections(job_text: str):
    """
    Prova a separare la parte 'Requisiti' dalla parte 'Nice to have'.
    Se non trova, ritorna stringhe vuote e poi useremo fallback.
    """
    text = job_text.lower()

    req_keywords = ["requisiti", "requirements", "must have", "must-have", "obbligatori", "required"]
    nice_keywords = ["nice to have", "nice-to-have", "gradito", "preferibile", "plus", "opzionale"]

    req_text = ""
    nice_text = ""

    # Prendiamo la parte dopo la keyword trovata
    for k in req_keywords:
        if k in text:
            req_text = text.split(k, 1)[1]
            break

    for k in nice_keywords:
        if k in text:
            nice_text = text.split(k, 1)[1]
            break

    return req_text, nice_text

def analyze(cv_text: str, job_text: str, user_skills: list[str]):
    # --- TF-IDF similarity (0-100) ---
    vectorizer = TfidfVectorizer(stop_words=None)
    tfidf_matrix = vectorizer.fit_transform([cv_text, job_text])
    sim = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])
    tfidf_score = float(sim[0][0]) * 100

    # --- Sezioni: requisiti / nice to have ---
    req_text, nice_text = split_sections(job_text)

    req_skills = find_required_skills(req_text) if req_text else []
    nice_skills = find_required_skills(nice_text) if nice_text else []

    # fallback: se non troviamo sezioni, estraiamo dal testo intero
    if not req_skills and not nice_skills:
        req_skills = find_required_skills(job_text)
        nice_skills = []

    # lista totale skill richieste (solo per mostrarle nella UI)
    required_skills = list(dict.fromkeys(req_skills + nice_skills))

    # --- Matching con pesi ---
    user_norm = {normalize(s) for s in user_skills}

    matching = []
    missing = []

    weighted_total = 0
    weighted_match = 0

    # Requisiti: peso 2
    for s in req_skills:
        weighted_total += 2
        if normalize(s) in user_norm:
            matching.append(s)
            weighted_match += 2
        else:
            missing.append(s)

    # Nice to have: peso 1
    for s in nice_skills:
        weighted_total += 1
        if normalize(s) in user_norm:
            matching.append(s)
            weighted_match += 1
        else:
            missing.append(s)

    # percentuale skill pesata
    if weighted_total > 0:
        skill_score = (weighted_match / weighted_total) * 100
    else:
        skill_score = 0.0

    # --- Score finale ---
    # Se abbiamo skill (req/nice), usiamo 70/30. Altrimenti solo TF-IDF.
    if weighted_total > 0:
        final_score = 0.70 * skill_score + 0.30 * tfidf_score
    else:
        final_score = tfidf_score

    # ✅ FIX: rimuove duplicati preservando ordine
    matching = list(dict.fromkeys(matching))
    missing = list(dict.fromkeys(missing))

    return (
        round(final_score, 2),
        matching,
        missing,
        round(tfidf_score, 2),
        round(skill_score, 2),
        required_skills,
    )
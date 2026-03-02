from ai_analyzer import analyze

def main():
    print("=== CV Analyzer (Terminale) ===")
    print("Incolla il testo e premi INVIO. Per chiudere: riga vuota.\n")

    print("Inserisci CV (puoi incollare più righe):")
    cv_lines = []
    while True:
        line = input()
        if line.strip() == "":
            break
        cv_lines.append(line)
    cv_text = "\n".join(cv_lines).strip()

    print("\nInserisci ANNUNCIO (puoi incollare più righe):")
    job_lines = []
    while True:
        line = input()
        if line.strip() == "":
            break
        job_lines.append(line)
    job_text = "\n".join(job_lines).strip()

    # skill opzionali: se vuoi puoi inserirle separate da virgola
    raw = input("\nInserisci le tue skill (separate da virgola) oppure lascia vuoto: ").strip()
    user_skills = [s.strip() for s in raw.split(",") if s.strip()] if raw else []

    final_score, matching, missing, tfidf_score, skill_score, required_skills, cv_found_skills = analyze(
    cv_text, job_text, user_skills
    )

    print("\nSkill trovate automaticamente nel CV:")
    if cv_found_skills:
        for s in cv_found_skills:
            print(f"- {s}")
    else:
        print("- Nessuna")

    print("\n=== RISULTATO ===")
    print(f"Compatibilità finale: {final_score}%")
    print(f"Dettaglio -> Skill: {skill_score}% | Contesto: {tfidf_score}%")

    print("\nSkill richieste (dall'annuncio):")
    for s in required_skills:
        print("-", s)

    print("\nSkill trovate:")
    if matching:
        for s in matching:
            print("✅", s)
    else:
        print("Nessuna")

    print("\nSkill mancanti:")
    if missing:
        for s in missing:
            print("❌", s)
    else:
        print("Nessuna")

if __name__ == "__main__":
    main()
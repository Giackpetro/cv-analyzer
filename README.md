# CV Analyzer

CV Analyzer è una web app sviluppata in Python che permette di confrontare il proprio CV con un annuncio di lavoro per stimare il livello di compatibilità e individuare competenze mancanti.

## 🎯 Obiettivo
L’obiettivo del progetto è simulare il funzionamento di un ATS (Applicant Tracking System), ovvero i sistemi utilizzati dalle aziende per filtrare e valutare i CV rispetto a una posizione lavorativa.

## ⚙️ Tecnologie utilizzate
- Python
- Flask (framework web)
- SQLite (database)
- NLP (Natural Language Processing)
- TF-IDF + Cosine Similarity (analisi testo)

## 🚀 Funzionalità
- Inserimento e gestione delle competenze dell’utente
- Inserimento di una job description
- Estrazione automatica delle skill richieste dall’annuncio
- Confronto tra CV e annuncio
- Calcolo percentuale di compatibilità
- Identificazione skill presenti e mancanti
- Distinzione tra requisiti obbligatori e nice to have con pesi diversi

## 🧠 Funzionamento
Il sistema utilizza tecniche di NLP per trasformare i testi in vettori numerici tramite TF-IDF. Successivamente viene calcolata la similarità tra CV e job description mediante cosine similarity. Il punteggio finale combina:
- percentuale di skill trovate
- similarità semantica del testo

## 📂 Struttura progetto

cv_analyzer/
│
├── app.py
├── models.py
├── ai_analyzer.py
├── templates/
├── static/
├── instance/
└── requirements.txt



## ▶️ Avvio progetto
1. Clonare il repository
2. Creare ambiente virtuale
3. Installare dipendenze
4. Avviare Flask

```bash
python app.py

http://127.0.0.1:5000
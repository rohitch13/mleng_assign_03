# Headline Scoring Web Service and Streamlit UI

## Overview

This project implements a headline sentiment scoring system with two components:

- **FastAPI backend** (`score_headlines_api.py`): Accepts a list of headlines and returns sentiment classification using a pre-trained SVM model and sentence embeddings.
- **Streamlit frontend** (`streamlit_app.py`): User interface to input headlines manually or upload `.txt` files, edit or delete headlines, and display scoring results from the backend service.

---

## API Endpoint (Must run this separately from mleng_assign_02 folder)

```bash
uvicorn score_headlines_api:app --host 0.0.0.0 --port 8011
```

## Stream app run

```bash
streamlit run streamlit_app.py --server.port 9011
```


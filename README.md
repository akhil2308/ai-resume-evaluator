# AI Resume Evaluator 🚀

An intelligent resume evaluating system that automates candidate evaluation using AI-powered criteria extraction and scoring.

[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=flat&logo=fastapi)](https://fastapi.tiangolo.com/)
[![OpenAI](https://img.shields.io/badge/OpenAI-412991?style=flat&logo=openai)](https://openai.com/)

## Features ✨

- **Smart JD Processing**: Extracts key criteria from job descriptions
- **AI-Powered Scoring**: Evaluates resumes against extracted criteria
- **Multi-Format Support**: Process PDF and DOCX files
- **Markdown Conversion**: Optimal format for AI analysis
- **Batch Processing**: Score multiple resumes in single request
- **Flexible Output**: JSON or Excel download options

## Installation 💻

1. **Clone Repository**
```bash
git clone https://github.com/yourusername/ai-resume-evaluator.git
cd ai-resume-evaluator
```

2. **Set Up Environment**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate  # Windows
```

3. **Install Dependencies**
```bash
pip install -r requirements.txt
```

### Running the Application

- **Local / Development:**

  Make sure to load your environment variables:

  ```bash
  source set_env.sh
  python main.py
  ```

- **Production:**

  Use the provided `run.sh` script (which runs Gunicorn + Uvicorn):

  ```bash
  ./run.sh
  ```

---

## API Documentation

Interactive API documentation is also available once the server is running:

- **Swagger UI:** [http://localhost:8000/docs](http://localhost:8000/docs)
- **Redoc:** [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

### API Endpoints

#### 1. Extract Criteria 🔍
**Endpoint**: `POST /v1/api/extract-criteria`

```bash
curl --location 'http://localhost:8000/v1/api/extract-criteria' \
--header 'Content-Type: multipart/form-data' \
--form 'file=@job_description.pdf'
```

**Response**:
```json
{
    "criteria": [
        "2-3+ years experience in Python",
        "AWS Certification",
        "Machine Learning expertise"
    ]
}
```

#### 2. Score Resumes 📊
**Endpoint**: `POST /v1/api/score-resumes`

```bash
curl --location 'http://localhost:8000/v1/api/score-resumes' \
--header 'Content-Type: multipart/form-data' \
--form 'files=@resume1.pdf' \
--form 'files=@resume2.docx' \
--form 'criteria="[\"Python experience\", \"Cloud certifications\"]"' \
--form 'download="false"'
```

**Response**:
```json
{
    "result": [
        {
            "Candidate Name": "John Doe",
            "Python Experience": 4,
            "Cloud Certifications": 5,
            "Total Score": 9
        }
    ]
}
```

## Project Structure 🗂️

```
.
├── app
│   ├── health
│   │   └── health_router.py
│   ├── resume_evaluator
│   │   ├── resume_evaluator_config.py
│   │   ├── resume_evaluator_router.py
│   │   └── resume_evaluator_service.py
│   ├── utils
│   │   └── helper.py
│   └── settings.py
├── temp
├── CONTRIBUTORS.txt
├── Dockerfile
├── LICENSE
├── README.md
├── gunicorn_conf.py
├── main.py
├── requirements.txt
├── run.sh
├── set_env.sh

6 directories, 15 files
```

## Dependencies 📦

| Package | Purpose |
|---------|---------|
| FastAPI | API framework |
| PyMuPDF | PDF processing |
| Mammoth | DOCX conversion |
| OpenAI | AI model integration |
| Pandas | Excel export |


See [CONTRIBUTORS.txt](./CONTRIBUTORS.txt) for contribution guidelines.

## License 📄

This project is licensed under the MIT License - see [LICENSE](./LICENSE) file for details.

---
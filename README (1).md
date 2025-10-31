# 🎯 Interview Preparation Chatbot (Flask + Google Generative AI)

An AI-powered **Interview Preparation Chatbot API** built using **Flask** and integrated with **Google Generative AI (Gemini)**.  
The API simulates real interview sessions, evaluates candidate answers, and provides structured feedback to help users improve their performance.

---

## 🚀 Features

- 🧠 Generates adaptive HR and technical interview questions.
- 💬 Analyzes candidate answers and gives AI-driven feedback.
- 📊 Provides structured output: strengths, gaps, suggestions, score, and rationale.
- ⚙️ Easy to integrate with any frontend chatbot interface.
- 🐳 Containerized using **Docker** for easy deployment.
- 🌐 RESTful API built with **Flask** and **Gunicorn** for scalable performance.

---

## 🧩 Tech Stack

**Backend:** Flask, Python  
**AI Integration:** Google Generative AI (Gemini API)  
**Deployment:** Docker, Gunicorn  
**Utilities:** Flask-CORS, Pydantic, python-dotenv, Requests  
**Tools:** Postman, VS Code, GitHub

---

## 📁 Project Structure

```
interview-bot-api/
│
├── app.py                # Main Flask app and API endpoints
├── requirements.txt      # Python dependencies
├── Dockerfile            # Container configuration
├── .env.example          # Environment variable template
└── README.md             # Project documentation
```

---

## ⚙️ Setup Instructions

### 1. Clone the Repository

```
git clone https://github.com/yourusername/interview-bot-api.git
cd interview-bot-api
```

### 2. Create and Activate Virtual Environment

```
python -m venv venv
source venv/bin/activate   # (Mac/Linux)
venv\Scripts\activate    # (Windows)
```

### 3. Install Dependencies

```
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the root directory and add:

```
GEMINI_API_KEY=your_google_api_key
GEMINI_MODEL=gemini-1.5-flash-latest
PORT=8080
```

### 5. Run the App

```
python app.py
```

The API will start on:  
👉 **http://127.0.0.1:8080**

---

## 🧠 API Endpoints

### **GET /**

**Description:** Health check endpoint to verify the server is running.  
**Response:**

```
{"status": "ok"}
```

---

### **POST /interview**

**Description:** Accepts a question and candidate’s answer, returns structured AI feedback.  
**Request Example:**

```
{
  "question": "Explain the difference between supervised and unsupervised learning.",
  "answer": "Supervised learning uses labeled data..."
}
```

**Response Example:**

```
{
  "question": "...",
  "answer": "...",
  "model_used": "gemini-1.5-flash-latest",
  "feedback": {
    "strengths": [...],
    "gaps": [...],
    "suggestions": [...],
    "score": 8,
    "rationale": "..."
  }
}
```

---

## 🐳 Docker Deployment

### Build and Run

docker build -t interview-bot-api .
docker run -d -p 8080:8080 --env-file .env interview-bot-api

```

The app will be accessible at **http://localhost:8080**

---

## 📘 Future Enhancements

- Add user authentication and personalized interview tracking.
- Expand AI models for domain-specific interviews (Tech, HR, Finance, etc.).
- Build a frontend chatbot interface with Streamlit or React.
- Store response history using SQLite or Firebase.

---

## 🤝 Contributing

Contributions are welcome!
1. Fork the repository
2. Create a new branch
3. Commit your changes
4. Submit a pull request


---

 🪪 License

This project is licensed under the **MIT License** — feel free to use, modify, and distribute.


```

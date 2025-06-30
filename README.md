# Life360 FastAPI Wrapper

A minimal FastAPI app that exposes the Life360 API as a RESTful service. Easily retrieve your circles, members, and user info using simple HTTP endpoints.

---

## 🚀 Quickstart

### 1. Clone the Repository
```bash
git clone https://www.github.com/andrewcincotta/life360-fast-api.git
cd life360-fast-api
```

### 2. Create a Virtual Environment (Recommended)
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Requirements
```bash
pip install -r requirements.txt
```

### 4. Set Your Life360 Authorization Token
Obtain your Life360 Bearer token and set it as an environment variable:
```bash
export LIFE360_AUTHORIZATION="your_life360_bearer_token"
```

### 5. Run the App
```bash
python run.py
```

The API will be available at [http://localhost:8000](http://localhost:8000)

---

## 🔑 Access Token Instructions

To use this API, you need a Life360 access token. The easiest way to get one is:

1. Go to [life360.com/login](https://life360.com/login) and log in.
2. Open your browser's Developer Tools and go to the Network tab.
3. Log in and look for a network request named `token` (POST method, not preflight/OPTIONS).
4. In the response, find `token_type` (usually "Bearer") and `access_token`.
5. Use these values for authentication in this app.

*Note: Life360's SMS login flow is not supported by this method. Any value can be used for the "Account identifier" if prompted.*

---

## 📖 API Documentation

Interactive docs are available at:
- Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)
- ReDoc: [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

## 🛠️ Example Usage

**Get all circles:**
```bash
curl http://localhost:8000/circles
```

**Get members of a circle:**
```bash
curl http://localhost:8000/circles/<circle_id>/members
```

**Get your user info:**
```bash
curl http://localhost:8000/me
```

**Get specific member of a circle:**
```bash
curl http://localhost:8000/circles/<circle_id>/members/<member_id>
```
# YouTube Comment Sentiment Analyzer

## Overview
This project is a YouTube Comment Sentiment Analyzer that fetches comments from a given YouTube video and analyzes their sentiment using Natural Language Processing (NLP). It provides insights into the overall sentiment distribution and presents the analysis with visualizations.

## Features
- Extracts comments from a YouTube video using the YouTube Data API
- Analyzes sentiment using TextBlob
- Categorizes comments into positive, neutral, or negative sentiments
- Generates sentiment distribution visualizations
- Displays video metadata including title, channel, views, likes, and comment count

## Requirements
Ensure you have the following installed:
- Python 3.x
- Virtual environment (recommended)

## Setup Instructions

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/youtube-comment-sentiment-analyzer.git
cd youtube-comment-sentiment-analyzer
```

### 2. Create and Activate a Virtual Environment
```bash
# On Windows
python -m venv venv
venv\Scripts\activate

# On macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Get API Keys
This project requires API keys to function properly:
- **YouTube Data API Key**: Obtain it from [Google Cloud Console](https://console.cloud.google.com/)

After obtaining your API key, open `app.py` and replace `YOUR_YOUTUBE_API_KEY_HERE` with your actual API key:
```python
YOUTUBE_API_KEY = "YOUR_YOUTUBE_API_KEY_HERE"
```

### 5. Run the Application
```bash
python app.py
```
The app will run locally on `http://127.0.0.1:5000/`.

## Deployment
To deploy on a cloud platform or a hosting service:
- Ensure all dependencies are installed
- Set environment variables for API keys
- Use a production-ready web server (e.g., Gunicorn with Flask)

## License
This project is open-source and available under the MIT License.


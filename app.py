from flask import Flask, render_template_string, request, redirect, url_for, flash
import re
import os
import io
import base64
from datetime import datetime
from googleapiclient.discovery import build
from textblob import TextBlob
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

app = Flask(__name__)
app.secret_key = "Your_secret_Key"  # Replace with your secret key

# YouTube Data API setup: Replace with your actual API key.
YOUTUBE_API_KEY = "Your_secret_key"
youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)

# Category mapping for YouTube video categories
CATEGORY_MAPPING = {
    1: "Film & Animation",
    2: "Autos & Vehicles",
    10: "Music",
    15: "Pets & Animals",
    17: "Sports",
    18: "Short Movies",
    19: "Travel & Events",
    20: "Gaming",
    21: "Videoblogging",
    22: "People & Blogs",
    23: "Comedy",
    24: "Entertainment",
    25: "News & Politics",
    26: "Howto & Style",
    27: "Education",
    28: "Science & Technology",
    29: "Nonprofits & Activism",
    30: "Movies",
    31: "Anime/Animation",
    32: "Action/Adventure",
    33: "Classics",
    34: "Comedy",
    35: "Documentary",
    36: "Drama",
    37: "Family",
    38: "Foreign",
    39: "Horror",
    40: "Sci-Fi/Fantasy",
    41: "Thriller",
    42: "Shorts",
    43: "Shows",
    44: "Trailers",
}

# HTML template (using Bootstrap for responsiveness)
HTML_TEMPLATE = '''
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <title>YouTube Comment Analysis Tool</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <!-- Bootstrap CSS CDN -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <!-- Google Fonts for a modern look -->
    <link rel="stylesheet" href="https://fonts.googleapis.com/css?family=Roboto:400,700">
    <style>
      /* Increase top margin for container */
      .container {
        margin-top: 50px;
      }
      
      /* Heading styling: Only "Tube" in YouTube is red */
      h1 {
        font-family: 'Roboto', sans-serif;
        font-weight: 700;
        font-size: 2.5rem;
        text-align: center;
        margin-bottom: 20px;
        color: #000; /* Default black */
      }
      h1 span.red {
        color: #FF0000;
      }
      
      /* Adjust input textbox styling */
      input.form-control {
        width: 50%;              /* Make textbox smaller */
        transition: box-shadow 0.3s ease;
        margin-right: 10px;      /* Space between textbox and button */
        border-radius: 5px;      /* Slight rounding */
      }
      
      /* Button styling: match textbox rounding */
      .btn-primary {
        border-radius: 5px;      /* Slight rounding */
      }
      
      /* Blue glow on focus for the textbox */
      input.form-control:focus {
        outline: none;
        box-shadow: 0 0 5px 2px rgba(0, 123, 255, 0.5);
      }
    </style>
  </head>
  <body>
    <div class="container my-4">
      <h1>You<span class="red">Tube</span> Comment Analysis Tool</h1>
      <form method="POST" action="/" class="mb-4">
        <div class="input-group justify-content-center">
          <input type="text" class="form-control" name="video_url" placeholder="Enter YouTube video URL" required>
          <button class="btn btn-primary" type="submit">Analyze Comments</button>
        </div>
      </form>
      
      {% if error %}
      <div class="alert alert-danger">{{ error }}</div>
      {% endif %}
      
      {% if analysis %}
      <div class="row">
        <div class="col-md-6 summary-box">
          <h4>Video Summary</h4>
          <p><strong>Channel:</strong> {{ analysis.channel_title }}</p>
          <p><strong>Title:</strong> {{ analysis.video_title }}</p>
          <p><strong>Category:</strong> {{ analysis.category }}</p>
          <p><strong>Uploaded:</strong> {{ analysis.upload_date }}</p>
          <p><strong>Total Views:</strong> {{ analysis.view_count }}</p>
          <p><strong>Total Likes:</strong> {{ analysis.like_count }}</p>
          <p><strong>Total Comments:</strong> {{ analysis.comment_count }}</p>
        </div>
        <div class="col-md-6 top-comments">
          <h4>Top 3 Comments (by likes)</h4>
          <ul>
            {% for comment in analysis.top_comments %}
            <li>"{{ comment.text }}" - ({{ comment.like_count }} likes)</li>
            {% endfor %}
          </ul>
        </div>
      </div>
      
      <div class="visualization text-center">
        <h4>Sentiment Distribution</h4>
        <img src="data:image/png;base64,{{ analysis.chart }}" alt="Sentiment Chart" class="img-fluid">
        <p><strong>Chart Type:</strong> {{ analysis.chart_type }}</p>
      </div>
      
      <div class="text-center mb-5">
        <a href="{{ analysis.video_url }}" target="_blank" class="btn btn-secondary">Go to YouTube Video</a>
      </div>
      {% endif %}
    </div>
    
    <!-- Bootstrap JS CDN -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
  </body>
</html>
'''

def is_valid_youtube_url(url):
    # Basic regex check for YouTube URLs.
    youtube_regex = r"(https?://)?(www\.)?(youtube\.com|youtu\.?be)/.+"
    return re.match(youtube_regex, url)

def extract_video_id(url):
    # Handles common YouTube URL formats.
    regex_patterns = [
        r"(?:v=|\/)([0-9A-Za-z_-]{11}).*",  # v=VIDEO_ID or /VIDEO_ID
    ]
    for pattern in regex_patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None

def get_video_metadata(video_id):
    # Call YouTube API to get video details.
    request = youtube.videos().list(
        part="snippet,statistics,contentDetails",
        id=video_id
    )
    response = request.execute()
    if not response["items"]:
        return None
    item = response["items"][0]
    snippet = item["snippet"]
    statistics = item.get("statistics", {})
    # Format upload date
    upload_date = datetime.strptime(snippet["publishedAt"], "%Y-%m-%dT%H:%M:%SZ").strftime("%Y")
    # Map categoryId to human-readable category name
    category_id = snippet.get("categoryId", "N/A")
    category = CATEGORY_MAPPING.get(int(category_id), "Unknown Category")  # Use the mapping
    metadata = {
        "channel_title": snippet["channelTitle"],
        "video_title": snippet["title"],
        "category": category,  # Now this will be a human-readable name
        "upload_date": upload_date,
        "view_count": statistics.get("viewCount", "0"),
        "like_count": statistics.get("likeCount", "0"),
        "comment_count": statistics.get("commentCount", "0"),
        "video_url": f"https://youtu.be/{video_id}"
    }
    return metadata

def get_video_comments(video_id, max_results=50):
    comments = []
    request = youtube.commentThreads().list(
        part="snippet",
        videoId=video_id,
        textFormat="plainText",
        maxResults=100
    )
    response = request.execute()
    while response:
        for item in response.get("items", []):
            snippet = item["snippet"]["topLevelComment"]["snippet"]
            comments.append({
                "text": snippet["textDisplay"],
                "like_count": snippet.get("likeCount", 0)
            })
        if "nextPageToken" in response and len(comments) < max_results:
            request = youtube.commentThreads().list(
                part="snippet",
                videoId=video_id,
                textFormat="plainText",
                maxResults=100,
                pageToken=response["nextPageToken"]
            )
            response = request.execute()
        else:
            break
    return comments

def generate_sentiment_score(comment, category):
    # For demonstration, we use TextBlob to get a polarity score.
    # Based on the video's category, we could adjust the thresholds.
    blob = TextBlob(comment)
    polarity = blob.sentiment.polarity
    # Adjust thresholds based on category (dummy logic)
    if category == "27":  # Suppose "27" stands for "Education" (example)
        # More forgiving thresholds for educational content:
        if polarity > 0.1:
            return 5
        elif polarity > -0.1:
            return 3
        else:
            return 1
    else:
        # Default scale mapping:
        if polarity > 0.5:
            return 5
        elif polarity > 0.2:
            return 4
        elif polarity > -0.2:
            return 3
        elif polarity > -0.5:
            return 2
        else:
            return 1

def create_sentiment_chart(sentiment_scores):
    # Analyze the dataset to decide the best chart type
    df = pd.DataFrame(sentiment_scores, columns=["Score"])
    distribution = df["Score"].value_counts().sort_index()
    scores = distribution.index
    counts = distribution.values

    # Decision logic for chart type
    if len(scores) <= 3:  # Small dataset or few categories
        chart_type = "Pie Chart"
        plt.figure(figsize=(6, 6))
        plt.pie(counts, labels=[f"Score {int(k)}" for k in scores], autopct='%1.1f%%', startangle=140, colors=plt.cm.Paired.colors)
        plt.title("Sentiment Distribution (Pie Chart)")
    elif len(scores) <= 10:  # Medium dataset
        chart_type = "Bar Chart"
        plt.figure(figsize=(8, 6))
        bars = plt.bar(scores, counts, color=['#FF6B6B', '#FFD166', '#06D6A0', '#118AB2', '#073B4C'])
        plt.xlabel("Sentiment Score (1 = Negative, 5 = Positive)")
        plt.ylabel("Number of Comments")
        plt.title("Sentiment Distribution (Bar Chart)")
        plt.xticks(scores)
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width() / 2, height, f'{int(height)}', ha='center', va='bottom')
    else:  # Large dataset
        chart_type = "Histogram"
        plt.figure(figsize=(8, 6))
        plt.hist(sentiment_scores, bins=5, color='#118AB2', edgecolor='black')
        plt.xlabel("Sentiment Score (1 = Negative, 5 = Positive)")
        plt.ylabel("Number of Comments")
        plt.title("Sentiment Distribution (Histogram)")

    # Save to a bytes object and encode as base64.
    buf = io.BytesIO()
    plt.savefig(buf, format="png", bbox_inches="tight")
    plt.close()
    buf.seek(0)
    encoded = base64.b64encode(buf.read()).decode("utf-8")
    return encoded, chart_type

@app.route("/", methods=["GET", "POST"])
def index():
    analysis = None
    error = None
    if request.method == "POST":
        video_url = request.form.get("video_url")
        if not is_valid_youtube_url(video_url):
            error = "Please provide a valid YouTube video URL."
            return render_template_string(HTML_TEMPLATE, error=error)
        video_id = extract_video_id(video_url)
        if not video_id:
            error = "Could not extract video ID from URL."
            return render_template_string(HTML_TEMPLATE, error=error)
        
        metadata = get_video_metadata(video_id)
        if not metadata:
            error = "Video not found or unable to fetch metadata."
            return render_template_string(HTML_TEMPLATE, error=error)
        
        comments = get_video_comments(video_id, max_results=50)
        # If no comments, use empty list
        if not comments:
            error = "No comments available for this video."
            return render_template_string(HTML_TEMPLATE, error=error)
        
        # Use the video category (here, metadata['category']) to customize sentiment analysis.
        sentiment_scores = []
        for c in comments:
            score = generate_sentiment_score(c["text"], metadata["category"])
            sentiment_scores.append(score)
        
        chart, chart_type = create_sentiment_chart(sentiment_scores)
        
        # Get top 3 comments based on like count
        top_comments = sorted(comments, key=lambda x: x["like_count"], reverse=True)[:3]
        
        analysis = {
            "channel_title": metadata["channel_title"],
            "video_title": metadata["video_title"],
            "category": metadata["category"],
            "upload_date": metadata["upload_date"],
            "view_count": metadata["view_count"],
            "like_count": metadata["like_count"],
            "comment_count": metadata["comment_count"],
            "video_url": metadata["video_url"],
            "top_comments": top_comments,
            "chart": chart,
            "chart_type": chart_type
        }
    return render_template_string(HTML_TEMPLATE, analysis=analysis, error=error)

if __name__ == "__main__":
    # To run on all interfaces and use a proper port
    app.run(host="0.0.0.0", port=5000, debug=True)
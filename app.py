from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

SLACK_WEBHOOK_URL = os.environ.get("SLACK_WEBHOOK_URL")

@app.route("/", methods=["GET"])
def health_check():
    return "Running", 200

@app.route("/sprout-webhook", methods=["POST"])
def handle_sprout_post():
    data = request.json
    
    network = data.get("network", "Unknown")
    post_url = data.get("post_url", "")
    post_text = data.get("post_text", "")
    profile_name = data.get("profile_name", "")
    
    # Choose emoji based on network
    emoji_map = {
        "Twitter": "🐦",
        "X": "𝕏",
        "Instagram": "📸",
        "Facebook": "📘",
        "LinkedIn": "💼"
    }
    emoji = emoji_map.get(network, "📣")
    
    slack_message = {
        "blocks": [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"{emoji} New {network} Post",
                    "emoji": True
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Profile:* {profile_name}"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": post_text[:500] if post_text else "_No text content_"
                }
            },
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "View Post"
                        },
                        "url": post_url,
                        "style": "primary"
                    }
                ]
            },
            {
                "type": "divider"
            }
        ]
    }
    
    response = requests.post(SLACK_WEBHOOK_URL, json=slack_message)
    
    if response.status_code == 200:
        return jsonify({"status": "ok"}), 200
    else:
        return jsonify({"status": "error", "detail": response.text}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
```

Click **Commit changes**.

**File 2: `requirements.txt`**

Click **Add file** → **Create new file**, name it `requirements.txt`, and paste:
```
flask==3.0.0
requests==2.31.0
gunicorn==21.2.0
```

Click **Commit changes**.

**File 3: `Procfile`**

Click **Add file** → **Create new file**, name it `Procfile` (no extension), and paste:
```
web: gunicorn app:app

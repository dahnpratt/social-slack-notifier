import os
import json
import requests
from datetime import datetime, timedelta, timezone
from flask import Flask

app = Flask(__name__)

SPROUT_API_KEY = os.environ.get("SPROUT_API_KEY")
SPROUT_CUSTOMER_ID = os.environ.get("SPROUT_CUSTOMER_ID")
SLACK_WEBHOOK_URL = os.environ.get("SLACK_WEBHOOK_URL")
LAST_CHECK_FILE = "/tmp/last_check.json"

# SproutSocial API base URL
SPROUT_BASE_URL = "https://api.sproutsocial.com/v1"

def get_last_check_time():
    """Get the timestamp of our last check, default to 15 minutes ago."""
    try:
        with open(LAST_CHECK_FILE, "r") as f:
            data = json.load(f)
            return datetime.fromisoformat(data["last_check"])
    except (FileNotFoundError, KeyError, ValueError):
        return datetime.now(timezone.utc) - timedelta(minutes=15)

def save_last_check_time(timestamp):
    """Save the current check timestamp."""
    with open(LAST_CHECK_FILE, "w") as f:
        json.dump({"last_check": timestamp.isoformat()}, f)

def get_published_posts(since_time):
    """Fetch published posts from SproutSocial API."""
    headers = {
        "Authorization": f"Bearer {SPROUT_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # Adjust this endpoint based on SproutSocial's actual API documentation
    # This is a common pattern but verify with your API docs
    endpoint = f"{SPROUT_BASE_URL}/{SPROUT_CUSTOMER_ID}/posts/published"
    
    params = {
        "since": since_time.isoformat(),
        "limit": 50
    }
    
    response = requests.get(endpoint, headers=headers, params=params)
    
    if response.status_code == 200:
        return response.json().get("data", [])
    else:
        print(f"SproutSocial API error: {response.status_code} - {response.text}")
        return []

def send_slack_notification(post):
    """Send a formatted Slack message for a published post."""
    
    # Extract post data - adjust field names based on actual API response
    network = post.get("network_type", post.get("network", "Unknown"))
    post_url = post.get("url", post.get("permalink", ""))
    post_text = post.get("text", post.get("content", ""))
    profile_name = post.get("profile_name", post.get("profile", {}).get("name", ""))
    created_at = post.get("created_at", post.get("published_at", ""))
    media_urls = post.get("media", [])
    
    # Choose emoji based on network
    emoji_map = {
        "twitter": "🐦",
        "x": "𝕏",
        "instagram": "📸",
        "facebook": "📘",
        "linkedin": "💼"
    }
    emoji = emoji_map.get(network.lower(), "📣")
    
    # Build the message blocks
    blocks = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": f"{emoji} New {network.title()} Post",
                "emoji": True
            }
        },
        {
            "type": "section",
            "fields": [
                {
                    "type": "mrkdwn",
                    "text": f"*Profile:*\n{profile_name}"
                },
                {
                    "type": "mrkdwn",
                    "text": f"*Posted:*\n{created_at}"
                }
            ]
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*Content:*\n{post_text[:500] if post_text else '_No text content_'}"
            }
        }
    ]
    
    # Add media info if present
    if media_urls:
        media_count = len(media_urls) if isinstance(media_urls, list) else 1
        blocks.append({
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": f"📎 {media_count} media attachment(s)"
                }
            ]
        })
    
    # Add the view button if we have a URL
    if post_url:
        blocks.append({
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
        })
    
    blocks.append({"type": "divider"})
    
    slack_message = {"blocks": blocks}
    
    response = requests.post(SLACK_WEBHOOK_URL, json=slack_message)
    return response.status_code == 200

def check_for_new_posts():
    """Main function to check for new posts and send notifications."""
    last_check = get_last_check_time()
    current_time = datetime.now(timezone.utc)
    
    print(f"Checking for posts since {last_check.isoformat()}")
    
    posts = get_published_posts(last_check)
    
    prin

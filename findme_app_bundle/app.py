
from flask import Flask, render_template, request, redirect
import json
import os
import datetime

app = Flask(__name__)

SETTINGS_FILE = 'settings.json'
HISTORY_FILE = 'post_history.txt'

def load_settings():
    with open(SETTINGS_FILE, 'r') as f:
        return json.load(f)

def save_settings(settings):
    with open(SETTINGS_FILE, 'w') as f:
        json.dump(settings, f, indent=2)

def save_post_to_history(post):
    timestamp = datetime.datetime.now().isoformat()
    with open(HISTORY_FILE, 'a') as f:
        f.write(f"{timestamp} - {post}\n")

@app.route('/', methods=['GET', 'POST'])
def index():
    settings = load_settings()
    last_post = None
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, 'r') as f:
            lines = f.readlines()
            if lines:
                last_post = lines[-1]
    return render_template('index.html', settings=settings, last_post=last_post)

@app.route('/toggle', methods=['POST'])
def toggle_pause():
    settings = load_settings()
    settings['pause'] = not settings.get('pause', False)
    save_settings(settings)
    return redirect('/')

@app.route('/regenerate', methods=['POST'])
def regenerate():
    # Placeholder: You would generate a new post here with GPT
    fake_post = "Here’s your freshly regenerated daily post!"
    save_post_to_history(fake_post)
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)

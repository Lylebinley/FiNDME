## FINDME APP — Enhanced Version with GPT, Pause, and Regeneration
# Project Structure:
# - Flask dashboard
# - Scheduler
# - GPT-based daily post generator (OpenAI API)
# - Local settings.json
# - Post history
# - Post regeneration
# - Pause toggle

# settings.json (user config)
{
  "business_name": "Down to Earth Electric Inc.",
  "zip_code": "75056",
  "industry": "Electrical",
  "tone": "laid back",
  "platform": "Facebook",
  "phone": "214-859-8707",
  "email": "downtoearthelec@gmail.com",
  "facebook_url": "https://facebook.com/DownToEarthElectric",
  "qr_code_url": "https://example.com/qr-code.png",
  "password": "admin123",
  "pause": false,
  "openai_api_key": "sk-REPLACE_ME"
}

# main.py (GPT content generator)
import json
from datetime import date
import openai

with open("settings.json") as f:
    settings = json.load(f)

if settings.get("pause"):
    print("Daily post generation paused.")
    exit()

openai.api_key = settings["openai_api_key"]

def generate_post(settings):
    prompt = f"""
    Write a daily {settings['platform']} post for a(n) {settings['industry']} company named {settings['business_name']}.
    They are located in ZIP code {settings['zip_code']}.
    The tone should be {settings['tone']}.
    Keep it short, natural, and relevant to local homeowners.
    Mention services when helpful.
    """
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=300
    )
    return response.choices[0].message.content.strip()

def save_post(content):
    today = date.today().isoformat()
    with open(f"posts/{today}.txt", "w") as f:
        f.write(content)

if __name__ == "__main__":
    post = generate_post(settings)
    save_post(post)
    print(post)

# app.py (Flask admin dashboard)
from flask import Flask, render_template, request, redirect, url_for
import json, os
from datetime import date
import subprocess

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def dashboard():
    with open("settings.json") as f:
        settings = json.load(f)

    today = date.today().isoformat()
    post_path = f"posts/{today}.txt"
    post = open(post_path).read() if os.path.exists(post_path) else "No post generated yet."

    if request.method == "POST":
        if request.form.get("password") == settings['password']:
            if request.form.get("action") == "regenerate":
                subprocess.run(["python", "main.py"])
                return redirect(url_for("dashboard"))
            elif request.form.get("action") == "toggle_pause":
                settings['pause'] = not settings.get('pause', False)
                with open("settings.json", "w") as f:
                    json.dump(settings, f, indent=2)
                return redirect(url_for("dashboard"))
            return render_template("dashboard.html", post=post, settings=settings, authed=True)
        else:
            return render_template("dashboard.html", post=post, settings=settings, authed=False, error="Bad password")

    return render_template("dashboard.html", post=post, settings=settings, authed=False)

if __name__ == "__main__":
    app.run(debug=True)

# scheduler.py (auto-run main.py daily)
from apscheduler.schedulers.blocking import BlockingScheduler
import subprocess

sched = BlockingScheduler()

@sched.scheduled_job('cron', hour=7)
def scheduled_job():
    subprocess.run(["python", "main.py"])

sched.start()

# templates/dashboard.html
<!DOCTYPE html>
<html>
<head>
    <title>FiNDME Dashboard</title>
    <link rel="stylesheet" href="/static/style.css">
</head>
<body>
    {% if not authed %}
        <form method="POST">
            <label>Enter Admin Password:</label><br>
            <input type="password" name="password">
            <button type="submit">Login</button>
            {% if error %}<p>{{ error }}</p>{% endif %}
        </form>
    {% else %}
        <h1>Today's Post</h1>
        <pre>{{ post }}</pre>
        <form method="POST">
            <input type="hidden" name="password" value="{{ settings['password'] }}">
            <button name="action" value="regenerate">Regenerate Post</button>
            <button name="action" value="toggle_pause">{{ 'Unpause' if settings['pause'] else 'Pause' }} Daily Posts</button>
        </form>
        <h2>Settings</h2>
        <ul>
            {% for key, val in settings.items() %}
                <li><strong>{{ key }}:</strong> {{ val }}</li>
            {% endfor %}
        </ul>
    {% endif %}
</body>
</html>

# static/style.css
body {
    font-family: sans-serif;
    background-color: #f2f2f2;
    padding: 20px;
}
input, button {
    font-size: 1rem;
    padding: 5px;
    margin: 5px 0;
}
pre {
    background: #fff;
    padding: 10px;
    border: 1px solid #ccc;
}

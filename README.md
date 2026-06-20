# 📋 Uniform Check-In App

A Streamlit web app for daily classroom uniform and attendance tracking (Mon–Fri).

## Features
- ✅ **Daily Check-In** — mark each student as checked, choose uniform items, set status (Present / Late / Absent / Sick), add notes
- 📊 **Weekly Summary** — colour-coded table + attendance counts + CSV export
- 📆 **Monthly Summary** — full month overview with top absence/uniform issue leaderboard + CSV export
- ⚙️ **Settings** — add/edit student names and customise uniform checklist items anytime

---

## 🚀 Deploy to Streamlit Cloud (Free)

### Step 1 — Push to GitHub

1. Create a **new repository** on [github.com](https://github.com) (e.g. `uniform-checker`)
2. Upload all files from this folder into the repo (drag & drop works on GitHub)

Your repo should look like:
```
uniform-checker/
├── app.py
├── requirements.txt
├── .gitignore
└── README.md
```

### Step 2 — Deploy on Streamlit Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io) and sign in with GitHub
2. Click **"New app"**
3. Select your repo → branch `main` → main file `app.py`
4. Click **"Deploy!"**

That's it! Your app will be live at a URL like:
`https://your-username-uniform-checker-app-xxxx.streamlit.app`

---

## 💾 Data Storage Note

Records are saved locally in a `data/` folder as JSON files.
- On Streamlit Cloud, data **resets** when the app restarts (free tier limitation).
- To keep data permanently, see the optional Persistent Storage section below.

### Optional: Persistent Storage via GitHub (Advanced)

To save data back to your GitHub repo automatically, you can use the GitHub API.
A simple alternative: **download the CSV** from the Summary pages after each week/month for your own records.

---

## 🛠 Local Development

```bash
pip install -r requirements.txt
streamlit run app.py
```

Then open `http://localhost:8501` in your browser.

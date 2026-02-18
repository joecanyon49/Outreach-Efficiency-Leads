# Quick Start - GCU Backend in 5 Minutes

## What You'll Have
A Python backend that fetches data from **3 free APIs simultaneously** when the frontend searches for a prospect.

---

## Step 1: Install Dependencies (1 min)
```bash
cd c:\Python
pip install -r requirements.txt
```

---

## Step 2: Get Free API Keys (2-3 min)

### NewsAPI (for articles/podcasts)
1. Go to https://newsapi.org
2. Click "Get API Key"
3. Sign up (free)
4. Copy your key

### Census Bureau (for income data)
1. Go to https://api.census.gov/data/key_signup.html
2. Enter your email
3. Wait for email with your key (instant usually)
4. Copy the key

---

## Step 3: Create `.env` File (1 min)
Create file `c:\Python\.env` with:
```
NEWSAPI_KEY=paste_your_newsapi_key_here
CENSUS_API_KEY=paste_your_census_key_here
```

---

## Step 4: Run Backend (1 min)
```bash
python backend.py
```

You'll see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
```

---

## Step 5: Test It Works
Open browser: **http://localhost:8000/docs**

You'll see an interactive API explorer. Try the `/lookup` endpoint:
- name: `John Doe`
- city: `Phoenix`
- state: `AZ`
- zip_code: `85254`

Click "Execute" → You'll get data from all APIs!

---

## Done! 🎉

The backend is now:
- ✅ Running on `http://localhost:8000`
- ✅ Ready for HTML frontend to call
- ✅ Fetching from 3 free APIs in parallel

### Next: Integrate with HTML

Add this to your HTML `<head>`:
```html
<script src="backend_client.js"></script>
```

Then use in your JavaScript:
```javascript
// When user searches
const data = await fetchProspectData("John", "Doe", "Phoenix", "AZ", "85254");
console.log(data.articles);  // News articles
console.log(data.nonprofits); // Nonprofit affiliations
console.log(data.income);     // Census income data
```

---

## Troubleshooting

**"NEWSAPI_KEY not set"**
- Make sure `.env` file exists in `c:\Python`
- Restart backend after creating `.env`

**"Connection refused"**
- Backend not running - run `python backend.py`

**"API returned 401"**
- API key is invalid - check https://newsapi.org/account and https://api.census.gov for your keys

---

## Full Docs
See `BACKEND_SETUP.md` for complete setup guide with all endpoints and details.

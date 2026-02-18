# GCU Lead Discovery Engine - Backend Setup Guide

## Overview
This backend provides a **FastAPI** service that fetches data from multiple free APIs **in parallel** to enrich donor/prospect data for the GCU Lead Discovery Engine.

### Free APIs Used
1. **ProPublica Nonprofit Explorer** - IRS 990 data, nonprofit affiliations, giving history (no key needed)
2. **NewsAPI** - Articles, podcasts, news mentions (free tier: 100 requests/day)
3. **Census Bureau API** - Income, demographic data by ZIP code (free, needs key)
4. **Zillow/Redfin** - Property values (optional, structured data available)

---

## Step-by-Step Setup

### Step 1: Install Python Dependencies
```bash
cd c:\Python
pip install -r requirements.txt
```

### Step 2: Get Free API Keys

#### 2a. NewsAPI (for articles, podcasts, news)
- **Go to:** https://newsapi.org
- **Click:** "Get API Key" (top right)
- **Sign up** with email (free tier available)
- **Copy** your API key
- **Paste** into `.env` file as `NEWSAPI_KEY=your_key_here`

#### 2b. Census Bureau API (for income data by ZIP)
- **Go to:** https://api.census.gov/data/key_signup.html
- **Fill out** the form with your email
- **Check your email** for activation link
- **Copy** the key provided
- **Paste** into `.env` file as `CENSUS_API_KEY=your_key_here`

#### 2c. ProPublica (no key needed)
- ProPublica's Nonprofit Explorer API is **free and requires no key**
- Used for IRS 990 data and nonprofit affiliations
- More info: https://projects.propublica.org/nonprofits/api

### Step 3: Create `.env` File
```bash
# Copy the example file
copy .env.example .env

# OR manually create .env with:
NEWSAPI_KEY=your_newsapi_key_from_step_2a
CENSUS_API_KEY=your_census_key_from_step_2b
CLOUDFLARE_WORKER_URL=
```

### Step 4: Run the Backend Server
```bash
python backend.py
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
```

Test the API in your browser: **http://localhost:8000/docs**
(FastAPI auto-generates interactive docs)

---

## API Endpoints

### Main Endpoint: Comprehensive Lookup
```
GET /lookup?name=John%20Doe&city=Phoenix&state=AZ&zip=85254
```
**Returns:** Aggregated data from all sources (nonprofits, news, income, property)

Example:
```bash
curl "http://localhost:8000/lookup?name=John+Doe&city=Phoenix&state=AZ&zip=85254"
```

### Individual API Endpoints

#### Search Nonprofits
```
GET /nonprofits/search?q=GCU+alumni
```

#### Search News/Articles
```
GET /news/search?q=John+Doe+Phoenix+nonprofit
```

#### Get Census Income Data
```
GET /census/income?state=AZ&zip=85254
```

#### Health Check
```
GET /health
```
Shows which API keys are configured.

---

## Integrating with HTML Frontend

To call the backend from your HTML file, modify the `runVA()` function or create a new function:

```javascript
async function fetchProspectData(firstName, lastName, city, state, zip) {
  const backendUrl = "http://localhost:8000/lookup";
  try {
    const params = new URLSearchParams({
      name: `${firstName} ${lastName}`,
      city: city,
      state: state,
      zip_code: zip
    });
    
    const res = await fetch(`${backendUrl}?${params}`);
    if (!res.ok) throw new Error(`Backend error: ${res.status}`);
    
    const data = await res.json();
    console.log("Prospect data:", data);
    
    // Parse and display
    return {
      nonprofits: data.nonprofits,
      articles: data.news_articles,
      income: data.census_data,
      property: data.property_data
    };
  } catch (err) {
    console.error("Fetch error:", err);
    return null;
  }
}
```

---

## Running with Gunicorn (Production)

For real deployments, use **Gunicorn**:

```bash
pip install gunicorn
gunicorn -w 4 -k uvicorn.workers.UvicornWorker backend:app --bind 0.0.0.0:8000
```

---

## Troubleshooting

### "NEWSAPI_KEY not set"
- Verify `.env` file exists in `c:\Python`
- Restart the Python server after adding keys
- Check that the key is valid at https://newsapi.org/account/login

### "Census API error: 400"
- Verify ZIP code format (5 digits)
- Ensure state code is 2 letters (e.g., "AZ", "CA")
- Check Census key is activated (wait 5 minutes after signup)

### CORS Errors in Browser
If accessing from a different domain:
1. **Option A:** Use Cloudflare Workers proxy (update `CLOUDFLARE_WORKER_URL`)
2. **Option B:** Add `Access-Control-Allow-Origin: *` headers (already done in backend)
3. **Option C:** Run frontend and backend on same machine

### "Connection refused" - Backend not running
```bash
# Make sure backend is running
python backend.py

# Or check if port 8000 is in use
netstat -ano | findstr :8000  # Windows
lsof -i :8000  # Mac/Linux
```

---

## API Performance Notes

- **Parallel execution:** All APIs called simultaneously (async)
- **Typical response time:** 2-5 seconds (depends on network/API speed)
- **Rate limits:**
  - NewsAPI: 100 requests/day (free tier)
  - Census: No explicit limit but respectful use recommended
  - ProPublica: No rate limit (public API)

---

## Free Data Sources Reference

| Source | Data Type | Key Needed | Requests/Day |
|--------|-----------|-----------|--------------|
| ProPublica | Nonprofits, IRS 990 | No | Unlimited |
| NewsAPI | Articles, Podcasts | Yes | 100 (free) |
| Census Bureau | Income, Demographics | Yes | Unlimited |
| Zillow/Redfin | Property Values | Optional | Limited |

---

## Next Steps

1. **Get the API keys** (Steps 2a-2b above)
2. **Create `.env` file** (Step 3)
3. **Run backend** (Step 4)
4. **Test in browser** at http://localhost:8000/docs
5. **Integrate with HTML** frontend (optional code provided above)

For questions or issues, refer to the **Troubleshooting** section or API documentation at `/docs`.

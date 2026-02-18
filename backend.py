"""
GCU Lead Discovery Engine - FastAPI Backend
Fetches data from multiple free APIs in parallel.
"""

import asyncio
import os
from typing import Optional, List, Dict, Any
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import httpx
import logging

# Load environment variables from .env file
load_dotenv()

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Initialize FastAPI app
app = FastAPI(title="GCU Lead Discovery Engine API", version="1.0.0")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for local development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Keys (from environment variables or .env file)
PROPUBLICA_API_KEY = os.getenv("PROPUBLICA_API_KEY", "")
NEWSAPI_KEY = os.getenv("NEWSAPI_KEY", "")
CENSUS_API_KEY = os.getenv("CENSUS_API_KEY", "")


# ──────────────────────────────────────────────────────────────────────────
# API CLIENTS
# ──────────────────────────────────────────────────────────────────────────


class ProPublicaClient:
    """ProPublica Nonprofit Explorer API - IRS 990 data, charitable giving."""
    BASE_URL = "https://projects.propublica.org/nonprofits/api/v2"
    
    @staticmethod
    async def search_nonprofits(query: str, org_name: str = None) -> Dict[str, Any]:
        """Search for nonprofits by name or location."""
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                # Search for nonprofits matching the criteria
                endpoint = f"{ProPublicaClient.BASE_URL}/organizations.json"
                params = {"q": query, "limit": 10}
                response = await client.get(endpoint, params=params)
                response.raise_for_status()
                return response.json()
        except httpx.RequestError as e:
            logger.error(f"ProPublica API error: {e}")
            return {"organizations": []}
    
    @staticmethod
    async def get_nonprofit_details(ein: str) -> Dict[str, Any]:
        """Get details on a specific nonprofit by EIN."""
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                endpoint = f"{ProPublicaClient.BASE_URL}/organizations/{ein}.json"
                response = await client.get(endpoint)
                response.raise_for_status()
                return response.json()
        except httpx.RequestError as e:
            logger.error(f"ProPublica API error: {e}")
            return {}


class NewsAPIClient:
    """NewsAPI - search for articles, podcasts, news about a person or topic."""
    BASE_URL = "https://newsapi.org/v2"
    
    @staticmethod
    async def search_news(query: str, sort_by: str = "relevancy") -> Dict[str, Any]:
        """Search for news articles."""
        if not NEWSAPI_KEY:
            logger.warning("NEWSAPI_KEY not set - news search unavailable")
            return {"articles": []}
        
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                endpoint = f"{NewsAPIClient.BASE_URL}/everything"
                params = {
                    "q": query,
                    "sortBy": sort_by,
                    "pageSize": 10,
                    "apiKey": NEWSAPI_KEY,
                    "language": "en"
                }
                response = await client.get(endpoint, params=params)
                response.raise_for_status()
                return response.json()
        except httpx.RequestError as e:
            logger.error(f"NewsAPI error: {e}")
            return {"articles": []}


class CensusDataClient:
    """U.S. Census Bureau - income, demographic data."""
    BASE_URL = "https://api.census.gov/data"
    
    @staticmethod
    async def get_area_income(state: str, zip_code: str) -> Dict[str, Any]:
        """Get median income data for a ZIP code or area."""
        if not CENSUS_API_KEY:
            logger.warning("CENSUS_API_KEY not set - census data unavailable")
            return {}
        
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                # ACS 5-year data median household income
                endpoint = f"{CensusDataClient.BASE_URL}/2021/acs/acs5"
                params = {
                    "get": "NAME,B19013_001E",  # Median household income
                    "for": f"zip code tabulation area:{zip_code}",
                    "key": CENSUS_API_KEY
                }
                response = await client.get(endpoint, params=params)
                response.raise_for_status()
                data = response.json()
                return {"zip": zip_code, "median_income": data[1][1] if len(data) > 1 else None}
        except httpx.RequestError as e:
            logger.error(f"Census API error: {e}")
            return {}


class ParcelDataClient:
    """Zillow/Property data - property values (via free public sources)."""
    
    @staticmethod
    async def estimate_property_value(address: str) -> Dict[str, Any]:
        """
        Estimate property value using free public data sources.
        Note: Zillow API is deprecated. Using Redfin data or free alternatives.
        """
        # For now, return placeholder. In production, use Redfin API or web scraping
        # with proper rate limiting.
        return {
            "address": address,
            "estimated_value": None,
            "source": "public_records",
            "note": "Requires Redfin API key or web scraping setup"
        }


# ──────────────────────────────────────────────────────────────────────────
# UNIFIED DATA MODEL
# ──────────────────────────────────────────────────────────────────────────


async def fetch_prospect_data(name: str, city: str, state: str, zip_code: str) -> Dict[str, Any]:
    """
    Fetch data from multiple APIs in parallel for a prospect.
    Returns aggregated data from nonprofits, news, census, and property sources.
    """
    
    # Prepare search queries
    nonprofit_query = f"{name} {city} {state}"
    news_query = f"{name} {city} nonprofit giving charity"
    
    # Fetch all data in parallel
    results = await asyncio.gather(
        ProPublicaClient.search_nonprofits(nonprofit_query),
        NewsAPIClient.search_news(news_query),
        CensusDataClient.get_area_income(state, zip_code),
        ParcelDataClient.estimate_property_value(f"{city}, {state} {zip_code}"),
        return_exceptions=True
    )
    
    nonprofits_data, news_data, census_data, property_data = results
    
    # Parse results
    nonprofits = []
    if isinstance(nonprofits_data, dict) and "organizations" in nonprofits_data:
        nonprofits = nonprofits_data.get("organizations", [])[:5]
    
    news_articles = []
    if isinstance(news_data, dict) and "articles" in news_data:
        news_articles = news_data.get("articles", [])[:8]
    
    census_info = census_data if isinstance(census_data, dict) else {}
    property_info = property_data if isinstance(property_data, dict) else {}
    
    return {
        "prospect": {
            "name": name,
            "city": city,
            "state": state,
            "zip": zip_code
        },
        "nonprofits": nonprofits,
        "news_articles": news_articles,
        "census_data": census_info,
        "property_data": property_info,
        "timestamp": asyncio.get_event_loop().time()
    }


# ──────────────────────────────────────────────────────────────────────────
# FAST API ENDPOINTS
# ──────────────────────────────────────────────────────────────────────────


@app.get("/")
async def root():
    """Health check / API info."""
    return {
        "service": "GCU Lead Discovery Engine API",
        "version": "1.0.0",
        "status": "operational",
        "endpoints": {
            "lookup": "/lookup?name=...&city=...&state=...&zip=...",
            "nonprofits": "/nonprofits/search?q=...",
            "news": "/news/search?q=...",
            "census": "/census/income?state=...&zip=..."
        }
    }


@app.get("/lookup")
async def lookup_prospect(
    name: str = Query(..., min_length=1, description="Prospect name"),
    city: str = Query(..., min_length=1, description="City"),
    state: str = Query(..., min_length=2, max_length=2, description="State code (e.g., AZ)"),
    zip_code: str = Query(..., min_length=5, max_length=5, description="ZIP code")
):
    """
    Main endpoint: fetch aggregated data for a prospect from all APIs.
    """
    try:
        data = await fetch_prospect_data(name, city, state, zip_code)
        return data
    except Exception as e:
        logger.error(f"Lookup error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/nonprofits/search")
async def search_nonprofits(q: str = Query(..., min_length=1, description="Search query")):
    """Search for nonprofits by name or location."""
    try:
        results = await ProPublicaClient.search_nonprofits(q)
        return results
    except Exception as e:
        logger.error(f"Nonprofit search error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/nonprofits/{ein}")
async def get_nonprofit(ein: str = Query(..., description="EIN (Employer ID Number)")):
    """Get details on a specific nonprofit."""
    try:
        results = await ProPublicaClient.get_nonprofit_details(ein)
        return results
    except Exception as e:
        logger.error(f"Nonprofit details error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/news/search")
async def search_news(q: str = Query(..., min_length=1, description="Search query")):
    """Search for news articles, podcasts, mentions."""
    try:
        results = await NewsAPIClient.search_news(q)
        return results
    except Exception as e:
        logger.error(f"News search error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/census/income")
async def get_census_income(
    state: str = Query(..., min_length=2, max_length=2, description="State code"),
    zip_code: str = Query(..., min_length=5, max_length=5, description="ZIP code")
):
    """Get median household income for a ZIP code."""
    try:
        results = await CensusDataClient.get_area_income(state, zip_code)
        return results
    except Exception as e:
        logger.error(f"Census income error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check():
    """Simple health check."""
    return {
        "status": "healthy",
        "has_newsapi_key": bool(NEWSAPI_KEY),
        "has_census_key": bool(CENSUS_API_KEY),
        "has_propublica_key": True  # ProPublica doesn't require key
    }


# ──────────────────────────────────────────────────────────────────────────
# RUN SERVER
# ──────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")

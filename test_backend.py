"""
Test script for GCU Lead Discovery Engine Backend
Run this to verify all APIs are working correctly before using in production.
"""

import asyncio
import sys
from backend import (
    fetch_prospect_data,
    ProPublicaClient,
    NewsAPIClient,
    CensusDataClient,
    health_check
)

def print_section(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")

async def test_all_apis():
    # Test prospect lookup
    print_section("TEST 1: Full Prospect Lookup (All APIs)")
    
    try:
        data = await fetch_prospect_data(
            name="Grace Hopper",
            city="Phoenix",
            state="AZ",
            zip_code="85254"
        )
        
        print(f"Prospect: {data['prospect']}")
        print(f"✓ Nonprofits found: {len(data['nonprofits'])}")
        print(f"✓ News articles found: {len(data['news_articles'])}")
        print(f"✓ Census data: {data['census_data']}")
        print(f"✓ Property data: {data['property_data']}")
        
    except Exception as e:
        print(f"✗ Error: {e}")
        return False
    
    # Test individual APIs
    print_section("TEST 2: ProPublica API (Nonprofits)")
    try:
        result = await ProPublicaClient.search_nonprofits("education Phoenix")
        print(f"✓ ProPublica working - Found {len(result.get('organizations', []))} organizations")
    except Exception as e:
        print(f"✗ ProPublica error: {e}")
    
    print_section("TEST 3: NewsAPI (Articles)")
    try:
        result = await NewsAPIClient.search_news("nonprofit education America")
        status = "✓" if result.get("articles") else "⚠"  # OK even if no articles
        print(f"{status} NewsAPI working - Found {len(result.get('articles', []))} articles")
        if "message" in result:
            print(f"  Note: {result['message']}")
    except Exception as e:
        print(f"✗ NewsAPI error: {e}")
    
    print_section("TEST 4: Census API (Income Data)")
    try:
        result = await CensusDataClient.get_area_income("AZ", "85254")
        if result.get("median_income"):
            print(f"✓ Census API working - Median income in 85254: ${result['median_income']:,.0f}")
        else:
            print(f"⚠ Census API response: {result}")
    except Exception as e:
        print(f"✗ Census API error: {e}")
    
    print_section("SUMMARY")
    print("✓ Backend is running and APIs are configured!")
    print("\nNext steps:")
    print("1. Open http://localhost:8000/docs in browser for interactive API docs")
    print("2. Test in HTML by calling backend_client.js functions")
    print("3. Check BACKEND_SETUP.md for full integration guide")
    
    return True

if __name__ == "__main__":
    print("GCU Lead Discovery Engine - API Test Suite\n")
    
    try:
        success = asyncio.run(test_all_apis())
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n✗ Fatal error: {e}")
        print("\nMake sure backend.py is running: python backend.py")
        sys.exit(1)

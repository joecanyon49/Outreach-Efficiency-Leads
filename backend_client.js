/**
 * GCU Lead Discovery Engine - Backend API Client
 * Helper to call the Python FastAPI backend
 */

// Backend URL - change if backend runs on different machine
const BACKEND_URL = "http://localhost:8000";

/**
 * Fetch comprehensive prospect data from all APIs in parallel
 * @param {string} firstName - Prospect first name
 * @param {string} lastName - Prospect last name  
 * @param {string} city - City
 * @param {string} state - State code (e.g., "AZ")
 * @param {string} zip - ZIP code (5 digits)
 * @returns {Promise<Object>} - Data from nonprofits, news, census, property
 */
async function fetchProspectData(firstName, lastName, city, state, zip) {
  const fullName = `${firstName} ${lastName}`;
  
  try {
    const params = new URLSearchParams({
      name: fullName,
      city: city,
      state: state,
      zip_code: zip
    });
    
    console.log(`[Backend] Fetching data for ${fullName} in ${city}, ${state} ${zip}`);
    
    const res = await fetch(`${BACKEND_URL}/lookup?${params.toString()}`);
    
    if (!res.ok) {
      throw new Error(`Backend returned ${res.status}: ${res.statusText}`);
    }
    
    const data = await res.json();
    console.log("[Backend] Response:", data);
    
    return {
      success: true,
      data: data,
      nonprofits: data.nonprofits || [],
      articles: data.news_articles || [],
      income: data.census_data || {},
      property: data.property_data || {}
    };
    
  } catch (err) {
    console.error("[Backend] Error:", err.message);
    return {
      success: false,
      error: err.message,
      nonprofits: [],
      articles: [],
      income: {},
      property: {}
    };
  }
}

/**
 * Search for nonprofits
 * @param {string} query - Search query (name, city, topic)
 */
async function searchNonprofits(query) {
  try {
    const params = new URLSearchParams({ q: query });
    const res = await fetch(`${BACKEND_URL}/nonprofits/search?${params.toString()}`);
    if (!res.ok) throw new Error(`Error: ${res.status}`);
    return await res.json();
  } catch (err) {
    console.error("[Nonprofits] Error:", err);
    return { organizations: [] };
  }
}

/**
 * Search for news articles
 * @param {string} query - Search query (name, topic, nonprofit)
 */
async function searchNews(query) {
  try {
    const params = new URLSearchParams({ q: query });
    const res = await fetch(`${BACKEND_URL}/news/search?${params.toString()}`);
    if (!res.ok) throw new Error(`Error: ${res.status}`);
    return await res.json();
  } catch (err) {
    console.error("[News] Error:", err);
    return { articles: [] };
  }
}

/**
 * Get census income data for a ZIP code
 * @param {string} state - State code (e.g., "AZ")
 * @param {string} zip - ZIP code
 */
async function getCensusIncome(state, zip) {
  try {
    const params = new URLSearchParams({ state: state, zip_code: zip });
    const res = await fetch(`${BACKEND_URL}/census/income?${params.toString()}`);
    if (!res.ok) throw new Error(`Error: ${res.status}`);
    return await res.json();
  } catch (err) {
    console.error("[Census] Error:", err);
    return {};
  }
}

/**
 * Check backend health and which APIs are configured
 */
async function checkBackendHealth() {
  try {
    const res = await fetch(`${BACKEND_URL}/health`);
    if (!res.ok) throw new Error("Backend not responding");
    const data = await res.json();
    console.log("[Backend Health]", data);
    return data;
  } catch (err) {
    console.error("[Backend] Not running:", err.message);
    console.log("[Backend] Make sure to run: python backend.py");
    return null;
  }
}

// Example usage in HTML:
// Place this code in your HTML <script> tag or button onclick handler
/*
async function exampleUsage() {
  // Check backend
  const health = await checkBackendHealth();
  if (!health) {
    alert("Backend not running. Start it with: python backend.py");
    return;
  }
  
  // Fetch prospect data
  const result = await fetchProspectData("John", "Doe", "Scottsdale", "AZ", "85254");
  
  if (result.success) {
    console.log("Nonprofits:", result.nonprofits);
    console.log("News Articles:", result.articles);
    console.log("Income Data:", result.income);
    console.log("Property Data:", result.property);
  } else {
    console.error("Failed:", result.error);
  }
}
*/

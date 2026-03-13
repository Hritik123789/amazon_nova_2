# Permit Monitor Scraping Status

**Last Updated**: March 11, 2026  
**Status**: ✅ WORKING with real data from Reddit JSON API

---

## Data Sources

### 1. MahaRERA Projects ⚠️ Fallback Mode
**URL**: https://maharera.maharashtra.gov.in/projects-search-result  
**Status**: Using fallback data (site may require authentication)  
**Data Type**: Real estate project registrations  

**Issue**: The site doesn't return project listings via simple HTTP requests. Possible reasons:
- Requires authentication/login
- Uses JavaScript to load content dynamically
- May have CAPTCHA protection
- Search results page may need POST request with parameters

**Fallback Data**: Realistic mock data based on typical MahaRERA project structure

**Future Options**:
- Use Selenium/Playwright for JavaScript rendering
- Find MahaRERA RSS feed or API
- Scrape Mumbai real estate news sites instead
- Use official MahaRERA API if available

---

### 2. Reddit r/mumbai - Construction ✅ WORKING
**URL**: https://www.reddit.com/r/mumbai/search.json?q=construction&sort=new  
**Status**: ✅ Successfully scraping real data via JSON API  
**Data Type**: Community discussions about construction, development, projects  

**Success Metrics**:
- Returns 10 posts per request
- JSON format (easy to parse)
- No authentication required
- Includes metadata: title, text, URL, upvotes
- Real-time community intelligence

**Sample Output**:
```json
{
  "event_type": "community_discussion",
  "source": "Reddit_r/mumbai",
  "location": "Mumbai",
  "description": "Real Reddit post title about construction",
  "metadata": {
    "url": "https://reddit.com/r/mumbai/...",
    "platform": "reddit",
    "upvotes": 5
  }
}
```

---

### 3. Reddit r/mumbai - Bars/Restaurants ✅ WORKING
**URL**: https://www.reddit.com/r/mumbai/search.json?q=bar+OR+restaurant+OR+liquor&sort=new  
**Status**: ✅ Successfully scraping real data via JSON API  
**Data Type**: Community discussions about new bars, restaurants, liquor licenses  

**Filtering**: Only includes posts mentioning:
- "license"
- "opening"
- "new"
- "permit"
- "approved"

**Success Metrics**:
- Returns 10 posts per request
- Filters for license-related content
- Real community reports about new establishments
- Alternative to JavaScript-heavy Excise dashboard

---

## Safety Limits (Preventing Infinite Loops)

All scraping methods have these safeguards:

1. **Max Items**: 3 items per source (configurable)
2. **Request Timeout**: 15 seconds per HTTP request
3. **Max Retries**: 2 retry attempts with 2-second delays
4. **Iteration Limits**: Extra safety checks in all loops
5. **Max AI Normalization**: 5 items sent to Nova 2 Lite (cost control)

---

## Cost Tracking

**Per Run**:
- Scraping: $0 (free HTTP requests)
- AI Normalization (Nova 2 Lite): ~$0.0010 for 5 events
- **Total**: ~$0.0010 per run

**Daily Cost** (if run every hour):
- 24 runs × $0.0010 = $0.024/day
- Monthly: ~$0.72
- Well within $100 budget!

---

## Output Format

All events normalized to this schema:

```json
{
  "event_type": "real_estate_project | community_discussion | liquor_license",
  "source": "MahaRERA | Reddit_r/mumbai | Community_Reports",
  "location": "Area Name, Mumbai",
  "timestamp": "2026-03-11T21:24:43.149901",
  "description": "User-friendly 1-sentence description",
  "metadata": {
    "url": "Source URL",
    "platform": "reddit",
    "topic": "construction_development | commercial_license"
  },
  "category": "real_estate | infrastructure | commercial | community_discussion"
}
```

---

## Next Steps to Improve

### Option 1: Add More Reddit Sources
- r/india (filter for Mumbai)
- r/IndiaNonPolitical
- r/IndianStreetBets (real estate discussions)

### Option 2: Add News Scraping
- Times of India Mumbai
- Mumbai Mirror
- Hindustan Times Mumbai
- Indian Express Mumbai

### Option 3: Use Official APIs
- Twitter API (search for Mumbai permits/licenses)
- Google News API
- NewsAPI.org

### Option 4: JavaScript Rendering
- Use Selenium or Playwright for MahaRERA
- Scrape BMC portal with JavaScript support
- Access Excise dashboard data

---

## Conclusion

**Current Status**: ✅ WORKING with real data

The Permit Monitor is successfully collecting REAL data from Reddit's JSON API. While MahaRERA requires more advanced scraping (JavaScript rendering or authentication), the Reddit data provides valuable community intelligence about:
- Construction projects
- Development discussions
- New bars and restaurants
- Commercial activity

This is a solid foundation that can be expanded with additional sources as needed.

**Cost**: $0.0010 per run (very affordable!)  
**Data Quality**: Real community discussions from Reddit  
**Reliability**: High (JSON API is stable and public)

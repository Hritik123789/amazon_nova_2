# Frontend Enhancement - Handoff Document

## 👋 Hey Teammate!

I've completed the data collection infrastructure for CityPlus. Now we need to integrate this data into the frontend to make it come alive!

## ✅ What's Ready for You

### Data Collection Scripts (All Working!)

1. **News Articles** - `agents/news-synthesis/collected_news.json`
   - 104 real articles from CNN and BBC
   - Ready to display on the main page

2. **Permits** - `agents/permit-monitor/collected_permits.json`
   - 21 mock permits with locations
   - Ready to show on the map view

3. **Social Posts** - `agents/social-listening/collected_social.json`
   - 50 mock social media posts with sentiment
   - Ready for a community feed section

### Data Schemas

All data follows the schemas in `/shared/schemas/`:
- `news-article.json`
- `permit.json`
- `social-post.json`
- `briefing.json`

## 🎯 Your Tasks

### Task 1: Display News Articles on Main Page

**File to Edit**: `frontend/CityPlus-prototype/main.html`

**What to Do**:
1. Load `agents/news-synthesis/collected_news.json`
2. Display articles in a news feed section
3. Show: title, source, summary, published date
4. Add "Read More" links to original articles

**Example Code**:
```javascript
// Load news data
fetch('../../agents/news-synthesis/collected_news.json')
  .then(response => response.json())
  .then(articles => {
    const newsContainer = document.getElementById('news-feed');
    articles.slice(0, 10).forEach(article => {
      const articleCard = `
        <div class="news-card">
          <h3>${article.title}</h3>
          <p class="source">${article.source} - ${new Date(article.published_at).toLocaleDateString()}</p>
          <p>${article.summary}</p>
          <a href="${article.url}" target="_blank">Read More →</a>
        </div>
      `;
      newsContainer.innerHTML += articleCard;
    });
  });
```

### Task 2: Show Permits on Map View

**File to Edit**: `frontend/CityPlus-prototype/map.html`

**What to Do**:
1. Load `agents/permit-monitor/collected_permits.json`
2. Display permits as markers on the map
3. Show permit details in popup/sidebar when clicked
4. Color-code by permit type (building, liquor, zoning, demolition)

**Permit Data Structure**:
```json
{
  "id": "permit-10000",
  "type": "building",
  "address": "123 Market St",
  "description": "New restaurant construction",
  "status": "approved",
  "coordinates": {"lat": 37.7749, "lng": -122.4194},
  "distance_miles": 0.5
}
```

### Task 3: Add Social Feed Section

**File to Edit**: `frontend/CityPlus-prototype/main.html` or create new `social.html`

**What to Do**:
1. Load `agents/social-listening/collected_social.json`
2. Display posts in a feed format
3. Show sentiment with color coding:
   - 🟢 Positive (green)
   - 🟡 Neutral (yellow)
   - 🔴 Negative (red)
4. Display engagement metrics (likes, comments, shares)
5. Show trending topics at the top

**Example Layout**:
```html
<div class="social-feed">
  <div class="trending-topics">
    <h3>🔥 Trending Topics</h3>
    <span class="topic-tag">traffic</span>
    <span class="topic-tag">construction</span>
    <span class="topic-tag">parking</span>
  </div>
  
  <div class="posts">
    <!-- Posts go here -->
  </div>
</div>
```

### Task 4: Create Dashboard Overview

**File to Edit**: `frontend/CityPlus-prototype/index.html` or `main.html`

**What to Do**:
1. Show summary statistics:
   - Total permits in area
   - Recent news count
   - Sentiment breakdown
2. Add quick links to detailed views
3. Display "What's Happening" summary

**Example Stats**:
```javascript
{
  "permits": {
    "total": 21,
    "building": 4,
    "liquor": 5,
    "zoning": 11,
    "demolition": 1
  },
  "news": {
    "total": 104,
    "today": 15
  },
  "social": {
    "positive": 36,
    "neutral": 30,
    "negative": 34
  }
}
```

## 📁 File Locations

```
frontend/CityPlus-prototype/
├── index.html          # Landing page
├── main.html           # Main dashboard (add news & social here)
├── map.html            # Map view (add permits here)
├── styles.css          # Add new styles here
└── theme.js            # Theme utilities

agents/
├── news-synthesis/collected_news.json      # 104 articles
├── permit-monitor/collected_permits.json   # 21 permits
└── social-listening/collected_social.json  # 50 posts
```

## 🎨 Design Guidelines

- Use the existing Tailwind CSS classes
- Keep the dark/light theme toggle working
- Match the current color scheme
- Make it mobile-responsive
- Add loading states for data fetching

## 🚀 Testing

1. Open `index.html` in a browser
2. Check that data loads correctly
3. Test all interactive elements
4. Verify mobile responsiveness
5. Test dark/light theme switching

## 💡 Tips

- Use `fetch()` to load JSON files (works with local files in most browsers)
- If CORS issues occur, use a local server: `python -m http.server 8000`
- Add error handling for failed data loads
- Consider adding filters (by date, type, sentiment)

## 📞 Questions?

If you need clarification on:
- Data structure → Check `/shared/schemas/`
- API format → See `/docs/api-contracts/` (coming soon)
- Requirements → Check `.kiro/specs/project-workflow/requirements.md`

## ✅ Checklist

- [ ] News feed displaying on main page
- [ ] Permits showing on map with markers
- [ ] Social feed with sentiment colors
- [ ] Dashboard statistics summary
- [ ] Mobile responsive
- [ ] Dark/light theme working
- [ ] Error handling for data loading
- [ ] Tested in multiple browsers

## 🎯 Priority Order

1. **High Priority**: News feed on main page (easiest, most visible)
2. **High Priority**: Dashboard statistics
3. **Medium Priority**: Permits on map
4. **Medium Priority**: Social feed
5. **Low Priority**: Filters and advanced features

Good luck! The data is all ready for you. Just load the JSON files and display them beautifully! 🚀

---

**Last Updated**: March 2, 2026
**Data Collection Status**: ✅ Complete
**Your Turn**: Frontend Integration

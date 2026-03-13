# Selenium Setup Guide for MahaRERA Scraping

This guide will help you set up Selenium and ChromeDriver to enable real MahaRERA project scraping.

---

## Why Selenium?

MahaRERA's website uses JavaScript to dynamically load project listings. Simple HTTP requests (like `requests` library) cannot see this content because it's rendered after the page loads. Selenium automates a real Chrome browser to:

1. Load the page
2. Wait for JavaScript to execute
3. Extract the rendered HTML with all project data

---

## Installation Steps

### Step 1: Install Selenium

```bash
pip install selenium
```

### Step 2: Install ChromeDriver

ChromeDriver is the bridge between Selenium and Chrome browser.

#### Option A: Automatic Installation (Recommended)

```bash
pip install webdriver-manager
```

Then update the code to use:
```python
from webdriver_manager.chrome import ChromeDriverManager
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
```

#### Option B: Manual Installation

1. **Check your Chrome version**:
   - Open Chrome
   - Go to `chrome://settings/help`
   - Note your version (e.g., "131.0.6778.86")

2. **Download matching ChromeDriver**:
   - Visit: https://googlechromelabs.github.io/chrome-for-testing/
   - Download the version matching your Chrome
   - For Windows: Download `chromedriver-win64.zip`

3. **Extract and add to PATH**:
   ```bash
   # Extract chromedriver.exe
   # Move to a permanent location, e.g., C:\chromedriver\
   # Add C:\chromedriver\ to your system PATH
   ```

4. **Verify installation**:
   ```bash
   chromedriver --version
   ```

---

## Testing the Setup

### Quick Test Script

Create `test_selenium.py`:

```python
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

# Setup Chrome options
chrome_options = Options()
chrome_options.add_argument('--headless')  # Run without opening browser window
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')

# Create driver
driver = webdriver.Chrome(options=chrome_options)

# Test navigation
driver.get('https://www.google.com')
print(f"✅ Page title: {driver.title}")

# Close
driver.quit()
print("✅ Selenium is working!")
```

Run:
```bash
python test_selenium.py
```

Expected output:
```
✅ Page title: Google
✅ Selenium is working!
```

---

## Running the Permit Monitor with Selenium

Once Selenium is installed:

```bash
python agents/permit-monitor/permit_monitor_real.py
```

You should see:
```
🏗️  Initializing Real Permit Monitor...
✓ Connected to Amazon Bedrock
🔒 Safety limits enabled:
   • Selenium enabled: True

🏢 Scraping MahaRERA projects...
   • Starting Chrome WebDriver...
   • Loading https://maharera.maharashtra.gov.in/projects-search-result?page=1...
   • Waiting for projects to load...
   ✓ Found 3 MahaRERA projects
   ✓ Extracted 3 real estate projects
```

---

## Troubleshooting

### Error: "chromedriver not found"

**Solution**: ChromeDriver is not in your PATH.
- Use Option A (webdriver-manager) for automatic handling
- Or manually add ChromeDriver to PATH

### Error: "Chrome version mismatch"

**Solution**: ChromeDriver version doesn't match your Chrome browser.
- Download the correct ChromeDriver version
- Or use webdriver-manager to handle this automatically

### Error: "selenium.common.exceptions.WebDriverException"

**Solution**: Chrome browser is not installed.
- Install Google Chrome: https://www.google.com/chrome/
- Or use Firefox with geckodriver instead

### Selenium is too slow

**Solution**: Selenium is slower than simple HTTP requests because it launches a real browser.
- This is expected behavior
- The `--headless` flag helps (no GUI rendering)
- Consider caching results and running less frequently

### Want to disable Selenium?

Edit `permit_monitor_real.py`:
```python
monitor = PermitMonitor(max_items_per_source=3, demo_mode=True, use_selenium=False)
```

This will use fallback data instead of real scraping.

---

## Performance Comparison

| Method | Speed | Data Quality | Setup Complexity |
|--------|-------|--------------|------------------|
| requests + BeautifulSoup | Fast (1-2s) | ❌ No data (JavaScript) | Easy |
| Selenium + Chrome | Slow (10-15s) | ✅ Real data | Medium |
| Reddit JSON API | Fast (1-2s) | ✅ Real community data | Easy |

**Recommendation**: Use Selenium for MahaRERA + Reddit API for community intelligence.

---

## Cost Impact

Selenium itself is free, but:
- **Time**: Adds 10-15 seconds per run
- **Resources**: Uses more CPU/memory (Chrome browser)
- **AWS Cost**: No change (Nova 2 Lite cost is the same)

**Total cost per run**: Still ~$0.0010 (only Nova normalization costs money)

---

## Alternative: webdriver-manager (Easiest)

Instead of manual ChromeDriver setup, use webdriver-manager:

```bash
pip install webdriver-manager
```

Update the code:
```python
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

chrome_options = Options()
chrome_options.add_argument('--headless')

# Automatically downloads and manages ChromeDriver
driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()),
    options=chrome_options
)
```

This handles version matching automatically!

---

## Next Steps

1. Install Selenium: `pip install selenium`
2. Install webdriver-manager: `pip install webdriver-manager` (recommended)
3. Run the permit monitor: `python agents/permit-monitor/permit_monitor_real.py`
4. Check the output: `agents/permit-monitor/permit_events_real.json`

You should now see REAL MahaRERA project data instead of fallback data! 🎉

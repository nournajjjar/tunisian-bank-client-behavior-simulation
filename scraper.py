import os
import json
import time
import random
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

class BankScraper:
    def __init__(self, driver_path: str = None):
        options = Options()
        
        # Enhanced anti-detection settings
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])
        options.add_experimental_option('useAutomationExtension', False)
        
        # Realistic user agent
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        ]
        options.add_argument(f"user-agent={random.choice(user_agents)}")
        
        # Connection settings - enhanced for Tunisian banks
        options.add_argument('--disable-dns-prefetch')
        options.add_argument('--ignore-certificate-errors')
        options.add_argument('--allow-running-insecure-content')
        options.add_argument('--disable-web-security')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-features=VizDisplayCompositor')
        
        # Performance
        options.add_argument("--headless=new")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-extensions")
        
        # Initialize driver
        if not driver_path:
            driver_path = "C:/Users/PC/Documents/tunisian-banks-scraper/chromedriver-win64/chromedriver-win64/chromedriver.exe"
        
        try:
            self.driver = webdriver.Chrome(
                service=Service(driver_path),
                options=options
            )
            # Set appropriate timeouts
            self.driver.set_page_load_timeout(45)
            self.driver.set_script_timeout(30)
            
            # Execute CDP commands to prevent detection
            self.driver.execute_cdp_cmd('Network.setUserAgentOverride', {
                "userAgent": random.choice(user_agents)
            })
            self.driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
                'source': '''
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => undefined
                    })
                    window.chrome = { runtime: {} };
                '''
            })
            
        except Exception as e:
            print(f"Driver initialization failed: {e}")
            raise
        
        # Groq client
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"), timeout=90)

    def _handle_special_banks(self, bank_info):
        """Special handling for problematic banks with extended timeouts"""
        url = bank_info["url"]
        
        try:
            # Extended timeout for specific banks
            if bank_info.get('timeout_extended', False):
                self.driver.set_page_load_timeout(60)
                print(f"Extended timeout to 60s for {bank_info['name']}")
            
            # Bank-specific handling
            if "bna.tn" in url:
                # BNA has specific news structure
                time.sleep(3)
                self.driver.execute_script("window.scrollTo(0, 500)")
                
            elif "stb.com.tn" in url:
                # STB - scroll to news section
                time.sleep(2)
                self.driver.execute_script("window.scrollTo(0, 800)")
                
            elif "attijaribank" in url:
                # Attijari - handle their complex structure
                time.sleep(4)
                
            elif "biat.com.tn" in url:
                # BIAT anti-bot handling
                time.sleep(5)
                self.driver.execute_script("window.scrollTo(0, 400)")
                time.sleep(2)
                self.driver.execute_script("window.scrollTo(0, 1000)")
                
            elif "atb.tn" in url:
                # ATB extended loading
                time.sleep(6)
                
            elif "qnbtunisia" in url or "qnb.com.tn" in url:
                # QNB specific handling
                time.sleep(4)
                self.driver.execute_script("window.scrollTo(0, 600)")
                
            # General scroll to trigger lazy loading
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight / 3)")
            time.sleep(1)
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight * 2/3)")
            time.sleep(1)
            
        except Exception as e:
            print(f"Special handling failed: {str(e)}")
        finally:
            # Reset timeout to default
            self.driver.set_page_load_timeout(45)

    def _extract_content_with_retry(self, max_attempts=2):
        """Robust content extraction with multiple strategies"""
        for attempt in range(max_attempts):
            try:
                # Wait for page to load with different strategies
                try:
                    WebDriverWait(self.driver, 20).until(
                        lambda driver: driver.execute_script('return document.readyState') == 'complete'
                    )
                except:
                    # Fallback - just wait a bit
                    time.sleep(3)
                
                # Try multiple content extraction strategies
                content_strategies = [
                    self._extract_by_selectors,
                    self._extract_body_content,
                    self._extract_visible_text
                ]
                
                for strategy in content_strategies:
                    content = strategy()
                    if content and len(content.strip()) > 100:  # Minimum content length
                        return content
                
                time.sleep(2 * (attempt + 1))
                
            except Exception as e:
                print(f"Content extraction attempt {attempt + 1} failed: {e}")
                if attempt == max_attempts - 1:
                    raise
                time.sleep(3)
        
        return ""

    def _extract_by_selectors(self):
        """Extract content from specific sections with enhanced selectors"""
        news_keywords = ['news', 'actualité', 'actualites', 'أخبار', 'نبذ', 'حملة', 'campagne', 'promotion', 'عرض', 'événement', 'event']
        content = ""
        
        # Enhanced selectors for Tunisian banks
        selectors = [
            "//*[contains(@class, 'news')]",
            "//*[contains(@class, 'actualite')]",
            "//*[contains(@class, 'actu')]",
            "//*[contains(@class, 'blog')]",
            "//*[contains(@class, 'article')]",
            "//*[contains(@class, 'post')]",
            "//div[contains(@id, 'content')]",
            "//div[contains(@id, 'news')]",
            "//div[contains(@id, 'actualites')]",
            "//section[contains(@class, 'content')]",
            "//main",
            "//article",
            "//div[contains(@class, 'card')]",
            "//div[contains(@class, 'item')]",
            "//li[contains(@class, 'news')]"
        ]
        
        for selector in selectors:
            try:
                elements = self.driver.find_elements(By.XPATH, selector)
                for element in elements:
                    try:
                        text = element.text.strip()
                        if text and (any(keyword in text.lower() for keyword in news_keywords) or len(text) > 50):
                            content += text + "\n\n"
                    except:
                        continue
            except:
                continue
        
        return content

    def _extract_body_content(self):
        """Extract all body content with error handling"""
        try:
            body = self.driver.find_element(By.TAG_NAME, 'body')
            return body.text
        except:
            return ""

    def _extract_visible_text(self):
        """Extract only visible text"""
        try:
            return self.driver.execute_script("""
                return Array.from(document.body.querySelectorAll('*'))
                    .filter(el => {
                        const style = window.getComputedStyle(el);
                        return style.display !== 'none' && 
                               style.visibility !== 'hidden' && 
                               el.offsetParent !== null &&
                               el.textContent.trim().length > 0;
                    })
                    .map(el => el.textContent.trim())
                    .filter(text => text.length > 0)
                    .join('\\n');
            """)
        except:
            return ""

    def _scrape_campaigns_separately(self, bank_name):
        """Scrape campaign pages separately for banks that need it"""
        from banks import CAMPAIGN_URLS
        
        campaign_url = CAMPAIGN_URLS.get(bank_name)
        if not campaign_url:
            return []
        
        try:
            print(f"Scraping campaigns from: {campaign_url}")
            self.driver.get(campaign_url)
            time.sleep(3)
            
            content = self._extract_content_with_retry()
            if not content:
                return []
            
            # Simple campaign extraction (can be enhanced with GROQ later)
            campaigns = []
            lines = content.split('\n')
            for line in lines:
                line = line.strip()
                if line and any(keyword in line.lower() for keyword in ['promo', 'campagne', 'offre', 'عرض', 'حملة']):
                    campaigns.append({"title": line[:100], "description": line})
                    
            return campaigns[:5]  # Limit to 5 campaigns
            
        except Exception as e:
            print(f"Campaign scraping failed: {e}")
            return []

    def scrape(self, bank_info, max_retries: int = 2):
        url = bank_info["url"]
        bank_name = bank_info["name"]
        
        for attempt in range(max_retries):
            try:
                print(f"\nAttempt {attempt+1} for {bank_name}")
                print(f"URL: {url}")
                
                # Navigate to URL with special handling
                self.driver.get(url)
                self._handle_special_banks(bank_info)
                
                # Extract content
                content = self._extract_content_with_retry()
                
                if not content or len(content.strip()) < 50:
                    print("Insufficient content, trying alternative approach...")
                    # Try scrolling more for lazy loading
                    self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
                    time.sleep(2)
                    content = self._extract_content_with_retry()
                
                if not content or len(content.strip()) < 50:
                    raise ValueError("Insufficient content extracted from page")
                
                # Enhanced multilingual prompt for Tunisian context
                prompt = f"""
                ANALYZE THIS TUNISIAN BANK WEBSITE CONTENT AND EXTRACT:

                CONTEXT: {bank_name} website - content in {bank_info.get('language', 'French/Arabic')}

                EXTRACT IN JSON FORMAT:

                1. NEWS/ACTUALITÉS/أخبار (recent articles, press releases, announcements):
                   - Extract titles and 1-sentence summaries
                   - Include dates if available
                   - Focus on financial news, service updates, bank announcements

                2. MARKETING CAMPAIGNS/CAMPAGNES/حملات (promotions, special offers):
                   - Limited-time offers, interest rate specials
                   - New product launches, banking package promotions
                   - Validity periods if mentioned

                3. SERVICE UPDATES (changes, new features):
                   - New branches, digital banking updates
                   - Service interruptions, maintenance notices

                IMPORTANT FOR TUNISIAN BANKS:
                - Look for both French and Arabic content
                - Common terms: "عرض خاص", "حملة ترويجية", "promotion", "offre exclusive", "نشرة إخبارية"
                - Ignore navigation menus, login forms, legal text
                - Focus on time-sensitive, customer-facing content

                URL: {url}
                CONTENT TO ANALYZE (first 3000 characters):
                {content[:3000]}
                """

                response = self.client.chat.completions.create(
                    model="llama3-70b-8192",
                    messages=[
                        {
                            "role": "system", 
                            "content": """You are an expert analyst for Tunisian banking content. 
                            Extract news, campaigns, and updates from bank websites. 
                            Return valid JSON with this structure:
                            {
                                "news": [
                                    {"title": "News title", "summary": "Brief summary", "date": "if available"}
                                ],
                                "campaigns": [
                                    {"title": "Campaign title", "description": "Details", "validity": "if available"}
                                ],
                                "updates": [
                                    {"type": "Update type", "details": "Description"}
                                ]
                            }"""
                        },
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.1,
                    max_tokens=2000,
                    response_format={"type": "json_object"}
                )
                
                data = json.loads(response.choices[0].message.content)
                
                # Additional campaign scraping for specific banks
                if bank_name in ['Attijari Bank', 'Banque Zitouna', 'Amen Bank', 'BIAT', 'ATB']:
                    additional_campaigns = self._scrape_campaigns_separately(bank_name)
                    if additional_campaigns:
                        data['campaigns'].extend(additional_campaigns)
                
                # Validate response structure
                required_keys = ['news', 'campaigns', 'updates']
                if not all(key in data for key in required_keys):
                    raise ValueError("Invalid API response format - missing required keys")
                
                return data
                
            except Exception as e:
                print(f"Attempt {attempt+1} failed: {str(e)}")
                if attempt == max_retries - 1:
                    return {
                        "news": [],
                        "campaigns": [],
                        "updates": [],
                        "error": str(e)
                    }
                # Exponential backoff with longer waits for timeouts
                backoff_time = 3 ** (attempt + 1)
                print(f"Waiting {backoff_time} seconds before retry...")
                time.sleep(backoff_time)

    def close(self):
        if hasattr(self, 'driver'):
            self.driver.quit()
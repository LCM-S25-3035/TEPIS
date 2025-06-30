import csv
import time
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager
from urllib.parse import urljoin

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class EventbriteScraper:
    def __init__(self, delay=2):
        self.delay = delay
        self.base_url = "https://www.eventbrite.com"
        self.start_url = "https://www.eventbrite.com/d/canada/all-events/"
        self.driver = None
        self.event_links = set()  # Use set to avoid duplicates
        
    def setup_driver(self):
        """Setup Chrome driver with appropriate options"""
        chrome_options = Options()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        # Uncomment the line below if you want to run in headless mode
        # chrome_options.add_argument("--headless")
        
        try:
            # Use webdriver-manager to automatically download and manage ChromeDriver
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            logger.info("Chrome driver initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Chrome driver: {e}")
            raise
    
    def wait_for_page_load(self, timeout=10):
        """Wait for page to load completely"""
        try:
            WebDriverWait(self.driver, timeout).until(
                lambda driver: driver.execute_script("return document.readyState") == "complete"
            )
            time.sleep(2)  # Additional wait for JS to render
        except TimeoutException:
            logger.warning("Page load timeout, continuing anyway...")
    
    def scroll_to_load_content(self):
        """Scroll down to load any lazy-loaded content"""
        try:
            last_height = self.driver.execute_script("return document.body.scrollHeight")
            
            while True:
                # Scroll down to bottom
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)
                
                # Calculate new scroll height and compare with last scroll height
                new_height = self.driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    break
                last_height = new_height
                
        except Exception as e:
            logger.warning(f"Error during scrolling: {e}")
    
    def extract_event_links(self):
        """Extract event links from current page"""
        try:
            # Wait for event cards to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "a[class*='event-card-link'], a.event-card-link"))
            )
            
            # Find all event card links
            event_elements = self.driver.find_elements(By.CSS_SELECTOR, "a[class*='event-card-link'], a.event-card-link")
            
            page_links = []
            for element in event_elements:
                try:
                    href = element.get_attribute('href')
                    if href:
                        # Convert relative URLs to absolute URLs
                        full_url = urljoin(self.base_url, href)
                        if full_url not in self.event_links:
                            self.event_links.add(full_url)
                            page_links.append(full_url)
                except Exception as e:
                    logger.warning(f"Error extracting link from element: {e}")
                    continue
            
            logger.info(f"Found {len(page_links)} new event links on current page")
            return page_links
            
        except TimeoutException:
            logger.warning("No event cards found on current page")
            return []
        except Exception as e:
            logger.error(f"Error extracting event links: {e}")
            return []
    
    def find_next_page_button(self):
        """Find and return the next page button if it exists"""
        next_button_selectors = [
            "button[aria-label='Next page']",
            "a[aria-label='Next page']",
            "button[data-testid='pagination-next']",
            "a[data-testid='pagination-next']",
            ".pagination button:last-child",
            ".pagination a:last-child",
            "button:contains('Next')",
            "a:contains('Next')"
        ]
        
        for selector in next_button_selectors:
            try:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                for element in elements:
                    if element.is_enabled() and element.is_displayed():
                        # Check if it's not disabled
                        if "disabled" not in element.get_attribute("class").lower():
                            return element
            except Exception:
                continue
        
        return None
    
    def scrape_all_pages(self):
        """Scrape all pages of events"""
        page_number = 1
        
        try:
            # Load the first page
            logger.info(f"Loading page {page_number}: {self.start_url}")
            self.driver.get(self.start_url)
            self.wait_for_page_load()
            
            while True:
                logger.info(f"Scraping page {page_number}")
                
                # Scroll to load all content
                self.scroll_to_load_content()
                
                # Extract event links from current page
                page_links = self.extract_event_links()
                
                if not page_links:
                    logger.warning(f"No event links found on page {page_number}")
                
                logger.info(f"Total unique events collected so far: {len(self.event_links)}")
                
                # Look for next page button
                next_button = self.find_next_page_button()
                
                if next_button:
                    try:
                        logger.info(f"Navigating to page {page_number + 1}")
                        # Scroll to the button first
                        self.driver.execute_script("arguments[0].scrollIntoView();", next_button)
                        time.sleep(1)
                        
                        # Click the next button
                        next_button.click()
                        
                        # Wait for the new page to load
                        time.sleep(self.delay)
                        self.wait_for_page_load()
                        
                        page_number += 1
                        
                    except Exception as e:
                        logger.error(f"Error clicking next button: {e}")
                        break
                else:
                    logger.info("No more pages found. Scraping completed.")
                    break
                    
                # Rate limiting
                time.sleep(self.delay)
                
        except KeyboardInterrupt:
            logger.info("Scraping interrupted by user")
        except Exception as e:
            logger.error(f"Unexpected error during scraping: {e}")
    
    def save_to_csv(self, filename="eventbrite_events.csv"):
        """Save event links to CSV file"""
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['Event_URL'])  # Header
                
                for link in sorted(self.event_links):  # Sort for consistent output
                    writer.writerow([link])
            
            logger.info(f"Successfully saved {len(self.event_links)} event links to {filename}")
            
        except Exception as e:
            logger.error(f"Error saving to CSV: {e}")
    
    def run(self, output_file="eventbrite_events.csv"):
        """Main method to run the scraper"""
        try:
            logger.info("Starting Eventbrite scraper...")
            self.setup_driver()
            self.scrape_all_pages()
            self.save_to_csv(output_file)
            logger.info(f"Scraping completed! Total events found: {len(self.event_links)}")
            
        except Exception as e:
            logger.error(f"Scraper failed: {e}")
        finally:
            if self.driver:
                self.driver.quit()
                logger.info("Browser closed")

def main():
    """Main function to run the scraper"""
    # You can adjust the delay between requests (in seconds)
    scraper = EventbriteScraper(delay=2)
    
    # Run the scraper and save to CSV
    scraper.run("eventbrite_canada_events.csv")

if __name__ == "__main__":
    main()
# Save this file as indiamart.py
import os
import csv
import logging
import time
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

DEBUG_FOLDER = r"C:\Users\HP\Desktop\AI price comparison\screenshots\debug"
CSV_FILE = r"C:\Users\HP\Desktop\AI price comparison\data\products.csv"

def create_driver():
    options = Options()
    options.headless = True
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36")

    driver_path = ChromeDriverManager().install()
    return uc.Chrome(driver_executable_path=driver_path, options=options)

def save_to_csv(results):
    fieldnames = ["site", "title", "price", "link", "supplier", "rating", "image"]
    existing_rows = []

    if os.path.exists(CSV_FILE):
        with open(CSV_FILE, mode='r', encoding='utf-8') as csvfile:
            existing_rows = list(csv.DictReader(csvfile))

    existing_set = set((row["title"], row["link"]) for row in existing_rows)
    new_rows = [r for r in results if (r["title"], r["link"]) not in existing_set]

    if not new_rows:
        logger.info("📎 No new products to add.")
        return

    with open(CSV_FILE, mode='a', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        if not existing_rows:
            writer.writeheader()
        for result in new_rows:
            writer.writerow(result)

    logger.info(f"✅ {len(new_rows)} new products saved to CSV.")

def scrape_indiamart(query, max_results=15):
    driver = create_driver()
    results = []
    try:
        os.makedirs(DEBUG_FOLDER, exist_ok=True)
        search_url = f"https://dir.indiamart.com/search.mp?ss={query.replace(' ', '+')}"
        logger.info(f"🌐 Searching IndiaMART: {search_url}")

        for attempt in range(3):
            driver.get(search_url)
            try:
                WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, "px-captcha")))
                logger.warning("⚠️ CAPTCHA detected! Retrying after 15s...")
                time.sleep(15)
            except TimeoutException:
                logger.info("✅ No CAPTCHA detected.")
                break
        else:
            logger.error("❌ CAPTCHA Failed after retries.")
            return []

        WebDriverWait(driver, 40).until(EC.presence_of_element_located((By.CSS_SELECTOR, '.card.brs5')))

        product_blocks = driver.find_elements(By.CSS_SELECTOR, '.card.brs5')
        logger.info(f"🔍 Found {len(product_blocks)} products")

        for item in product_blocks:
            try:
                title = item.find_element(By.CSS_SELECTOR, ".producttitle a").text.strip()
                link = item.find_element(By.CSS_SELECTOR, ".producttitle a").get_attribute('href')
                price = item.find_element(By.CSS_SELECTOR, "p.price").text.strip() if item.find_elements(By.CSS_SELECTOR, "p.price") else "Ask Price"
                supplier = item.find_element(By.CSS_SELECTOR, ".companyname a").text.strip() if item.find_elements(By.CSS_SELECTOR, ".companyname a") else "Unknown Supplier"
                rating = item.find_element(By.CSS_SELECTOR, ".ratingValue").text.strip() if item.find_elements(By.CSS_SELECTOR, ".ratingValue") else "No Rating"
                image = item.find_element(By.CSS_SELECTOR, "img.productimg").get_attribute('src') if item.find_elements(By.CSS_SELECTOR, "img.productimg") else ""

                results.append({
                    "site": "Indiamart",
                    "title": title,
                    "price": price,
                    "link": link,
                    "supplier": supplier,
                    "rating": rating,
                    "image": image,
                })
            except Exception as e:
                logger.warning(f"⚠️ Error parsing block: {e}")
                continue

    except Exception as e:
        logger.exception("❌ Error during scraping")
        try:
            ts = time.strftime("%Y%m%d_%H%M%S")
            screenshot_path = os.path.join(DEBUG_FOLDER, f"indiamart_error_{ts}.png")
            driver.save_screenshot(screenshot_path)
            logger.info(f"📸 Screenshot saved at {screenshot_path}")
        except Exception as ss_e:
            logger.error(f"⚠️ Screenshot failed: {ss_e}")
    finally:
        driver.quit()

    # Save results to CSV always (frontend or terminal)
    if results:
        save_to_csv(results)
    return results

# This is only triggered if run directly
if __name__ == "__main__":
    query = input("🔍 Enter search query for IndiaMART: ").strip()
    if query:
        products = scrape_indiamart(query)
        if products:
            for i, result in enumerate(products, 1):
                print(f"\n🔹 Product {i}")
                print(f"Title    : {result['title']}")
                print(f"Price    : {result['price']}")
                print(f"Supplier : {result['supplier']}")
                print(f"Rating   : {result['rating']}")
                print(f"Link     : {result['link']}")
                print(f"Image    : {result['image']}")
                print("-" * 60)
        else:
            print("❌ No results found.")
    else:
        print("❗ Please enter a valid search term.")

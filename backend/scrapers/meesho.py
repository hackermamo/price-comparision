import time
import os
import logging
import traceback
import chromedriver_autoinstaller
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import undetected_chromedriver as uc
import csv

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

CSV_FILE = r"C:\Users\HP\Desktop\AI price comparison\data\meesho_data.csv"

def save_to_csv(results):
    fieldnames = ["site", "title", "price", "link", "rating", "image"]
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

def safe_uc_driver(options):
    try:
        return uc.Chrome(options=options)
    except FileExistsError:
        logger.warning("⚠️ Chrome already patched. Retrying with patch skipped...")
        uc_exe = os.path.expanduser("~\\appdata\\roaming\\undetected_chromedriver\\undetected_chromedriver.exe")
        if os.path.exists(uc_exe):
            return uc.Chrome(options=options, driver_executable_path=uc_exe)
        else:
            raise FileNotFoundError("Undetected ChromeDriver binary not found.")

def scrape_meesho(query):
    logger.info(f"🔍 Query: {query}")
    search_url = f"https://www.meesho.com/search?q={query}"
    logger.info(f"🌐 URL: {search_url}")

    chromedriver_autoinstaller.install()

    options = uc.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-extensions")
    options.page_load_strategy = 'eager'
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
    )

    results = []
    driver = None

    try:
        driver = safe_uc_driver(options)

        driver.execute_cdp_cmd("Network.enable", {})
        driver.execute_cdp_cmd("Network.setUserAgentOverride", {
            "userAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                         "(KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
        })
        driver.execute_cdp_cmd("Network.setExtraHTTPHeaders", {
            "headers": {
                "Referer": "https://www.google.com/",
                "Accept-Language": "en-US,en;q=0.9"
            }
        })

        driver.get(search_url)
        time.sleep(1)  # brief pause to allow basic rendering


        for _ in range(2):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1.2)

        product_cards = driver.find_elements(By.CSS_SELECTOR, "div.NewProductCardstyled__StyledDetailsCard-sc-6y2tys-1")
        if not product_cards:
            product_cards = driver.find_elements(By.CSS_SELECTOR, "div.sc-cWSHoV")

        logger.info(f"📦 Total cards found: {len(product_cards)}")

        for card in product_cards[:15]:
            try:
                title = card.find_element(By.CSS_SELECTOR, "p.NewProductCardstyled__StyledDesktopProductTitle-sc-6y2tys-5").text.strip()
            except:
                title = "N/A"

            try:
                price = card.find_element(By.CSS_SELECTOR, "h5.sc-eDvSVe").text.strip()
            except:
                price = "N/A"

            link = ""
            image = ""
            try:
                parent = card.find_element(By.XPATH, ".//ancestor::a[1]")
                link = parent.get_attribute("href") if parent else ""
                img_elem = parent.find_element(By.TAG_NAME, "img")
                image = img_elem.get_attribute("src") if img_elem else ""
            except:
                try:
                    link_elem = card.find_element(By.TAG_NAME, "a")
                    link = link_elem.get_attribute("href")
                    image = link_elem.find_element(By.TAG_NAME, "img").get_attribute("src")
                except:
                    pass

            try:
                rating = card.find_element(By.CSS_SELECTOR, "div.NewProductCardstyled__RatingsRow-sc-6y2tys-8 span").text.strip()
            except:
                rating = "N/A"

            results.append({
                "site": "meesho",
                "title": title,
                "price": price,
                "link": link,
                "rating": rating,
                "image": image
            })

            logger.info(f"✅ {title} | {price} | {rating}")
    except Exception as e:
        logger.error("❌ Scraping failed:")
        traceback.print_exc()
        if driver:
            driver.save_screenshot("meesho_error.png")
            logger.info("📸 Screenshot saved as meesho_error.png")
    finally:
        if driver:
            driver.quit()
            logger.info("🧹 Driver closed.")

    if not results:
        logger.warning("🚨 No results returned.")
    save_to_csv(results)
    return results


if __name__ == "__main__":
    query = input("🔍 Enter product name: ").strip()
    data = scrape_meesho(query)
    if data:
        logger.info("🔍 Search completed and products scraped.")
    else:
        logger.warning("⚠️ No products found.")

import time
import random
import logging
import os
import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

CSV_FILE = r"C:\Users\HP\Desktop\AI price comparison\data\amazon_data.csv"

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

def scrape_amazon(query, csv_filename=None):
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("start-maximized")
    options.add_argument("disable-infobars")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36"
    )

    proxy = os.getenv("PROXY_SERVER")
    if proxy:
        options.add_argument(f"--proxy-server={proxy}")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    results = []

    try:
        search_url = f"https://www.amazon.in/s?k={query.replace(' ', '+')}"
        logger.info(f"🌐 Searching Amazon: {search_url}")
        driver.get(search_url)

        if "captcha" in driver.page_source.lower():
            raise Exception("⚠️ CAPTCHA encountered on Amazon")

        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.s-main-slot"))
        )

        body = driver.find_element(By.TAG_NAME, "body")
        for _ in range(3):
            body.send_keys(Keys.PAGE_DOWN)
            time.sleep(random.uniform(1, 2))

        product_blocks = driver.find_elements(By.XPATH, "//div[contains(@data-component-type, 's-search-result')]")
        logger.info(f"🔍 Found {len(product_blocks)} product blocks")

        for item in product_blocks:
            try:
                title = "No Title Found"
                try:
                    h2_element = item.find_element(By.TAG_NAME, "h2")
                    aria_label = h2_element.get_attribute("aria-label")
                    if aria_label:
                        title = aria_label.strip()
                    else:
                        span_element = h2_element.find_element(By.TAG_NAME, "span")
                        title = span_element.text.strip()
                except Exception as e:
                    logger.warning(f"⚠️ Error extracting title: {str(e)}")
                    title = "No Title Found"

                link = "#"
                try:
                    link_elem = item.find_element(By.CSS_SELECTOR, "h2 a")
                    href = link_elem.get_attribute("href")
                    if href:
                        if not href.startswith("http"):
                            href = "https://www.amazon.in" + href
                        link = href
                except Exception:
                    asin = item.get_attribute("data-asin")
                    if asin:
                        link = f"https://www.amazon.in/dp/{asin}"
                    else:
                        logger.debug("🔗 No link or ASIN found")

                image = ""
                image_elem = item.find_elements(By.CSS_SELECTOR, "img.s-image")
                if image_elem:
                    image = image_elem[0].get_attribute("src") or image_elem[0].get_attribute("data-src")

                price = "N/A"
                price_whole = item.find_elements(By.CSS_SELECTOR, "span.a-price-whole")
                price_fraction = item.find_elements(By.CSS_SELECTOR, "span.a-price-fraction")
                if price_whole:
                    price = f"₹{price_whole[0].text.strip()}"
                    if price_fraction:
                        price += f".{price_fraction[0].text.strip()}"

                rating = "No Rating"
                rating_elem = item.find_elements(By.XPATH, ".//span[@class='a-icon-alt']")
                if rating_elem:
                    rating = rating_elem[0].text.strip()

                results.append({
                    "site": "Amazon",
                    "title": title,
                    "price": price,
                    "link": link,
                    "image": image,
                    "rating": rating
                })

                if len(results) >= 10:
                    break

            except Exception as e:
                logger.warning(f"⚠️ Error parsing an Amazon item: {str(e)}")
                logger.debug(f"🔎 Item HTML:\n{item.get_attribute('outerHTML')}")
                continue

    except Exception as e:
        driver.save_screenshot("amazon_error.png")
        logger.exception(f"❌ Amazon scraping error: {str(e)}")
        raise e

    finally:
        driver.quit()

    # Save to CSV if filename provided
    if results:
        save_to_csv(results)

    return results

# Terminal Test
if __name__ == "__main__":
    query = input("🔍 Enter product to search on Amazon: ").strip()
    csv_filename = r"C:\Users\HP\Desktop\AI price comparison\data\amazon_data.csv"
    results = scrape_amazon(query, csv_filename)

    print("\n📦 Scraped Results:\n" + "-" * 50)
    for i, item in enumerate(results, 1):
        print(f"{i}. {item['title']}")
        print(f"   🏷️ Price: {item['price']}")
        print(f"   🌟 Rating: {item['rating']}")
        print(f"   🔗 Link: {item['link']}")
        print(f"   🖼️ Image: {item['image']}")
        print("-" * 50)

    print("✅ Scraping completed successfully!")

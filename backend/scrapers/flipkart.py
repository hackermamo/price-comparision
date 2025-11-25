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

def scrape_flipkart(query, max_results=14, headless=True):
    options = Options()
    if headless:
        options.add_argument("--headless=new")
        options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--start-maximized")
    options.add_argument("--disable-infobars")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36")

    proxy = os.getenv("PROXY_SERVER")
    if proxy:
        options.add_argument(f"--proxy-server={proxy}")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    results = []

    try:
        search_url = f"https://www.flipkart.com/search?q={query.replace(' ', '+')}"
        logger.info(f"\u2728 Searching Flipkart: {search_url}")
        driver.get(search_url)

        # Close login popup if appears
        try:
            close_btn = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), '\u2715')]"))
            )
            close_btn.click()
            logger.info("\u2705 Closed login popup")
        except Exception:
            logger.info("\u2139\ufe0f No login popup detected")

        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "a[href][rel='noopener noreferrer']"))
        )

        body = driver.find_element(By.TAG_NAME, "body")
        for _ in range(5):
            body.send_keys(Keys.PAGE_DOWN)
            time.sleep(random.uniform(1.2, 2.0))

        product_links = driver.find_elements(By.CSS_SELECTOR, "a[class^='WKTcLC'][href][rel='noopener noreferrer']")

        if not product_links:
            logger.info("No product links found with the first condition. Using the second condition.")
            product_links = driver.find_elements(By.CSS_SELECTOR, "a[class='wjcEIp'][href][rel='noopener noreferrer']")

        if not product_links:
            logger.info("No product links found with the second condition. Using the third condition.")
            product_links = driver.find_elements(By.CSS_SELECTOR, "a[href][rel='noopener noreferrer']")

        bad_words = ["Add to Compare", "Save", "Wishlist"]

        for link in product_links:
            try:
                href = link.get_attribute("href")
                if not href or "/p/" not in href:
                    continue

                product = {"title": "No Title", "price": "N/A", "rating": "No Rating", "link": href, "image": ""}

                title = link.get_attribute("title") or link.text.strip()

                if any(bad in title for bad in bad_words) or not title.strip():
                    try:
                        img_elem = link.find_element(By.TAG_NAME, "img")
                        title = img_elem.get_attribute("alt") or "No Title"
                        product["image"] = img_elem.get_attribute("src") or img_elem.get_attribute("data-src") or ""
                    except Exception:
                        title = "No Title"

                product["title"] = title.strip()

                try:
                    price_elem = link.find_element(By.XPATH, "./ancestor::div[@data-id]//div[starts-with(@class, 'Nx9bqj')]")
                    product["price"] = price_elem.text.strip()
                except Exception:
                    product["price"] = "N/A"

                try:
                    rating_elem = link.find_element(By.XPATH, "./ancestor::div[@data-id]//div[contains(@class, 'XQDdHH')]")
                    product["rating"] = rating_elem.text.strip()
                except Exception:
                    product["rating"] = "No Rating"

                if not product["image"]:
                    try:
                        image_elem = link.find_element(By.XPATH, "./ancestor::div[@data-id]//img")
                        product["image"] = image_elem.get_attribute("src") or ""
                    except Exception:
                        product["image"] = ""

                results.append(product)

                if len(results) >= max_results:
                    break

            except Exception as e:
                logger.warning(f"\u26a0\ufe0f Error parsing a product link: {e}")
                continue

    except Exception as e:
        driver.save_screenshot("flipkart_error.png")
        logger.exception(f"\u274c Flipkart scraping failed: {e}")
        raise e

    finally:
        driver.quit()
        logger.info("\ud83d\udea9 WebDriver closed")

    # ✅ Save to CSV without duplicates
    csv_path = os.path.join(os.getcwd(), "data","flipkart_results.csv")
    existing_links = set()
    if os.path.exists(csv_path):
        try:
            with open(csv_path, mode="r", encoding="utf-8") as file:
                reader = csv.DictReader(file)
                for row in reader:
                    existing_links.add(row["link"])
        except Exception as e:
            logger.error(f"⚠️ Failed to read existing CSV: {e}")

    unique_new_results = [item for item in results if item["link"] not in existing_links]

    if unique_new_results:
        try:
            file_exists = os.path.exists(csv_path)
            with open(csv_path, mode="a", newline="", encoding="utf-8") as file:
                writer = csv.DictWriter(file, fieldnames=["title", "price", "rating", "link", "image"])
                if not file_exists:
                    writer.writeheader()
                writer.writerows(unique_new_results)
            logger.info(f"\U0001F4C2 {len(unique_new_results)} new results appended to {csv_path}")
        except Exception as e:
            logger.error(f"\u274c Failed to append results to CSV: {e}")
    else:
        logger.info("✅ No new unique results to append.")

    return results

if __name__ == "__main__":
    query = input("Enter product to search on Flipkart: ").strip()
    results = scrape_flipkart(query, max_results=10, headless=False)

    print("\nScraped Results:\n" + "-" * 70)
    for i, item in enumerate(results, 1):
        print(f"{i}. {item['title']}")
        print(f"   Price : {item['price']}")
        print(f"   Rating: {item['rating']}")
        print(f"   Link  : {item['link']}")
        print(f"   Image : {item['image']}")
        print("-" * 70)

    print("Scraping completed successfully!")

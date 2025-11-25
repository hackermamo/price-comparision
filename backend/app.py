from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from scrapers.amazon import scrape_amazon
from scrapers.flipkart import scrape_flipkart
from scrapers.meesho import scrape_meesho
from scrapers.indiamart import scrape_indiamart
from recommender import get_recommendations
import logging
import os
import csv
from datetime import datetime
import pandas as pd

# ✅ Corrected __name__ and static/template paths
app = Flask(__name__, template_folder='./templates', static_folder='../static')
CORS(app)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 🔒 History file path
HISTORY_FILE = os.path.join(os.getcwd(), "search_history.csv")

# ✅ CSV files to load products from
CSV_FILES = [
    "amazon_data.csv",
    "flipkart_results.csv",
    "meesho_data.csv",
    "products.csv"
]

def save_search_query(query):
    os.makedirs(os.path.dirname(HISTORY_FILE), exist_ok=True)
    with open(HISTORY_FILE, mode='a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([datetime.now().strftime("%Y-%m-%d %H:%M:%S"), query])

def load_search_history():
    if not os.path.exists(HISTORY_FILE):
        return []
    with open(HISTORY_FILE, mode='r', encoding='utf-8') as f:
        reader = csv.reader(f)
        return [{"time": row[0], "query": row[1]} for row in reader]

# ✅ Load product data from all CSV files
def load_csv_products():
    products = []
    for file_name in CSV_FILES:
        if os.path.exists(file_name):
            try:
                df = pd.read_csv(file_name)
                for _, row in df.iterrows():
                    products.append({
                        "title": row.get("title", "No Title"),
                        "price": row.get("price", "N/A"),
                        "rating": row.get("rating", "N/A"),
                        "link": row.get("link", "#"),
                        "image": row.get("image", "/static/default.jpg")  # default image fallback
                    })
            except Exception as e:
                logger.error(f"Failed to load {file_name}: {e}")
    return products

@app.route("/")
def index():
    history = load_search_history()
    products = load_csv_products()  # ✅ Load products from CSVs
    return render_template("index.html", history=history, products=products)

@app.route("/search", methods=["POST"])
def search():
    data = request.get_json()
    query = data.get("query", "")

    if not query.strip():
        return jsonify({"error": "Query is required"}), 400

    query = query.strip().lower()
    save_search_query(query)
    logger.info(f"🔍 Searching for: {query}")

    results = {
        "amazon": [],
        "flipkart": [],
        "meesho": [],
        "indiamart": [],
        "recommendations": [],
        "errors": {}
    }

    try:
        results["amazon"] = scrape_amazon(query)
    except Exception as e:
        logger.error(f"❌ Amazon scraper failed: {e}")
        results["errors"]["amazon"] = str(e)

    try:
        results["flipkart"] = scrape_flipkart(query)
    except Exception as e:
        logger.error(f"❌ Flipkart scraper failed: {e}")
        results["errors"]["flipkart"] = str(e)

    try:
        results["meesho"] = scrape_meesho(query)
    except Exception as e:
        logger.error(f"❌ Meesho scraper failed: {e}")
        results["errors"]["meesho"] = str(e)

    try:
        results["indiamart"] = scrape_indiamart(query)
    except Exception as e:
        logger.error(f"❌ IndiaMART scraper failed: {e}")
        results["errors"]["indiamart"] = str(e)

    try:
        results["recommendations"] = get_recommendations(query)
    except Exception as e:
        logger.error(f"❌ Recommender failed: {e}")
        results["errors"]["recommendations"] = str(e)

    return jsonify(results)

@app.route("/clear-history", methods=["POST"])
def clear_history():
    try:
        if os.path.exists(HISTORY_FILE):
            os.remove(HISTORY_FILE)
            return jsonify({"message": "🧹 Search history cleared."}), 200
        return jsonify({"message": "No history to clear."}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/health")
def health():
    return jsonify({"status": "ok"})

if __name__ == "__main__":  
    app.run(debug=True, host="127.0.0.1", port=5050)

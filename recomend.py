from flask import Flask, render_template, jsonify
import pandas as pd
import random
import os
from flask import Flask, render_template


app = Flask(__name__, template_folder='backend/templates',static_folder='static')
DATA_DIR = r"C:\Users\HP\Desktop\AI price comparison\data"

# Load 1 random product from a specific site
def load_one_product(site_name):
    filepath = os.path.join(DATA_DIR, f"{site_name}.csv")
    if os.path.exists(filepath):
        df = pd.read_csv(filepath)
        product = df.sample(1).to_dict('records')[0]
        return product
    return {}

@app.route('/')
def index():
    product_blocks = {}
    for site in ['amazon', 'flipkart', 'meesho', 'indiamart']:
        product_blocks[site] = load_one_product(site)
    return render_template('index.html', product_blocks=product_blocks)

@app.route('/product/<site>/<int:index>')
def product_detail(site, index):
    df = pd.read_csv(os.path.join(DATA_DIR, f"{site}.csv"))
    product = df.iloc[index].to_dict()
    return render_template('product.html', product=product)

@app.route('/refresh/<site>')
def refresh_product(site):
    product = load_one_product(site)
    return jsonify(product)

if __name__ == "__main__":  
    app.run(debug=True, host="127.0.0.1", port=5000)
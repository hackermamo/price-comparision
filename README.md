# AI Price Comparison

A web-based price comparison tool that scrapes product data from multiple e-commerce platforms (Amazon, Flipkart, Meesho, and IndiaMART) to help users find the best deals.

## Features

- **Multi-Platform Scraping**: Aggregates product data from Amazon, Flipkart, Meesho, and IndiaMART
- **Dark Mode**: Toggle between light and dark themes
- **Search History**: Keeps track of your recent searches
- **Responsive Design**: Works seamlessly on desktop and mobile devices
- **Price Comparison**: View and compare prices across different platforms
- **Product Details**: Displays product titles, prices, ratings, images, and direct links

## Project Structure

```
├── backend/
│   ├── app.py                 # Flask backend server
│   ├── recommender.py         # Product recommendation logic
│   ├── utils.py               # Utility functions
│   ├── scrapers/
│   │   ├── amazon.py          # Amazon scraper
│   │   ├── flipkart.py        # Flipkart scraper
│   │   ├── meesho.py          # Meesho scraper
│   │   └── indiamart.py       # IndiaMART scraper
│   └── templates/             # HTML templates
├── static/
│   ├── script.js              # Frontend JavaScript
│   ├── styles.css             # Stylesheet
│   └── js/                    # Additional JS files
├── data/
│   ├── amazon_data.csv        # Amazon products data
│   ├── flipkart_results.csv   # Flipkart products data
│   ├── meesho_data.csv        # Meesho products data
│   └── products.csv           # IndiaMART products data
├── screenshots/               # Debug screenshots
├── index.html                 # Main HTML file
└── README.md                  # This file
```

## Technologies Used

- **Backend**: Python, Flask
- **Web Scraping**: Selenium, Undetected ChromeDriver
- **Frontend**: HTML, CSS, JavaScript
- **Data Storage**: CSV files
- **Automation**: ChromeDriver Manager, WebDriver Manager

## Installation

### Prerequisites

- Python 3.8+
- Chrome/Chromium browser
- pip package manager

### Setup

1. **Clone the repository**
```bash
git clone <repository-url>
cd "AI price comparison"
```

2. **Install Python dependencies**
```bash
pip install selenium webdriver-manager undetected-chromedriver flask
```

3. **Run the Flask backend**
```bash
cd backend
python app.py
```

4. **Access the application**
Open your browser and navigate to `http://localhost:5000`

## Usage

### Searching for Products

1. Enter a product name in the search box
2. Select platforms to search (Amazon, Flipkart, Meesho, IndiaMART)
3. View results sorted by price
4. Click on products to visit the store page

## Scrapers

### Amazon Scraper
- Extracts product title, price, rating, image, and link
- Handles pagination
- Saves results to amazon_data.csv

### Flipkart Scraper
- Scrapes Flipkart product listings
- Extracts pricing and product details
- Saves to flipkart_results.csv

### Meesho Scraper
- Uses undetected ChromeDriver to bypass bot detection
- Collects product information from Meesho
- Stores data in meesho_data.csv

### IndiaMART Scraper
- Scrapes IndiaMART marketplace
- Handles dynamic content loading
- Saves to products.csv

## Data Format

All scraped data is stored in CSV format with the following fields:
- `site`: Source platform (Amazon, Flipkart, Meesho, IndiaMART)
- `title`: Product title
- `price`: Product price
- `link`: Direct product link
- `rating`: Product rating (if available)
- `image`: Product image URL

## Troubleshooting

- **Amazon 503 Error**: Amazon blocks automated access. Use rotating proxies or add delays between requests.
- **Meesho Detection**: The scraper uses undetected ChromeDriver. Ensure it's up to date.
- **Missing Data**: Some fields may be empty if not available on the platform.

## License

This project is licensed under the MIT License.

## Disclaimer

This tool is for educational purposes only. Always respect the `robots.txt` and terms of service of the websites being scraped.

## Contact & Support

For issues, questions, or suggestions, please open an issue in the repository.


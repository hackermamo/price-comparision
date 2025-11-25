from textblob import TextBlob
import difflib

# Predefined related accessories
accessory_map = {
    "iphone": ["iPhone Case", "Apple Watch", "AirPods"],
    "samsung": ["Samsung Buds", "Galaxy Watch", "Fast Charger"],
    "laptop": ["Laptop Stand", "Cooling Pad", "Wireless Mouse"],
    "tv": ["TV Wall Mount", "Streaming Stick", "Soundbar"],
    "headphone": ["Protective Case", "Bluetooth Transmitter", "Audio Splitter"],
    "earbuds": ["Protective Case", "Bluetooth Transmitter", "Audio Splitter"],
    "smartwatch": ["Extra Straps", "Screen Guard", "Charger Dock"],
    "macbook": ["USB-C Hub", "Laptop Sleeve", "Apple Mouse"],
    "camera": ["Tripod", "Camera Bag", "Extra Battery"],
    "printer": ["Ink Refill", "Paper Pack", "Printer Cable"],
    "router": ["WiFi Extender", "LAN Cable", "Router Stand"],
    "milk": ["Milk Bottle", "Organic Milk Pack", "Flavored Milk"],
    "bread": ["Brown Bread", "Garlic Bread", "Multigrain Bread"],
    "butter": ["Peanut Butter", "Salted Butter", "Unsalted Butter"],
    "rice": ["Basmati Rice", "Brown Rice", "Jasmine Rice"],
    "oil": ["Olive Oil", "Mustard Oil", "Sunflower Oil"]
}

def get_recommendations(query):
    query = query.lower()
    blob = TextBlob(query)
    nouns = [word.lower() for word, tag in blob.tags if tag.startswith("NN") ]

    recommendations = []
    seen_names = set()

    def create_item(name):
        title = name.title()
        if title not in seen_names:
            seen_names.add(title)
            return {
                "name": title,
                "image": f"https://via.placeholder.com/100?text={title.replace(' ', '+')}"
            }
        return None

    # Full match on whole query
    full_match = difflib.get_close_matches(query, accessory_map.keys(), n=1, cutoff=0.7)
    if full_match:
        for item in accessory_map[full_match[0]]:
            data = create_item(item)
            if data:
                recommendations.append(data)

    # Partial match on nouns in query
    if not recommendations:
        for noun in nouns:
            match = difflib.get_close_matches(noun, accessory_map.keys(), n=1, cutoff=0.6)
            if match:
                for item in accessory_map[match[0]]:
                    data = create_item(item)
                    if data:
                        recommendations.append(data)

    # Smart fallback if no matches found
    if not recommendations:
        keywords = query.split()[:3]
        for word in keywords:
            word = word.strip().title()
            for phrase in [
                f"Top Deals on {word}",
                f"Best Offers for {word}",
                f"Affordable {word}s"
            ]:
                data = create_item(phrase)
                if data:
                    recommendations.append(data)

    return recommendations or [{
        "name": "Popular Items",
        "image": "https://via.placeholder.com/100?text=Explore+More"
    }]
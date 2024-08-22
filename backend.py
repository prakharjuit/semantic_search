from flask import Flask, request, render_template, jsonify
import pandas as pd
import spacy
from spellchecker import SpellChecker

app = Flask(__name__)

# Load the spaCy model and dataset
nlp = spacy.load("en_core_web_sm")
df = pd.read_csv('product list.csv')

# Initialize spell checker
spell = SpellChecker(language=None)  # Initialize without default language
hindi_words = [
    'chini', 'chawal', 'makhan', 'tel', 'namak', 'masale', 'dal', 'doodh', 
    'pasta', 'aata', 'biscuit', 'paneer', 'haldi', 'mirch', 'pyaz', 'lahsun', 
    'nariyal', 'adrak', 'badam', 'cheeni', 'ghee', 'makhana', 'moong', 'rajma', 
    'masoor', 'chana', 'besan', 'bhindi', 'gobi', 'tamatar', 'kaddu', 'mooli', 
    'palak', 'baingan'
]
spell.word_frequency.load_words(hindi_words)  # Add Hindi terms to spell checker
spell.word_frequency.load_words(df['Product Name'].str.lower().str.split().explode().unique())  # Add product names to spell checker

# Define Hindi to English mapping based on the unique products identified
hindi_to_english = {
    'chini': 'sugar',       # Chini is Sugar in English
    'chawal': 'rice',       # Chawal is Rice in English
    'makhan': 'butter',     # Makhan is Butter in English
    'tel': 'oil',           # Tel is Oil in English
    'namak': 'salt',        # Namak is Salt in English
    'masale': 'spices',     # Masale is Spices in English
    'dal': 'lentils',       # Dal is Lentils in English
    'doodh': 'milk',        # Doodh is Milk in English
    'pasta': 'pasta',       # Pasta remains Pasta
    'aata': 'flour',        # Aata is Flour in English
    'biscuit': 'biscuits',  # Biscuit remains Biscuits
    'paneer': 'cottage cheese', # Paneer is Cottage Cheese in English
    'haldi': 'turmeric',    # Haldi is Turmeric in English
    'mirch': 'chilli',      # Mirch is Chilli in English
    'pyaz': 'onion',        # Pyaz is Onion in English
    'lahsun': 'garlic',     # Lahsun is Garlic in English
    'nariyal': 'coconut',   # Nariyal is Coconut in English
    'adrak': 'ginger',      # Adrak is Ginger in English
    'badam': 'almonds',     # Badam is Almonds in English
    'cheeni': 'sugar',      # Cheeni is also Sugar in English
    'ghee': 'ghee',         # Ghee remains Ghee
    'makhana': 'foxnuts',   # Makhana is Foxnuts in English
    'moong': 'green gram',  # Moong is Green Gram in English
    'rajma': 'kidney beans',# Rajma is Kidney Beans in English
    'masoor': 'red lentils',# Masoor is Red Lentils in English
    'chana': 'chickpeas',   # Chana is Chickpeas in English
    'besan': 'gram flour',  # Besan is Gram Flour in English
    'bhindi': 'okra',       # Bhindi is Okra in English
    'gobi': 'cauliflower',  # Gobi is Cauliflower in English
    'tamatar': 'tomato',    # Tamatar is Tomato in English
    'kaddu': 'pumpkin',     # Kaddu is Pumpkin in English
    'mooli': 'radish',      # Mooli is Radish in English
    'palak': 'spinach',     # Palak is Spinach in English
    'baingan': 'eggplant',  # Baingan is Eggplant in English
    # Add more mappings as required
}

@app.route('/')
def home():
    return render_template('search.html')

@app.route('/search', methods=['POST'])
def search():
    query = request.form['query']
    corrected_query = correct_spelling(query)
    results = search_products(corrected_query, df)
    return render_template('results.html', results=results.to_dict(orient='records'))

@app.route('/suggestions', methods=['GET'])
def suggestions():
    term = request.args.get('term', '')
    corrected_term = correct_spelling(term)
    suggestions = get_suggestions(corrected_term, df)
    return jsonify(suggestions)

def correct_spelling(query):
    corrected_query = ' '.join([spell.correction(word) for word in query.split()])
    return corrected_query

def search_products(query, df):
    doc = nlp(query)
    keyword = None
    price_limit = None
    comparator = None

    for token in doc:
        if token.pos_ == 'NOUN':
            keyword = token.text.lower()
            if keyword in hindi_to_english:
                keyword = hindi_to_english[keyword]
        if token.like_num:
            price_limit = float(token.text)
        if token.text in ['under', 'below', 'less']:
            comparator = 'below'
        if token.text in ['above', 'over', 'more']:
            comparator = 'above'
    
    if keyword and price_limit and comparator:
        if comparator == 'below':
            result = df[(df['Product Name'].str.contains(keyword, case=False)) & (df['Product Price'] <= price_limit)]
        elif comparator == 'above':
            result = df[(df['Product Name'].str.contains(keyword, case=False)) & (df['Product Price'] >= price_limit)]
    elif keyword and price_limit:
        result = df[(df['Product Name'].str.contains(keyword, case=False)) & (df['Product Price'] <= price_limit)]
    elif keyword:
        result = df[df['Product Name'].str.contains(keyword, case=False)]
    elif price_limit:
        result = df[df['Product Price'] <= price_limit]
    else:
        result = df

    return result

def get_suggestions(term, df):
    term = term.lower()
    if term in hindi_to_english:
        term = hindi_to_english[term]
    suggestions = df[df['Product Name'].str.contains(term, case=False, na=False)]['Product Name'].unique().tolist()
    return suggestions

if __name__ == '__main__':
    app.run(debug=True)

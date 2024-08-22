import pandas as pd
import spacy

# Load the dataset
df = pd.read_csv('product list.csv')

# Load the spaCy model
nlp = spacy.load("en_core_web_sm")

# Define the search function
def search_products(query, df):
    doc = nlp(query)
    keyword = None
    price_limit = None
    comparator = None

    for token in doc:
        if token.pos_ == 'NOUN':
            keyword = token.text
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


# Example search query
query = "peanut butter under 400"
results = search_products(query, df)
print(results.head())

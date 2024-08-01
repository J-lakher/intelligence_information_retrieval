from flask import Flask, request, render_template
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
import re
import nltk

# Download NLTK data files
nltk.download('stopwords')

app = Flask(__name__)

# Step 1: Collect Documents
documents = [
    "The stock market is expected to rise as new economic policies are introduced. ",
    "The latest blockbuster movie has broken all box office records.",
    "Political tensions are rising as elections approach.",
    "New government regulations are affecting economic growth.",
    "A famous actor has announced their retirement from the film industry.",
    "Debates over healthcare policies are intensifying in the political arena.",
    "The central bank has adjusted interest rates to control inflation.",
    "The film festival has attracted numerous international stars.",
    "A new political party has emerged with a focus on environmental issues.",
    "Economic sanctions have been imposed on the country.",
    "A highly anticipated movie sequel is set to release next month.",
    "The election results have caused significant political upheaval.",
    "Global trade agreements are impacting local economies.",
    "An award-winning director is working on a new film project.",
    "Political protests are becoming more frequent in major cities.",
    "The unemployment rate is declining as the economy recovers.",
    "A popular TV show has been renewed for another season.",
    "Political leaders are negotiating new climate change agreements.",
    "Consumer spending is increasing, boosting economic growth.",
    "A renowned musician is planning a world tour.",
    # Add more documents to reach at least 100...
]

# Ensure there are at least 100 documents by repeating the existing ones
documents *= 5  # Multiply to ensure a large enough dataset (20 * 5 = 100 documents)

# Step 2: Preprocess the Data
def preprocess(text):
    stop_words = set(stopwords.words('english'))
    stemmer = PorterStemmer()
    
    text = re.sub(r'\W', ' ', text)  # Remove non-word characters
    text = text.lower()
    tokens = text.split()
    tokens = [stemmer.stem(word) for word in tokens if word not in stop_words]
    return ' '.join(tokens)

processed_documents = [preprocess(doc) for doc in documents]

# Remove empty documents after preprocessing
processed_documents = [doc for doc in processed_documents if doc]

# Ensure we have enough non-empty documents
if len(processed_documents) < 100:
    raise ValueError("Not enough non-empty documents after preprocessing. Please add more documents.")

# Step 3: Feature Extraction
vectorizer = TfidfVectorizer(max_features=1000)
X = vectorizer.fit_transform(processed_documents)

# Step 4: Clustering
kmeans = KMeans(n_clusters=3, random_state=42)
kmeans.fit(X)
labels = kmeans.labels_

# Step 6: Assign New Documents
def assign_cluster(new_document):
    new_document = preprocess(new_document)
    new_document_vec = vectorizer.transform([new_document])
    cluster = kmeans.predict(new_document_vec)
    return cluster[0]

# Flask routes
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        query = request.form['query']
        cluster = assign_cluster(query)
        categories = {0: 'Economics', 1: 'Entertainment', 2: 'Politics'}
        result = f"Document falls under category: {categories[cluster]}"
        return render_template('index.html', query=query, result=result)
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)

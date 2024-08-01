from flask import Flask, request, render_template, redirect, url_for
import json
import subprocess
import os

app = Flask(__name__)

crawler_process = None
crawler_interval = 300  # 5 minutes

def start_crawler():
    global crawler_process
    if not crawler_process:
        crawler_process = subprocess.Popen(['python', 'crawler.py'])
        print("Crawler started.")

def stop_crawler():
    global crawler_process
    if crawler_process:
        crawler_process.terminate()
        crawler_process.wait()
        crawler_process = None
        print("Crawler stopped.")

def load_publications():
    if not os.path.exists('publications.json'):
        print("No data available. Please wait for the crawler to complete its first run.")
        return []
    with open('publications.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def search_publications(query):
    publications = load_publications()
    if not publications:
        return []
    
    query_lower = query.lower()
    results = []
    
    for pub in publications:
        if (query_lower in pub['Title'].lower() or
            any(query_lower in author['name'].lower() for author in pub['Authors']) or
            (pub['Year'] and query_lower in pub['Year'])):
            results.append(pub)
    
    return results

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        query = request.form['query']
        results = search_publications(query)
        return render_template('index.html', query=query, results=results)
    return render_template('index.html', query=None, results=None)

if __name__ == "__main__":
    start_crawler()
    try:
        app.run(debug=True)
    finally:
        stop_crawler()

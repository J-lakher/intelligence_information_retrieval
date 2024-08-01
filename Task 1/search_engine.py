import json
import time
import threading
import subprocess
import webbrowser
import os

crawler_process = None
crawler_interval = 300  #5 mins

def start_crawler():
    global crawler_process
    crawler_process = subprocess.Popen(['python', 'crawler.py'])
    print("Crawler started.")

def stop_crawler():
    global crawler_process
    if crawler_process:
        crawler_process.terminate()
        crawler_process.wait()
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

def beautify_results(results):
    formatted_results = []
    for idx, result in enumerate(results, start=1):
        authors = ", ".join([f"{author['name']} ({author['link']})" for author in result['Authors']])
        formatted_result = (f"Result {idx}:\n"
                            f"Title: {result['Title']}\n"
                            f"Authors: {authors}\n"
                            f"Year: {result['Year']}\n"
                            f"Link: {result['Link']}\n")
        formatted_results.append(formatted_result)
    
    return "\n\n".join(formatted_results)

def clear_console():
    os.system('cls' if os.name == 'nt' else 'clear')

def main():
    start_crawler()
    try:
        next_crawl = time.time() + crawler_interval
        while True:
            clear_console()
            time_remaining = int(next_crawl - time.time())
            if time_remaining < 0:
                next_crawl = time.time() + crawler_interval
                time_remaining = int(next_crawl - time.time())
                
            print(f"Next crawl in {time_remaining // 60} minutes and {time_remaining % 60} seconds.")
            
            query = input("Enter your search query (or type 'exit' to quit): ").strip()
            if query.lower() == 'exit':
                break
            if not query:
                continue

            clear_console()
            time_remaining = int(next_crawl - time.time())
            print(f"Next crawl in {time_remaining // 60} minutes and {time_remaining % 60} seconds.")
            
            start_time = time.time()
            results = search_publications(query)
            end_time = time.time()

            print(f"\nSearch completed in {end_time - start_time:.2f} seconds.\n")
            print("="*50)
            print("\nSearch Results:\n")
            
            if results:
                print(beautify_results(results))
                print("\nTo open a result, type the result number (e.g., '1' to open the first result).")
                while True:
                    selection = input("Enter result number to open the link, 'n' to start a new search, or 'exit' to quit: ").strip()
                    if selection.lower() == 'n':
                        break
                    elif selection.lower() == 'exit':
                        return
                    elif selection.isdigit() and 1 <= int(selection) <= len(results):
                        webbrowser.open(results[int(selection) - 1]['Link'])
                    else:
                        print("Invalid selection. Please try again.")
            else:
                print("No results found. Please try a different query.")
                print("Please wait to refresh....")
                time.sleep(3)

    except KeyboardInterrupt:
        pass
    finally:
        stop_crawler()
        print("Search engine stopped.")

if __name__ == "__main__":
    main()

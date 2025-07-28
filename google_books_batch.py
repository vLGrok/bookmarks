import re
import csv
import requests
import sys
import time
import os

MD_FILE = "wealth-reading-list.md"
CSV_FILE = "books_output.csv"
API_KEY = None
API_URL = "https://www.googleapis.com/books/v1/volumes"

# Read API key from books-api-cli.key if present
def get_api_key():
    key_file = "books-api-cli.key"
    if os.path.exists(key_file):
        with open(key_file, encoding="utf-8") as f:
            for line in f:
                if line.startswith("key:"):
                    return line.split(":", 1)[1].strip()
    return None

# Regex to match table rows
ROW_RE = re.compile(r"^\|\s*(.*?)\s*\|\s*(.*?)\s*\|\s*(.*?)\s*\|\s*(.*?)\s*\|\s*(.*?)\s*\|$")

def extract_books(md_path):
    books = []
    with open(md_path, encoding="utf-8") as f:
        for line in f:
            m = ROW_RE.match(line)
            if m:
                # Extract columns
                category, year, rating, author, title = m.groups()
                # Only process rows with placeholders (skip header/separators)
                if author and title and author != "Author" and title != "Title":
                    books.append({
                        "author": author.strip(),
                        "title": title.strip()
                    })
    return books


def query_google_books(author, title, api_key, max_retries=5):
    params = {
        "q": f"inauthor:{author} intitle:{title}",
        "key": api_key
    }
    backoff = 1
    for attempt in range(max_retries):
        try:
            resp = requests.get(API_URL, params=params, timeout=10)
            if resp.status_code == 429:
                print(f"429 Too Many Requests for {author} - {title}. Backing off for {backoff} seconds...")
                time.sleep(backoff)
                backoff = min(backoff * 2, 60)
                continue
            resp.raise_for_status()
            data = resp.json()
            if "items" in data and len(data["items"]):
                info = data["items"][0]["volumeInfo"]
                year = info.get("publishedDate", "")
                rating = info.get("averageRating", "")
                # Use first author if multiple
                author_out = info.get("authors", [author])[0]
                title_out = info.get("title", title)
                return author_out, title_out, year, rating
            break
        except Exception as e:
            print(f"Error for {author} - {title}: {e}")
            time.sleep(backoff)
            backoff = min(backoff * 2, 60)
    return author, title, "", ""


def main():
    global API_KEY
    API_KEY = get_api_key()
    if not API_KEY:
        print("API key not found. Please create books-api-cli.key with 'key: YOUR_KEY' in the current directory.")
        sys.exit(1)
    books = extract_books(MD_FILE)
    with open(CSV_FILE, "w", newline='', encoding="utf-8") as f:
        writer = csv.writer(f, delimiter='|')
        writer.writerow(["Author", "Title", "Year", "Rating"])
        for book in books:
            author, title, year, rating = query_google_books(book["author"], book["title"], API_KEY)
            writer.writerow([author, title, year, rating])
            time.sleep(0.2)  # Be nice to API
    print(f"Wrote {len(books)} entries to {CSV_FILE}")

if __name__ == "__main__":
    main()

#!/bin/zsh

# Usage: ./google_books_query.sh "Author Name" "Book Title" "YOUR_API_KEY"

AUTHOR="$1"
TITLE="$2"
API_KEY="$3"
QUERY="${AUTHOR// /+}+${TITLE// /+}"
URL="https://www.googleapis.com/books/v1/volumes?q=inauthor:${AUTHOR// /+}+intitle:${TITLE// /+}&key=${API_KEY}"

# Query Google Books API and parse first result
RESPONSE=$(curl -s "$URL")

# Extract fields using jq
BOOK_TITLE=$(echo "$RESPONSE" | jq -r '.items[0].volumeInfo.title // ""')
BOOK_AUTHOR=$(echo "$RESPONSE" | jq -r '.items[0].volumeInfo.authors[0] // ""')
BOOK_YEAR=$(echo "$RESPONSE" | jq -r '.items[0].volumeInfo.publishedDate // ""')
BOOK_RATING=$(echo "$RESPONSE" | jq -r '.items[0].volumeInfo.averageRating // ""')

# Output to CSV file in current directory
CSV_FILE="books_output.csv"

# Overwrite CSV file each run
echo "Author|Title|Year|Rating" > "$CSV_FILE"
echo "$BOOK_AUTHOR|$BOOK_TITLE|$BOOK_YEAR|$BOOK_RATING" >> "$CSV_FILE"

echo "Saved: $BOOK_AUTHOR|$BOOK_TITLE|$BOOK_YEAR|$BOOK_RATING to $CSV_FILE"
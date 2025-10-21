# String Analyzer Service

A RESTful API service for analyzing strings and storing their computed properties.

## Features
- Analyze and store string properties (length, palindrome, unique characters, word count, sha256 hash, character frequency map)
- Retrieve a specific string and its properties
- List all strings with advanced filtering
- Filter using natural language queries
- Delete a string

## Endpoints

### 1. Create/Analyze String
- **POST** `/strings`
- **Request Body:**
  ```json
  { "value": "string to analyze" }
  ```
- **Success Response (201):**
  ```json
  {
    "id": "sha256_hash_value",
    "value": "string to analyze",
    "properties": {
      "length": 17,
      "is_palindrome": false,
      "unique_characters": 12,
      "word_count": 3,
      "sha256_hash": "abc123...",
      "character_frequency_map": { "s": 2, "t": 3, ... }
    },
    "created_at": "2025-08-27T10:00:00Z"
  }
  ```

### 2. Get Specific String
- **GET** `/strings/{string_value}`

### 3. Get All Strings with Filtering
- **GET** `/strings?is_palindrome=true&min_length=5&max_length=20&word_count=2&contains_character=a`

### 4. Natural Language Filtering
- **GET** `/strings/filter-by-natural-language?query=all%20single%20word%20palindromic%20strings`

### 5. Delete String
- **DELETE** `/strings/{string_value}`

## Setup Instructions

1. **Clone the repository:**
   ```sh
   git clone <your-repo-url>
   cd string-analyser_service
   ```
2. **Install dependencies:**
   ```sh
   pip install -r requirements.txt
   ```
3. **Run the server:**
   ```sh
   uvicorn main:app --reload
   ```

## Dependencies
- fastapi
- uvicorn

## Environment Variables
None required.

## Notes
- All data is stored in memory and will be lost when the server restarts.
- Test endpoints using tools like Postman or curl.

## License
GMK


### Author
Name: Usman Ghamzaki Abdulhamid
Email: uthmanghamaki@gmail.com
Github: @Ghamzaki

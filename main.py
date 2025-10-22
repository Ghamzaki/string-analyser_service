from fastapi import FastAPI, HTTPException, status, Query
from datetime import datetime, timezone
import hashlib
from typing import Dict, Any, List, Optional

app = FastAPI()

# Store strings by their sha256 hash
string_db: Dict[str, Dict[str, Any]] = {}

# Helper function to analyze string
def analyze_string(value: str) -> Dict[str, Any]:
    value_lower = value.lower()
    chars_no_space = [ch for ch in value if not ch.isspace()]
    return {
        "length": len(value),
        "is_palindrome": value_lower == value_lower[::-1],
        "unique_characters": len(set(chars_no_space)),
        "word_count": len(value.split()),
        "sha256_hash": hashlib.sha256(value.encode()).hexdigest(),
        "character_frequency_map": {ch: chars_no_space.count(ch) for ch in set(chars_no_space)}
    }

@app.post("/strings", status_code=status.HTTP_201_CREATED)
def create_string(payload: Dict[str, Any]):
    value = payload.get("value")
    if value is None:
        raise HTTPException(status_code=400, detail='Missing "value" field')
    if not isinstance(value, str):
        raise HTTPException(status_code=422, detail='"value" must be a string')
    sha256_hash = hashlib.sha256(value.encode()).hexdigest()
    if sha256_hash in string_db:
        raise HTTPException(status_code=409, detail='String already exists')
    properties = analyze_string(value)
    created_at = datetime.now(timezone.utc).isoformat()
    string_db[sha256_hash] = {
        "id": sha256_hash,
        "value": value,
        "properties": properties,
        "created_at": created_at
    }
    return string_db[sha256_hash]

@app.get("/strings/{string_value}")
def get_string(string_value: str):
    sha256_hash = hashlib.sha256(string_value.encode()).hexdigest()
    result = string_db.get(sha256_hash)
    if not result:
        raise HTTPException(status_code=404, detail="String does not exist")
    return result

@app.get("/strings")
def get_strings(
    is_palindrome: Optional[bool] = Query(None),
    min_length: Optional[int] = Query(None),
    max_length: Optional[int] = Query(None),
    word_count: Optional[int] = Query(None),
    contains_character: Optional[str] = Query(None)
):
    filters_applied = {}
    results = []
    for entry in string_db.values():
        props = entry["properties"]
        if is_palindrome is not None and props["is_palindrome"] != is_palindrome:
            continue
        if min_length is not None and props["length"] < min_length:
            continue
        if max_length is not None and props["length"] > max_length:
            continue
        if word_count is not None and props["word_count"] != word_count:
            continue
        if contains_character is not None and contains_character not in entry["value"]:
            continue
        results.append(entry)
    if is_palindrome is not None:
        filters_applied["is_palindrome"] = is_palindrome
    if min_length is not None:
        filters_applied["min_length"] = min_length
    if max_length is not None:
        filters_applied["max_length"] = max_length
    if word_count is not None:
        filters_applied["word_count"] = word_count
    if contains_character is not None:
        filters_applied["contains_character"] = contains_character
    return {
        "data": results,
        "count": len(results),
        "filters_applied": filters_applied
    }

@app.delete("/strings/{string_value}", status_code=status.HTTP_204_NO_CONTENT)
def delete_string(string_value: str):
    sha256_hash = hashlib.sha256(string_value.encode()).hexdigest()
    if sha256_hash not in string_db:
        raise HTTPException(status_code=404, detail="String does not exist")
    del string_db[sha256_hash]
    return

@app.get("/strings/filter-by-natural-language")
def filter_by_natural_language(query: str):
    # Simple parser
    parsed_filters = {}
    q = query.lower()
    if "single word" in q:
        parsed_filters["word_count"] = 1
    if "palindromic" in q or "palindrome" in q:
        parsed_filters["is_palindrome"] = True
    if "longer than" in q:
        import re
        match = re.search(r"longer than (\d+)", q)
        if match:
            parsed_filters["min_length"] = int(match.group(1)) + 1
    if "containing the letter" in q:
        match = re.search(r"containing the letter ([a-zA-Z])", q)
        if match:
            parsed_filters["contains_character"] = match.group(1)
    if not parsed_filters:
        raise HTTPException(status_code=400, detail="Unable to parse natural language query")
    # Use the same filtering logic as /strings endpoint
    results = []
    for entry in string_db.values():
        props = entry["properties"]
        if parsed_filters.get("is_palindrome") is not None and props["is_palindrome"] != parsed_filters["is_palindrome"]:
            continue
        if parsed_filters.get("min_length") is not None and props["length"] < parsed_filters["min_length"]:
            continue
        if parsed_filters.get("word_count") is not None and props["word_count"] != parsed_filters["word_count"]:
            continue
        if parsed_filters.get("contains_character") is not None and parsed_filters["contains_character"] not in entry["value"]:
            continue
        results.append(entry)
    return {
        "data": results,
        "count": len(results),
        "interpreted_query": {
            "original": query,
            "parsed_filters": parsed_filters
        }
    }
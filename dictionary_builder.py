#!/usr/bin/env python3
import os
import re

SYSTEM_DICT = "/usr/share/dict/words"
OUTPUT_FILE = "dictionary.js"

def build_dictionary():
    if not os.path.exists(SYSTEM_DICT):
        print(f"System dictionary not found at {SYSTEM_DICT}")
        return False
        
    print(f"Reading from system dictionary: {SYSTEM_DICT}...")
    
    # We want to group words by length
    # Valid lengths: 2 to 12 letters
    grouped_words = {i: [] for i in range(2, 13)}
    
    count_read = 0
    count_added = 0
    
    # Regular expression for lowercase alphabetic words of length 2-12
    valid_pattern = re.compile(r"^[a-z]{2,12}$")
    
    with open(SYSTEM_DICT, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            count_read += 1
            raw_word = line.strip()
            
            # Skip words starting with uppercase (proper nouns like "Boston", "English")
            # in Scrabble proper nouns are banned.
            if raw_word and raw_word[0].isupper():
                continue
                
            word = raw_word.lower()
            
            # Check length and pattern (strictly lowercase a-z, length 2 to 12)
            if valid_pattern.match(word):
                length = len(word)
                grouped_words[length].append(word)
                count_added += 1
                
    print(f"Total lines read: {count_read}")
    print(f"Total valid lowercase words added: {count_added}")
    
    # Write to dictionary.js
    print(f"Writing output to {OUTPUT_FILE}...")
    with open(OUTPUT_FILE, "w", encoding="utf-8") as out:
        out.write("// Auto-generated clean dictionary grouped by word length\n")
        out.write("window.DICTIONARY = {\n")
        
        for length in sorted(grouped_words.keys()):
            # Sort words alphabetically
            words_sorted = sorted(list(set(grouped_words[length])))
            words_str = " ".join(words_sorted)
            
            # Write key and value
            out.write(f'  {length}: "{words_str}",\n')
            print(f"  Length {length}: {len(words_sorted)} unique words")
            
        out.write("};\n")
        
    print("Dictionary successfully built!")
    return True

if __name__ == "__main__":
    build_dictionary()

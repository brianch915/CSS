import pandas as pd
import re

def extract(text, leader_name="Vladimir Putin"):
    if not isinstance(text, str):
        return ""

    # 1. Standardize text: Replace \n and \xa0 with spaces
    # This turns the messy raw string into a clean, single-line string
    clean_text = text.replace('\xa0', ' ').replace('\n', ' ')
    clean_text = " ".join(clean_text.split())

    # 2. Check if the leader is mentioned as a speaker
    # Look for "Vladimir Putin" followed by optional space and colon
    has_identifier = re.search(rf"{leader_name}\s*:", clean_text, re.IGNORECASE)

    if has_identifier:
        # TYPE A: Transcript/Interview
        # We find the leader's name and capture everything until the next "Name :"
        # [A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s*:  matches "Pavel Zarubin :", "Question :", etc.
        pattern = rf"{leader_name}\s*:\s*(.*?)(?=[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s*:|$)"
        
        matches = re.findall(pattern, clean_text, re.IGNORECASE)
        
        # Join matches, remove parentheticals like (Laughter), and normalize whitespace
        speech = " ".join(matches).strip()
        speech = re.sub(r'\(.*?\)|\[.*?\]', '', speech)
        return " ".join(speech.split())
    
    else:
        # TYPE B: Article or Statement
        # If no colons exist, we assume the whole text is the leader's own words
        clean_text = re.sub(r'\(.*?\)|\[.*?\]', '', clean_text)
        return clean_text

putin_df = pd.read_csv('putin_final.csv')



if __name__ == "__main__":
    print("🧹 Cleaning transcripts...")

    putin_df['Cleaned_data'] = putin_df['Full_Transcript'].apply(
        lambda x: extract(x, leader_name="Vladimir Putin")
    )
    putin_df.to_csv('putin_final.csv', index=False, encoding='utf-8-sig')
    
    print("✅ Done! Cleaned text saved")
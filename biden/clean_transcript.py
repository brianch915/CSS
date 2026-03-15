import pandas as pd
import re

def extract_leader_speech(text, target_names):
    """
    Extracts speech for specific leaders and removes parenthetical annotations.
    """
    if not isinstance(text, str):
        return ""
    
    # Regex to find speaker blocks: 
    # Matches strings like 'PRESIDENT BIDEN:' or 'THE PRESIDENT:' at the start of a line
    # Then captures everything until the next speaker or end of string.
    speaker_pattern = r'(?m)^\s*([A-Z][A-Z\s]+):\s*'
    
    # Split text by speakers
    parts = re.split(speaker_pattern, text)
    
    # parts looks like: [metadata, speaker1, content1, speaker2, content2, ...]
    if len(parts) < 2:
        return text
    
    leader_content = []
    
    # Iterate through speakers (odd indices) and their content (even indices)
    for i in range(1, len(parts), 2):
        speaker_name = parts[i].strip()
        content = parts[i+1].strip()
        
        # Check if the speaker matches our target leader
        if any(name.upper() in speaker_name.upper() for name in target_names):
            # 1. Remove parentheticals like (Laughter.), (As interpreted.), [Inaudible]
            content = re.sub(r'\(.*?\)', '', content)
            content = re.sub(r'\[.*?\]', '', content)
            
            # 2. Normalize whitespace (remove extra newlines/tabs)
            content = " ".join(content.split())
            
            leader_content.append(content)
            
    return " ".join(leader_content)


biden_df = pd.read_csv('biden_final.csv')
biden_identifiers = ["PRESIDENT BIDEN", "THE PRESIDENT"]

if __name__ == "__main__":
    print("🧹 Cleaning transcripts...")

    biden_df['Cleaned_data'] = biden_df['Full_Transcript'].apply(
        lambda x: extract_leader_speech(x, biden_identifiers)
    )
    biden_df.to_csv('biden_cleaned_speeches.csv', index=False, encoding='utf-8-sig')
    
    print("✅ Done! Cleaned text saved")
import pandas as pd

def deduplicate_records(records: list[dict]) -> tuple[list[dict], int]:
    """
    Deduplicates records based on source and normalized title/name.
    Returns unique records and count of duplicates removed.
    """
    df = pd.DataFrame(records)
    if df.empty:
        return [], 0

    initial_count = len(df)
    
    # Create a deduplication key: source + lowercase stripped title/name
    df['dedup_key'] = df['source'] + "_" + df['name_or_title'].str.lower().str.replace(r'\s+', ' ', regex=True).str.strip()
    
    # Drop duplicates keeping the first occurrence
    df_unique = df.drop_duplicates(subset=['dedup_key'], keep='first')
    df_unique = df_unique.drop(columns=['dedup_key'])
    
    unique_records = df_unique.to_dict(orient='records')
    duplicates_removed = initial_count - len(unique_records)
    
    return unique_records, duplicates_removed
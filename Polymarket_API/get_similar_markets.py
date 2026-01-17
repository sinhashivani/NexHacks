# Given an exact event_title, this method:
# 1) looks up the corresponding clob_token_ids in the events table,
# 2) uses those token IDs to query the similarity table,
# 3) fetches the top 5 most similar markets ordered by cosine similarity,
# 4) enriches each result with human-readable metadata (title and question),
# and returns this events clob_token_ids
def get_similar_by_event_title(event_title: str) -> dict:
    print(event_title)
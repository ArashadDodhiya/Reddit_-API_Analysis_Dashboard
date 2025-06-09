import praw

reddit = praw.Reddit(
    client_id="KvIXop_whf_hGYsYuU-aHA",
    client_secret="230L_3InRvurp6MwvevV4D2aW5cWCQ",
    user_agent="reddit-analysis-script by u/Natural_Stuff_7011"
)

# Example: Fetch top 5 posts from r/technology
for post in reddit.subreddit("technology").hot(limit=5):
    print(f"{post.title} (Score: {post.score})")

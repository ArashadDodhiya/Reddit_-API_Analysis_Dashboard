import praw

# Initialize the Reddit API client
def initialize_reddit():
    return praw.Reddit(client_id='xxxxxx',
                       client_secret='xxxxx',
                       user_agent='xxxxx')

# Fetch Reddit posts based on a keyword or subreddit
def fetch_posts(query, subreddit=None, limit=100, time_filter='all'):
    reddit = initialize_reddit()
    if subreddit:
        posts = reddit.subreddit(subreddit).search(query, limit=limit, time_filter=time_filter)
    else:
        posts = reddit.subreddit('all').search(query, limit=limit, time_filter=time_filter)
    
    data = []
    for post in posts:
        data.append({
            'title': post.title,
            'score': post.score,
            'url': post.url,
            'created': post.created_utc,
            'comments': post.num_comments,
            'body': post.selftext
        })
    return data


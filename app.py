import streamlit as st
import pandas as pd
import plotly.express as px
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from reddit_scraper import fetch_posts
from sentiment_analysis import analyze_sentiment
from datetime import datetime
import re

# Dark theme configuration
st.set_page_config(
    page_title="Reddit Sentiment Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for dark theme
st.markdown("""
    <style>
    :root {
        --primary-color: #1a1a1a;
        --secondary-color: #2d2d2d;
        --text-color: #ffffff;
        --accent-color: #4a90e2;
        --positive-color: #2ecc71;
        --negative-color: #e74c3c;
    }
    
    .main {
        background-color: var(--primary-color);
        color: var(--text-color);
    }
    
    .sidebar .sidebar-content {
        background-color: var(--secondary-color) !important;
        color: var(--text-color);
    }
    
    .st-bw {
        background-color: var(--secondary-color);
        border-radius: 10px;
        padding: 15px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
        margin-bottom: 20px;
        color: var(--text-color);
    }
    
    .metric-card {
        background-color: var(--secondary-color);
        border-radius: 10px;
        padding: 15px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
        margin-bottom: 20px;
        color: var(--text-color);
    }
    
    .stTextInput>div>div>input, .stSlider>div>div>div>div {
        color: var(--text-color) !important;
    }
    
    .st-bq {
        border-color: var(--secondary-color);
    }
    
    /* Plotly dark theme */
    .js-plotly-plot .plotly, .js-plotly-plot .plotly div {
        background-color: transparent !important;
    }
    
    /* Matplotlib dark theme */
    plt.style.use('dark_background')
    </style>
    """, unsafe_allow_html=True)

# Apply dark theme to matplotlib
plt.style.use('dark_background')

# Dashboard title and description
st.title("📊 Reddit Sentiment Analytics Dashboard")
st.markdown("Analyze sentiment trends and engagement metrics from Reddit discussions")

# Sidebar for user inputs
with st.sidebar:
    st.header("🔍 Search Parameters")
    query = st.text_input("Keyword or Hashtag:", value="AI")
    subreddit = st.text_input("Subreddit (Optional):", value="")
    limit = st.slider("Number of Posts:", 10, 100, 50)
    st.markdown("---")
    st.markdown("### Sentiment Thresholds")
    positive_threshold = st.slider("Positive Threshold:", 0.1, 1.0, 0.3)
    negative_threshold = st.slider("Negative Threshold:", -1.0, -0.1, -0.3)
    st.markdown("---")
    st.markdown("Built with ❤️ using Streamlit")

# Main content
with st.spinner(f"Fetching {limit} posts about '{query}'..."):
    posts = fetch_posts(query, subreddit=subreddit, limit=limit)

# Analyze sentiment
posts_data = []
for post in posts:
    sentiment_score = analyze_sentiment(post['body'])
    posts_data.append({
        'title': post['title'],
        'score': post['score'],
        'comments': post['comments'],
        'sentiment_score': sentiment_score,
        'created': datetime.utcfromtimestamp(post['created'])
    })

df = pd.DataFrame(posts_data)
df['created'] = pd.to_datetime(df['created'])
df['date'] = df['created'].dt.date

# Key metrics cards
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown('<div class="metric-card">'
                '<h3>📌 Total Posts</h3>'
                f'<h1 style="color: var(--accent-color);">{len(df)}</h1>'
                '</div>', unsafe_allow_html=True)

with col2:
    avg_sentiment = df['sentiment_score'].mean()
    sentiment_color = "var(--positive-color)" if avg_sentiment > 0 else "var(--negative-color)"
    st.markdown(f'<div class="metric-card">'
                '<h3>😊 Avg. Sentiment</h3>'
                f'<h1 style="color: {sentiment_color};">{avg_sentiment:.2f}</h1>'
                '</div>', unsafe_allow_html=True)

with col3:
    st.markdown('<div class="metric-card">'
                '<h3>💬 Total Comments</h3>'
                f'<h1 style="color: #9b59b6;">{df["comments"].sum()}</h1>'
                '</div>', unsafe_allow_html=True)

# Main content tabs
tab1, tab2, tab3 = st.tabs(["📈 Charts", "☁️ Word Clouds", "📊 Data Tables"])

with tab1:
    st.markdown('<div class="st-bw">', unsafe_allow_html=True)
    st.subheader("Sentiment Analysis")
    
    col1, col2 = st.columns(2)
    with col1:
        fig_sentiment_dist = px.histogram(
            df, x='sentiment_score', nbins=20,
            title="Sentiment Distribution",
            color_discrete_sequence=['#4a90e2'],
            template='plotly_dark'
        )
        fig_sentiment_dist.add_vline(x=positive_threshold, line_dash="dash", line_color="#2ecc71")
        fig_sentiment_dist.add_vline(x=negative_threshold, line_dash="dash", line_color="#e74c3c")
        st.plotly_chart(fig_sentiment_dist, use_container_width=True)
    
    with col2:
        sentiment_over_time = df.groupby('date').agg({'sentiment_score': 'mean'}).reset_index()
        fig_sentiment_time = px.line(
            sentiment_over_time, x='date', y='sentiment_score',
            title="Sentiment Over Time",
            color_discrete_sequence=['#9b59b6'],
            template='plotly_dark'
        )
        st.plotly_chart(fig_sentiment_time, use_container_width=True)
    
    st.subheader("Post Engagement")
    most_discussed = df.nlargest(10, 'comments')
    fig_most_discussed = px.bar(
        most_discussed, x='title', y='comments',
        title="Most Discussed Posts",
        color='comments',
        color_continuous_scale='Viridis',
        labels={'title': 'Post Title', 'comments': 'Number of Comments'},
        template='plotly_dark'
    )
    fig_most_discussed.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig_most_discussed, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with tab2:
    st.markdown('<div class="st-bw">', unsafe_allow_html=True)
    st.subheader("Sentiment Word Clouds")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### Positive Sentiment")
        positive_text = ' '.join(df[df['sentiment_score'] > positive_threshold]['title'].values)
        if positive_text:
            positive_wordcloud = WordCloud(
                width=800, height=400,
                background_color='#1a1a1a',
                colormap='Greens',
                contour_width=1,
                contour_color='#2ecc71'
            ).generate(positive_text)
            fig_pos = plt.figure(figsize=(10, 5), facecolor='#1a1a1a')
            plt.imshow(positive_wordcloud, interpolation='bilinear')
            plt.axis('off')
            st.pyplot(fig_pos)
        else:
            st.warning("Not enough positive content")
    
    with col2:
        st.markdown("#### Negative Sentiment")
        negative_text = ' '.join(df[df['sentiment_score'] < negative_threshold]['title'].values)
        if negative_text:
            negative_wordcloud = WordCloud(
                width=800, height=400,
                background_color='#1a1a1a',
                colormap='Reds',
                contour_width=1,
                contour_color='#e74c3c'
            ).generate(negative_text)
            fig_neg = plt.figure(figsize=(10, 5), facecolor='#1a1a1a')
            plt.imshow(negative_wordcloud, interpolation='bilinear')
            plt.axis('off')
            st.pyplot(fig_neg)
        else:
            st.warning("Not enough negative content")
    
    st.markdown('</div>', unsafe_allow_html=True)

with tab3:
    st.markdown('<div class="st-bw">', unsafe_allow_html=True)
    st.subheader("Raw Data")
    
    st.dataframe(df.style.set_properties(**{
        'background-color': '#2d2d2d',
        'color': 'white',
        'border-color': '#4a4a4a'
    }), height=400, use_container_width=True)
    
    st.subheader("Top Hashtags")
    hashtags = []
    for post in posts:
        hashtags.extend(re.findall(r'\#\w+', post['title']))
    
    if hashtags:
        hashtag_counts = pd.Series(hashtags).value_counts().reset_index()
        hashtag_counts.columns = ['Hashtag', 'Count']
        fig_hashtags = px.bar(
            hashtag_counts.head(10), x='Hashtag', y='Count',
            title="Top 10 Hashtags",
            color='Count',
            color_continuous_scale='Viridis',
            template='plotly_dark'
        )
        st.plotly_chart(fig_hashtags, use_container_width=True)
    else:
        st.info("No hashtags found in the analyzed posts")
    
    st.subheader("Extreme Sentiment Posts")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("##### Top Positive Posts")
        top_positive = df.nlargest(5, 'sentiment_score')
        st.dataframe(top_positive[['title', 'sentiment_score', 'comments']].style.set_properties(**{
            'background-color': '#2d2d2d',
            'color': 'white',
            'border-color': '#4a4a4a'
        }), height=250)
    
    with col2:
        st.markdown("##### Top Negative Posts")
        top_negative = df.nsmallest(5, 'sentiment_score')
        st.dataframe(top_negative[['title', 'sentiment_score', 'comments']].style.set_properties(**{
            'background-color': '#2d2d2d',
            'color': 'white',
            'border-color': '#4a4a4a'
        }), height=250)
    
    st.markdown('</div>', unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("""
    <div style="text-align: center; color: #7f8c8d;">
        <p>Reddit Sentiment Analytics Dashboard • Updated at {}</p>
    </div>
""".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S")), unsafe_allow_html=True)
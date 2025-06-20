import requests
from bs4 import BeautifulSoup
import pandas as pd

# Define target URLs for each newspaper and category
news_sites = {
    "BBC": {
        "Business": "https://www.bbc.com/news/business",
        "Politics": "https://www.bbc.com/news/politics",
        "Arts/Culture/Celebrities": "https://www.bbc.com/culture",
        "Sports": "https://www.bbc.com/sport"
    },
    "CNN": {
        "Business": "https://edition.cnn.com/business",
        "Politics": "https://edition.cnn.com/politics",
        "Arts/Culture/Celebrities": "https://edition.cnn.com/entertainment",
        "Sports": "https://edition.cnn.com/sport"
    },
    "Al Jazeera": {
        "Business": "https://www.aljazeera.com/economy",
        "Politics": "https://www.aljazeera.com/politics",
        "Arts/Culture/Celebrities": "https://www.aljazeera.com/culture",
        "Sports": "https://www.aljazeera.com/sports"
    },
    "The Guardian": {
    "Business": "https://www.theguardian.com/uk/business",
    "Politics": "https://www.theguardian.com/politics",
    "Arts/Culture/Celebrities": "https://www.theguardian.com/culture",
    "Sports": "https://www.theguardian.com/uk/sport"
}

}

# Initialize data list
data = []

# Scrape articles
for site, categories in news_sites.items():
    for category, url in categories.items():
        try:
            response = requests.get(url, timeout=10)
            soup = BeautifulSoup(response.content, "html.parser")

            # Get all anchor tags with hrefs and meaningful text
            for a in soup.find_all("a", href=True):
                title = a.get_text(strip=True)
                link = a['href']
                if len(title.split()) > 4:  # Avoid short or meaningless titles
                    if not link.startswith("http"):
                        link = f"https://{url.split('/')[2]}{link}"
                    data.append({
                        "source": site,
                        "category": category,
                        "title": title,
                        "url": link
                    })
        except Exception as e:
            print(f"Error fetching {url}: {e}")

# Create dataframe
df = pd.DataFrame(data)

# Save to CSV
df.to_csv("news_articles.csv", index=False)
print(f"✅ Scraping complete: {len(df)} articles saved to articles.csv")





# Load data
df = pd.read_csv("news_articles.csv")

# Map categories to cluster IDs
category_to_cluster = {
    "Business": 0,
    "Politics": 1,
    "Arts/Culture/Celebrities": 2,
    "Sports": 3
}

# Assign cluster IDs based on the category
df['cluster'] = df['category'].map(category_to_cluster)

# Save clustered data
df.to_csv("clustered_news.csv", index=False)
print("✅ Clustering complete. Results saved to clustered_news.csv")





from flask import Flask, render_template, request
import pandas as pd

app = Flask(__name__)

@app.route('/')
def home():
    # Load clustered data
    df = pd.read_csv("clustered_news.csv")
    
    # Get filter values from the request
    search_query = request.args.get('search', '').lower()
    selected_category = request.args.get('category', '')
    selected_source = request.args.get('source', '')
    selected_date = request.args.get('date', '')

    # Filter articles based on user input
    filtered_articles = df.copy()
    if search_query:
        filtered_articles = filtered_articles[
            filtered_articles['title'].str.lower().str.contains(search_query, na=False) |
            filtered_articles['summary'].str.lower().str.contains(search_query, na=False)
        ]
    if selected_category:
        filtered_articles = filtered_articles[filtered_articles['category'] == selected_category]
        filtered_articles = filtered_articles[filtered_articles['source'] == selected_source]
    selected_date = request.args.get('date', '')
     
    clusters = {}
    if 'cluster' in df.columns:
        for cluster_id, group in df.groupby('cluster'):
            clusters[cluster_id] = group.to_dict('records')


    # Get unique values for filters
    all_categories = df['category'].unique()
    all_sources = df['source'].unique()
    #all_dates = df['timestamp'].str[:10].unique()  # Extract only the date part

    # Convert filtered articles to a list of dictionaries
    articles = filtered_articles.to_dict('records')

    return render_template(
    'index.html',
    categories=all_categories,
    sources=all_sources,
    filtered_articles=articles,
    clusters=clusters
)

@app.route('/cluster/<category>')
def show_cluster(category):
    # Load clustered data
    df = pd.read_csv("clustered_news.csv")
    
    # Filter articles by cluster category
    cluster_articles = df[df['category'] == category]
    articles = cluster_articles.to_dict('records')
    
    return render_template('cluster.html', category=category, articles=articles)
if __name__ == '__main__':
    app.run(debug=True)

from flask import Flask, render_template
import pandas as pd
from collections import defaultdict
import os

app = Flask(__name__)

@app.route('/')
def home():
    try:
        # Verify file exists
        if not os.path.exists('data/clustered_news.csv'):
            return render_template('error.html', message="Data file not found. Please run the scraper first.")
        
        df = pd.read_csv('data/clustered_news.csv')
        
        # Check if dataframe has required columns
        required_columns = ['cluster', 'title', 'url', 'source']
        if not all(col in df.columns for col in required_columns):
            return render_template('error.html', message="Data file is missing required columns.")
        
        clusters = defaultdict(list)
        for _, row in df.iterrows():
            clusters[row['cluster']].append({
                'title': row['title'],
                'url': row['url'],
                'source': row['source']
            })
        
        # Default cluster names if clustering didn't work as expected
        if not clusters:
            return render_template('error.html', message="No articles found in the data file.")
        
        cluster_names = {
            0: "Business & Economy",
            1: "Politics & World Affairs",
            2: "Arts & Culture",
            3: "Sports & Entertainment"
        }
        
        return render_template('index.html', 
                             clusters=clusters, 
                             cluster_names=cluster_names)
        
    except Exception as e:
        return render_template('error.html', 
                             message=f"Error loading data: {str(e)}")

@app.route('/cluster/<int:cluster_id>')
def cluster_view(cluster_id):
    try:
        df = pd.read_csv('data/clustered_news.csv')
        cluster_articles = df[df['cluster'] == cluster_id][['title', 'url', 'source']].to_dict('records')
        
        if not cluster_articles:
            return render_template('error.html', 
                                 message=f"No articles found in cluster {cluster_id}")
        
        cluster_names = {
            0: "Business & Economy",
            1: "Politics & World Affairs",
            2: "Arts & Culture",
            3: "Sports & Entertainment"
        }
        
        return render_template('cluster.html', 
                            articles=cluster_articles, 
                            cluster_name=cluster_names.get(cluster_id, f"Cluster {cluster_id}"))
    except Exception as e:
        return render_template('error.html', 
                            message=f"Error loading cluster: {str(e)}")

if __name__ == '__main__':
    app.run(debug=True)
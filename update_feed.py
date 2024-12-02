import requests
from bs4 import BeautifulSoup
import os
import subprocess

def fetch_paul_graham_articles():
    url = "https://paulgraham.com/articles.html"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    # Find all tables on the page
    tables = soup.find_all("table")
    
    # Ensure at least three tables exist
    if len(tables) < 3:
        raise ValueError("Unable to locate the main essays table.")

    # The main list is in the third table
    main_table = tables[2]  
    essays = []

    # Extract all links from the third table
    for link in main_table.find_all("a", href=True):
        href = link['href']
        text = link.text.strip()

        # Ensure only valid links are included
        if href.endswith(".html") and text:
            essays.append({
                "title": text,
                "link": f"https://paulgraham.com/{href}"
            })

    return essays

def generate_rss_feed(articles):
    rss = """<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
    <channel>
        <title>Paul Graham's Essays</title>
        <link>https://paulgraham.com/articles.html</link>
        <description>RSS feed for Paul Graham's essays.</description>
    """
    for article in articles:
        rss += f"""
        <item>
            <title>{article['title']}</title>
            <link>{article['link']}</link>
            <description>{article['title']}</description>
        </item>
        """
    rss += """
    </channel>
</rss>
"""
    with open("feed.xml", "w") as file:
        file.write(rss)

def push_to_github():
    # Set user identity for git before pushing changes
    subprocess.run(["git", "config", "user.name", "github-actions"])
    subprocess.run(["git", "config", "user.email", "github-actions@github.com"])
    
    subprocess.run(["git", "add", "feed.xml"])
    subprocess.run(["git", "commit", "-m", "Update RSS feed"])  # Will fail if no changes
    # Push to GitHub repository with proper authentication using GH_TOKEN
    subprocess.run([
        "git", "push",
        f"https://github-actions:${{ secrets.GH_TOKEN }}@github.com/{os.environ['GITHUB_REPOSITORY']}.git", 
        "HEAD:main"
    ])

if __name__ == "__main__":
    articles = fetch_paul_graham_articles()
    generate_rss_feed(articles)
    push_to_github()

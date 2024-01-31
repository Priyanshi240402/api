# api/fetch_youtube_data.py

import mysql.connector
import urllib.request
from bs4 import BeautifulSoup
from fastapi import FastAPI

app = FastAPI()

def scrape_channel_data(page_soup):
    # Extract data from the web scraping
    uploads = page_soup.findAll("span", {"id": "youtube-stats-header-uploads"})
    subs = page_soup.findAll("span", {"id": "youtube-stats-header-subs"})
    views = page_soup.findAll("span", {"id": "youtube-stats-header-views"})

    # Assuming you want to return the text values of uploads, subscribers, and views
    return [uploads[0].text if uploads else None, subs[0].text if subs else None, views[0].text if views else None]

def fetch_and_store_youtube_data(channel_url, channelId):
    # Fetch HTML content
    user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'
    headers = {'User-Agent': user_agent}

    request = urllib.request.Request(channel_url, None, headers)
    uClient = urllib.request.urlopen(request)
    page_html = uClient.read()
    uClient.close()

    # Parsing HTML with BeautifulSoup
    page_soup = BeautifulSoup(page_html, 'html.parser')

    # Your MySQL database credentials
    mydb = mysql.connector.connect(
        host="localhost",
        database="staff",
        user="root",
        password="Princy@123#"
    )

    # Create a cursor object to interact with the database
    mycursor = mydb.cursor()

    # Assuming you have a table named 'analysis' with columns (channel_id, videos_published, audience, views)
    table_name = 'youtubeanalytics'

    # Extract data from the scraped results
    scraped_data = scrape_channel_data(page_soup)

    # Insert data into the MySQL table
    sql = f"INSERT INTO {table_name} (channelId, videos_published, audience, views) VALUES (%s, %s, %s, %s)"
    scraped_data_with_channelId = [channelId] + scraped_data
    mycursor.execute(sql, scraped_data_with_channelId)

    # Commit the changes to the database
    mydb.commit()

    # Close the database connection
    mycursor.close()
    mydb.close()

@app.post("/fetch_youtube_data/{channelId}")
def fetch_youtube_data_by_id(channelId: str):
    channel_url = f'https://socialblade.com/youtube/channel/{channelId}'
    fetch_and_store_youtube_data(channel_url, channelId)
    return {"message": "Data fetched and stored successfully!"}

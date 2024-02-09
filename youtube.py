from flask import Flask, request, jsonify
import mysql.connector
import urllib.request
from bs4 import BeautifulSoup
import requests
import json

app = Flask(__name__)

analytics_url = "https://api.promulgateinnovations.com/api/v1/setYoutubeAnalytics"

analytics_headers = {
    'Authorization': 'Basic cHJvbXVsZ2F0ZTpwcm9tdWxnYXRl',
    'Content-Type': 'application/json'
}

def scrape_channel_data(page_soup, channel_id):
    
    payload = {
        "channelId": channel_id,
        "views": page_soup.find("span", {"id": "youtube-stats-header-views"}).text if page_soup.find("span", {"id": "youtube-stats-header-views"}) else None,
        "whatch_time": page_soup.find("span", {"id": "youtube-stats-header-whatch_time"}).text if page_soup.find("span", {"id": "youtube-stats-header-whatch_time"}) else None,
        "videos_published": page_soup.find("span", {"id": "youtube-stats-header-uploads"}).text if page_soup.find("span", {"id": "youtube-stats-header-uploads"}) else None,
        "total_likes": page_soup.find("span", {"id": "youtube-stats-header-total_likes"}).text if page_soup.find("span", {"id": "youtube-stats-header-total_likes"}) else None,
        "playlists": page_soup.find("span", {"id": "youtube-stats-header-playlists"}).text if page_soup.find("span", {"id": "youtube-stats-header-playlists"}) else None,
        "audience_retention": page_soup.find("span", {"id": "youtube-stats-header-audience_retention"}).text if page_soup.find("span", {"id": "youtube-stats-header-audience_retention"}) else None,
        "recent_videos": page_soup.find("span", {"id": "youtube-stats-header-recent_videos"}).text if page_soup.find("span", {"id": "youtube-stats-header-recent_videos"}) else None,
        "audience_by_countries": page_soup.find("span", {"id": "youtube-stats-header-audience_by_countries"}).text if page_soup.find("span", {"id": "youtube-stats-header-audience_by_countries"}) else None,
        "audience_by_demographics": page_soup.find("span", {"id": "youtube-stats-header-audience_by_demographics"}).text if page_soup.find("span", {"id": "youtube-stats-header-audience_by_demographics"}) else None,
        "traffic_source": page_soup.find("span", {"id": "youtube-stats-header-traffic_source"}).text if page_soup.find("span", {"id": "youtube-stats-header-traffic_source"}) else None,
        "external_source": page_soup.find("span", {"id": "youtube-stats-header-external_source"}).text if page_soup.find("span", {"id": "youtube-stats-header-external_source"}) else None,
        "audience": page_soup.find("span", {"id": "youtube-stats-header-subs"}).text if page_soup.find("span", {"id": "youtube-stats-header-subs"}) else None,
        "addedBy": "Priyanshi"
    }
    return payload

def fetch_and_store_youtube_data(channel_url):
    referer_url = 'https://socialblade.com/youtube/channel/UCq-Fj5jknLsUf-MWSy4_brA'

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7',
        'Referer': referer_url,
    }

    try:
        request = urllib.request.Request(channel_url, None, headers)
        uClient = urllib.request.urlopen(request)
        page_html = uClient.read()
        uClient.close()

        page_soup = BeautifulSoup(page_html, 'html.parser')
        channel_id = channel_url.split('/')[-1]

        mydb = mysql.connector.connect(
            host="localhost",
            database="youtube",
            user="root",
            password="Princy@123#"
        )

        mycursor = mydb.cursor()

        table_name = 'scrapping'
        scraped_data = scrape_channel_data(page_soup, channel_id)
        placeholders = ', '.join(['%s'] * len(scraped_data))
        sql = f"INSERT INTO {table_name} (channelId,Views, Whatch_time,videos_published, Total_likes, Playlists, Audience_retention, Recent_videos, Audience_by_countries, Audience_by_demographics, Traffic_source, External_source, Audience, AddedBy) VALUES ({placeholders})"
        
        mycursor.execute(sql, [scraped_data[key] for key in scraped_data])
        mydb.commit()
        mycursor.close()
        mydb.close()

        analytics_response = requests.post(analytics_url, headers=analytics_headers, json=scraped_data)
        print("YouTube Analytics API Response:", analytics_response.text)

    except urllib.error.HTTPError as e:
        print(f"HTTP Error {e.code}: {e.reason}")
        print(f"Request URL: {e.url}")
        print(f"Request Headers: {e.headers}")

@app.route('/fetch_and_store/<channel_id>', methods=['GET'])
def fetch_and_store(channel_id):
    channel_url = f'https://socialblade.com/youtube/channel/{channel_id}'
    fetch_and_store_youtube_data(channel_url)
    return jsonify({"message": "Data fetched and stored successfully."})
if __name__ == '__main__':
    app.run(debug=True)

    try:
        request = urllib.request.Request(channel_url, None, headers)
        uClient = urllib.request.urlopen(request)
        page_html = uClient.read()
        uClient.close()

        page_soup = BeautifulSoup(page_html, 'html.parser')

        mydb = mysql.connector.connect(
            host="localhost",
            database="youtube",
            user="root",
            password="Princy@123#"
        )

        mycursor = mydb.cursor()

        table_name = 'websap'

        scraped_data = scrape_channel_data(page_soup)

        sql = f"INSERT INTO {table_name} (channelId, videos_published, audience, views, whatch_time, total_likes, playlists, audience_retention, recent_videos, audience_by_countries, audience_by_demographics, traffic_source, external_source) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        scraped_data_with_channelId = [channelId] + scraped_data
        mycursor.execute(sql, tuple(scraped_data_with_channelId[:13]))

        mydb.commit()

        mycursor.close()
        mydb.close()

        send_data_to_external_api(channelId, *scraped_data)

    except Exception as e:
        print("Error:", e)

@app.route('/fetch_youtube_data', methods=['POST'])
def fetch_youtube_data():
    try:
        data = request.json
        channelId = data.get('channelId')

        # Replace 'your_channel_url' with the actual URL pattern for your channel
        channel_url = f'https://socialblade.com/youtube/channel/{channelId}'

        fetch_and_store_youtube_data(channel_url, channelId)

        return jsonify({"success": True, "message": "YouTube data fetched and stored successfully"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

if __name__ == '__main__':
    app.run(debug=True)


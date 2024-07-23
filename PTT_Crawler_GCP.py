import requests
from bs4 import BeautifulSoup
import pandas as pd
from google.cloud import storage
import os
import tempfile
import datetime


#the feature of the google functions. The request parameter is the entry point of the google functions. So, if we need to set 'ptt' as our entry point.
def ptt(request):
    urls = [
        "https://www.ptt.cc/bbs/C_Chat/M.1711166406.A.562.html",
        "https://www.ptt.cc/bbs/C_Chat/M.1711445201.A.E2E.html"
    ]
    def scrape_ptt_to_gcs(url):
        session = requests.Session()
        session.cookies.set('over18', '1', domain='.ptt.cc')
        response = session.get(url)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        all_comments = soup.find_all("div", class_="push")
        data = []

        for user in all_comments:
            user_id = user.find("span", class_="f3 hl push-userid")
            content = user.find("span", class_="f3 push-content")
            if user_id and content:
                data.append({"user_id": user_id.text, "vote": content.text})
                print(f"user_id: {user_id.text}, vote: {content.text}")
        return data
    all_data = []
    for url in urls:
        data = scrape_ptt_to_gcs(url)
        all_data.extend(data)
    # Create DataFrame
    df = pd.DataFrame(all_data)

    # Save DataFrame to a temporary CSV file
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.csv')
    df.to_csv(temp_file.name, mode= 'a', index=False, encoding='utf-8-sig')

    def time(): #時間 
        dateNow = ((datetime.datetime.now())+datetime.timedelta(hours=8)) #Taiwan is UTC+8
        dateTimeNowStr = dateNow.strftime("%Y%m%d_%H:%M")
        return dateTimeNowStr
    
    # Upload to GCS
    storage_client = storage.Client()
    # bucket_name = os.environ.get('ptt_crawler')
    bucket = storage_client.bucket('ptt_crawler')
    blob = bucket.blob("first/ptt_requests" + time() + " .csv")
    blob.upload_from_filename(temp_file.name)

    # Clean up temporary file
    os.remove(temp_file.name)

    return "Mission completed!"

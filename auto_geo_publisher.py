import os
import requests
import json
import base64
import random
from datetime import datetime
import pytz
import google.generativeai as genai

# Setup Environment Variables
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
WP_USERNAME = os.environ.get("WP_USERNAME")
WP_APP_PASSWORD = os.environ.get("WP_APP_PASSWORD")
WP_BASE_URL = "https://geotv.dothome.co.kr/wp-json/wp/v2"

# Date setup
kst = pytz.timezone('Asia/Seoul')
now = datetime.now(kst)
date_str = now.strftime("%Y-%m-%d")

# Gemini Setup
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# 3 topics
TOPICS = [
      "Recommend 3 hidden unique travel destinations in Korea or abroad and introduce their characteristics.",
      "5 practical tips to reduce luggage and pack efficiently when packing a travel carrier.",
      "5 useful tips to stay safe and save budget when traveling alone."
]

selected_topic = random.choice(TOPICS)

prompt = f"""
You are a professional travel blogger and SEO expert.
Today's date is {date_str}.

Please write a blog post in Korean about the following topic:
Topic: "{selected_topic}"

[Requirements]
1. Write the content in Korean.
2. The format MUST be HTML (exclude <html>, <head>, <body> tags, only use <p>, <h2>, <ul>, <li>, <strong>, etc.).
3. Start with an interesting introduction, and structure the content with subheadings (<h2>).
4. Use a friendly and polite tone in Korean.
5. Include only one <h1> tag at the very first line of the content as the post title. (e.g. <h1>[Today's Travel] Title in Korean</h1>)
                                                                                       """

                                                                                       def generate_post():
                                                                                           try:
                                                                                                   response = model.generate_content(prompt)
                                                                                                           content = response.text
                                                                                                                   
                                                                                                                           # Default title
                                                                                                                                   title = f"[{date_str}] Daily Travel Info"

                  if "<h1>" in content and "</h1>" in content:
                              start = content.find("<h1>") + 4
                                          end = content.find("</h1>")
                                                      title = content[start:end].strip()
                                                                  content = content.replace(f"<h1>{title}</h1>", "").strip()
                                                                              content = content.replace(f"<h1> {title} </h1>", "").strip()

                                                                                              if content.startswith("```html"):
                                                                                                          content = content[7:]
                                                                                                                  if content.endswith("```"):
                                                                                                                              content = content[:-3]
                                                                                                                                      content = content.strip()
                                                                                                                                              
                                                                                                                                                      return title, content
                                                                                                                                                          except Exception as e:
                                                                                                                                                                  print(f"Gemini API Error: {e}")
                                                                                                                                                                          return None, None
                                                                                                                                                                          
                                                                                                                                                                          # WordPress API Integration
                                                                                                                                                                          def publish_to_wordpress(title, content):
                                                                                                                                                                              credentials = f"{WP_USERNAME}:{WP_APP_PASSWORD}"
      token = base64.b64encode(credentials.encode('utf-8')).decode('utf-8')

              headers = {
                      'Authorization': f'Basic {token}',
                              'Content-Type': 'application/json'
                                  }

                                          post_data = {
                                                  'title': title,
                                                          'content': content,
                                                                  'status': 'publish',
                                                                          'categories': [1]
                                                                              }

                                                                                      try:
                                                                                              response = requests.post(
                                                                                                          f"{WP_BASE_URL}/posts",
                                                                                                                      headers=headers,
                                                                                                                                  data=json.dumps(post_data)
                                                                                                                                          )
                                                                                                                                                  if response.status_code == 201:
                                                                                                                                                              print("Post published successfully!")
                                                                                                                                                                          print(f"Link: {response.json().get('link')}")
                                                                                                                                                                                  else:
                                                                                                                                                                                              print(f"Failed to publish. Status code: {response.status_code}")
                                                                                                                                                                                                          print(response.text)
                                                                                                                                                                                                              except Exception as e:
                                                                                                                                                                                                                      print(f"WordPress API Error: {e}")
                                                                                                                                                                                                                      
                                                                                                                                                                                                                      if __name__ == "__main__":
                                                                                                                                                                                                                          print(f"Starting auto publishing for {date_str}...")
                                                                                                                                                                                                                              title, content = generate_post()
                                                                                                                                                                                                                                  if title and content:
                                                                                                                                                                                                                                          print(f"Generated Title: {title}")
                                                                                                                                                                                                                                                  publish_to_wordpress(title, content)
                                                                                                                                                                                                                                                      else:
                                                                                                                                                                                                                                                              print("Failed to generate content. Exiting.")
                                                                                                                                                                                                                                                              

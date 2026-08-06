import os
import sys
import json
import base64
from datetime import datetime, timedelta
import pytz
import requests
import google.generativeai as genai

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
WP_USERNAME = os.environ.get("WP_USERNAME")
WP_APP_PASSWORD = os.environ.get("WP_APP_PASSWORD")
WP_BASE_URL = "https://koreaebook.co.kr"

DRY_RUN = "--dry-run" in sys.argv

def setup_gemini():
    if not GEMINI_API_KEY:
        print("[Error] GEMINI_API_KEY not set")
        sys.exit(1)
    genai.configure(api_key=GEMINI_API_KEY)
    try:
        print("[Info] Supported models list:")
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                print(f" - {m.name}")
    except Exception as e:
        print(f"[Warning] Could not list models: {e}")

def generate_blog_content():
        print("[Info] Generating content...")
    model_name = 'gemini-1.5-flash'
    try:
                supported = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
                target_name = f"models/{model_name}"
                if target_name not in supported:
                                print(f"[Warning] {target_name} not in list.")
                                candidates = [name for name in supported if 'gemini-1.5' in name or 'gemini-2.0' in name]
                                if candidates:
                                                    model_name = candidates[0].replace("models/", "")
                                                    print(f"[Info] Fallback to: {model_name}")
    except Exception as e:
        print(f"[Warning] Fallback check failed: {e}")

    model = genai.GenerativeModel(model_name)

    prompt = """
    You are a professional business strategist and travel solopreneur blogger who specializes in 'Solopreneurship, bootstrapping, and digital nomad monetization'.
    Please choose a trendy and interesting specific topic related to this concept and write a high-quality blog post in Korean.

    The output MUST be returned strictly as a JSON object matching the schema below (Structured JSON), with no other markdown wrappers or explanations.

    {
      "title": "import os
      import sys
      import json
      import base64
      from datetime import datetime, timedelta
      import pytz
      import requests
      import google.generativeai as genai
      import urllib.parse

      GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
      WP_USERNAME = os.environ.get("WP_USERNAME")
      WP_APP_PASSWORD = os.environ.get("WP_APP_PASSWORD")
      WP_BASE_URL = "https://koreaebook.co.kr"

DRY_RUN = "--dry-run" in sys.argv

def setup_gemini():
    if not GEMINI_API_KEY:
            print("[Error] GEMINI_API_KEY not set")
                    sys.exit(1)
                        genai.configure(api_key=GEMINI_API_KEY)
                            try:
                                    print("[Info] Supported models list:")
                                            for m in genai.list_models():
                                                        if 'generateContent' in m.supported_generation_methods:
                                                                        print(f" - {m.name}")
                                                                            except Exception as e:
                                                                                    print(f"[Warning] Could not list models: {e}")

                                                                                    def generate_blog_content():
                                                                                        print("[Info] Generating content...")
                                                                                            model_name = 'gemini-1.5-flash'
                                                                                                try:
                                                                                                        supported = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
                                                                                                                target_name = f"models/{model_name}"
        if target_name not in supported:
                    print(f"[Warning] {target_name} not in list.")
                                candidates = [name for name in supported if 'gemini-1.5' in name or 'gemini-2.0' in name]
                                            if candidates:
                                                            model_name = candidates[0].replace("models/", "")
                                                                            print(f"[Info] Fallback to: {model_name}")
                                                                                except Exception as e:
                                                                                        print(f"[Warning] Fallback check failed: {e}")

                                                                                            model = genai.GenerativeModel(model_name)

                                                                                                    prompt = """
You are a professional business strategist and travel solopreneur blogger who specializes in 'Solopreneurship, bootstrapping, and digital nomad monetization'.
Please choose a trendy and interesting specific topic related to this concept and write a high-quality blog post in Korean.

The output MUST be returned strictly as a JSON object matching the schema below (Structured JSON), with no other markdown wrappers or explanations.

{
      "title": "Write the title of the post here in Korean",
      "tldr": "3-sentence summary (TL;DR) for AI citation. Write in 3 complete sentences in Korean. No markdown.",
      "content_strategy_1": "Describe the 1st actionable strategy (HTML format, using h3 and p tags) in Korean",
      "content_strategy_2": "Describe the 2nd actionable strategy (HTML format, using h3 and p tags) in Korean",
      "content_strategy_3": "Describe the 3rd actionable strategy (HTML format, using h3 and p tags) in Korean",
      "faq_1_q": "FAQ 1 Question in Korean",
      "faq_1_a": "FAQ 1 Answer in Korean",
      "faq_2_q": "FAQ 2 Question in Korean",
      "faq_2_a": "FAQ 2 Answer in Korean",
      "faq_3_q": "FAQ 3 Question in Korean",
      "faq_3_a": "FAQ 3 Answer in Korean"
}

Writing Guidelines (Write the values in Korean):
1. Focus on practical tips and real-world execution.
2. Use polite and professional honorifics (~\\uc694, ~\\uc2b5\\ub2c8\\ub2e4) in Korean.
3. Make sure the content is highly detailed and SEO optimized.
    """

        response = model.generate_content(
            prompt,
            generation_config={"response_mime_type": "application/json"}
)
    try:
                data = json.loads(response.text)
                return data
except Exception as e:
        print(f"[Error] Failed parsing JSON: {e}. Raw response:\n{response.text}")
        sys.exit(1)

def construct_html_post(data):
        html = f"""
        <!-- TL;DR (AI Summary) -->
        <div class="tldr-section" style="background-color: #f7f9fa; border-left: 4px solid #0056b3; padding: 15px; margin-bottom: 30px; border-radius: 4px;">
            <p style="font-weight: bold; margin-top: 0; color: #333;">\\ud83d\\udca1 \\uc694\\uc57d (TL;DR)</p>
                <p style="font-style: italic; color: #555; line-height: 1.6; margin-bottom: 0;">{data['tldr']}</p>
                </div>

                <!-- Main Strategies -->
                <div class="strategies-section">
                    <h2>3\\uac00\\uc9c0 \\uc2e4\\uc804 \uc2e4\\ud589 \\uc804\\ub7b5</h2>
                        <div class="strategy-item" style="margin-bottom: 25px;">
                                {data['content_strategy_1']}
                                    </div>
                                        <div class="strategy-item" style="margin-bottom: 25px;">
                                                {data['content_strategy_2']}
                                                    </div>
                                                        <div class="strategy-item" style="margin-bottom: 25px;">
                                                                {data['content_strategy_3']}
                                                                    </div>
                                                                    </div>

                                                                    <hr style="border: 0; border-top: 1px solid #eee; margin: 40px 0;" />

                                                                    <!-- FAQ Section (FAQ Schema Target) -->
                                                                    <div class="faq-section" style="margin-top: 30px;">
                                                                        <h2>\\uc790\\uc8fc \\ubb3b\\ub294 \\uc9c8\\ubb38 (FAQ)</h2>
                                                                            <div class="faq-item" style="margin-bottom: 20px; padding: 15px; border: 1px solid #eaeaea; border-radius: 6px;">
                                                                                    <h3 class="faq-question" style="color: #0056b3; margin-top: 0; font-size: 1.15em;">\\u2753 Q1. {data['faq_1_q']}</h3>
                                                                                            <p class="faq-answer" style="color: #444; margin-bottom: 0; line-height: 1.6;">\\ud83d\\udcac A. {data['faq_1_a']}</p>
                                                                                                </div>
                                                                                                    <div class="faq-item" style="margin-bottom: 20px; padding: 15px; border: 1px solid #eaeaea; border-radius: 6px;">
                                                                                                            <h3 class="faq-question" style="color: #0056b3; margin-top: 0; font-size: 1.15em;">\\u2753 Q2. {data['faq_2_q']}</h3>
                                                                                                                    <p class="faq-answer" style="color: #444; margin-bottom: 0; line-height: 1.6;">\\ud83d\\udcac A. {data['faq_2_a']}</p>
                                                                                                                        </div>
                                                                                                                            <div class="faq-item" style="margin-bottom: 20px; padding: 15px; border: 1px solid #eaeaea; border-radius: 6px;">
                                                                                                                                    <h3 class="faq-question" style="color: #0056b3; margin-top: 0; font-size: 1.15em;">\\u2753 Q3. {data['faq_3_q']}</h3>
                                                                                                                                            <p class="faq-answer" style="color: #444; margin-bottom: 0; line-height: 1.6;">\\ud83d\\udcac A. {data['faq_3_a']}</p>
                                                                                                                                                </div>
                                                                                                                                                </div>
                                                                                                                                                """
    return html

def get_or_create_category(headers):
        category_name = urllib.parse.unquote("%EC%9D%B8%20%EA%B8%B0%EC%97%85%20%26%20%EC%B0%BD%EC%97%85")
    url = f"{WP_BASE_URL}/wp-json/wp/v2/categories"
    try:
                response = requests.get(url, params={"search": category_name}, headers=headers)
                if response.status_code == 200:
                                categories = response.json()
                                for cat in categories:
                                                    if cat['name'] == category_name:
                                                                            return cat['id']
                                                                payload = {"name": category_name}
                                            create_res = requests.post(url, json=payload, headers=headers)
                            if create_res.status_code == 201:
                                            return create_res.json()['id']
except Exception as e:
        print(f"[Warning] Category check failed: {e}")
    return 1

def publish_to_wordpress(title, content):
        if not WP_USERNAME or not WP_APP_PASSWORD:
                    sys.exit(1)
                credentials = f"{WP_USERNAME}:{WP_APP_PASSWORD}"
    token = base64.b64encode(credentials.encode()).decode()
    headers = {
                "Authorization": f"Basic {token}",
                "Content-Type": "application/json"
    }
    kst = pytz.timezone('Asia/Seoul')
    now_kst = datetime.now(kst)
    target_time = now_kst.replace(hour=9, minute=0, second=0, microsecond=0)
    if now_kst >= target_time:
                target_time += timedelta(days=1)
    wp_date_str = target_time.strftime('%Y-%m-%dT%H:%M:%S')
    category_id = get_or_create_category(headers)
    post_data = {
                "title": title,
                "content": content,
                "status": "future",
                "date": wp_date_str,
                "categories": [category_id]
    }
    post_url = f"{WP_BASE_URL}/wp-json/wp/v2/posts"
    response = requests.post(post_url, json=post_data, headers=headers)
    if response.status_code == 201:
                print("Success: Post scheduled!")
else:
        print(f"Error: {response.status_code}")

def main():
        setup_gemini()
    blog_data = generate_blog_content()
    title = blog_data['title']
    html_content = construct_html_post(blog_data)
    if DRY_RUN:
                print(title)
        print(html_content)
else:
        publish_to_wordpress(title, html_content)

if __name__ == "__main__":
        main()

import os
import sys
import json
import base64
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import requests
from pydantic import BaseModel
from google import genai
from google.genai import types

# 환경 변수 및 설정
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
WP_USERNAME = os.environ.get("WP_USERNAME")
WP_APP_PASSWORD = os.environ.get("WP_APP_PASSWORD")
WP_BASE_URL = "https://koreaebook.co.kr"

DRY_RUN = "--dry-run" in sys.argv

# 1. Structured Output을 위한 Pydantic Schema 정의
class BlogPostSchema(BaseModel):
    title: str
    tldr: str
    content_strategy_1: str
    content_strategy_2: str
    content_strategy_3: str
    faq_1_q: str
    faq_1_a: str
    faq_2_q: str
    faq_2_a: str
    faq_3_q: str
    faq_3_a: str

def setup_gemini():
    if not GEMINI_API_KEY:
        print("[Error] GEMINI_API_KEY가 설정되지 않았습니다.")
        sys.exit(1)
    return genai.Client(api_key=GEMINI_API_KEY)
def generate_blog_content(client):
    print("[Info] 콘텐츠 생성 중...")
    
    # 모델명을 gemini-2.0-flash 또는 gemini-1.5-flash 로 변경합니다.
    model_name = 'gemini-2.0-flash'
    print(f"[Info] 사용 모델: {model_name}")


    prompt = """
You are a professional business strategist and travel solopreneur blogger who specializes in 'Solopreneurship, bootstrapping, and digital nomad monetization'.
Please choose a trendy and interesting specific topic related to this concept and write a high-quality blog post in Korean.

Guidelines for response:
1. Focus on practical tips and real-world execution.
2. Use polite and professional honorifics (~요, ~습니다) in Korean.
3. Make sure the content is highly detailed and SEO optimized.
4. Each strategy (content_strategy_1, 2, 3) must be written in valid HTML format using <h3> and <p> tags in Korean.
"""

    try:
        response = client.models.generate_content(
            model=model_name,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=BlogPostSchema,
                temperature=0.7,
            )
        )
        
        # Structured Output 덕분에 파싱 오류 없이 안심하고 JSON load 가능
        data = json.loads(response.text)
        return data
    except Exception as e:
        print(f"[Error] Gemini API 호출 또는 JSON 파싱 실패: {e}")
        if 'response' in locals() and hasattr(response, 'text'):
            print(f"Raw response:\n{response.text}")
        sys.exit(1)

def construct_html_post(data):
    html = f"""
    <!-- TL;DR (AI Summary) -->
    <div class="tldr-section" style="background-color: #f7f9fa; border-left: 4px solid #0056b3; padding: 15px; margin-bottom: 30px; border-radius: 4px;">
        <p style="font-weight: bold; margin-top: 0; color: #333;">💡 요약 (TL;DR)</p>
        <p style="font-style: italic; color: #555; line-height: 1.6; margin-bottom: 0;">{data.get('tldr', '')}</p>
    </div>

    <!-- Main Strategies -->
    <div class="strategies-section">
        <h2>3가지 실전 실행 전략</h2>
        <div class="strategy-item" style="margin-bottom: 25px;">
            {data.get('content_strategy_1', '')}
        </div>
        <div class="strategy-item" style="margin-bottom: 25px;">
            {data.get('content_strategy_2', '')}
        </div>
        <div class="strategy-item" style="margin-bottom: 25px;">
            {data.get('content_strategy_3', '')}
        </div>
    </div>

    <hr style="border: 0; border-top: 1px solid #eee; margin: 40px 0;" />

    <!-- FAQ Section -->
    <div class="faq-section" style="margin-top: 30px;">
        <h2>자주 묻는 질문 (FAQ)</h2>
        <div class="faq-item" style="margin-bottom: 20px; padding: 15px; border: 1px solid #eaeaea; border-radius: 6px;">
            <h3 class="faq-question" style="color: #0056b3; margin-top: 0; font-size: 1.15em;">❓ Q1. {data.get('faq_1_q', '')}</h3>
            <p class="faq-answer" style="color: #444; margin-bottom: 0; line-height: 1.6;">💬 A. {data.get('faq_1_a', '')}</p>
        </div>
        <div class="faq-item" style="margin-bottom: 20px; padding: 15px; border: 1px solid #eaeaea; border-radius: 6px;">
            <h3 class="faq-question" style="color: #0056b3; margin-top: 0; font-size: 1.15em;">❓ Q2. {data.get('faq_2_q', '')}</h3>
            <p class="faq-answer" style="color: #444; margin-bottom: 0; line-height: 1.6;">💬 A. {data.get('faq_2_a', '')}</p>
        </div>
        <div class="faq-item" style="margin-bottom: 20px; padding: 15px; border: 1px solid #eaeaea; border-radius: 6px;">
            <h3 class="faq-question" style="color: #0056b3; margin-top: 0; font-size: 1.15em;">❓ Q3. {data.get('faq_3_q', '')}</h3>
            <p class="faq-answer" style="color: #444; margin-bottom: 0; line-height: 1.6;">💬 A. {data.get('faq_3_a', '')}</p>
        </div>
    </div>
    """
    return html

def get_or_create_category(headers):
    category_name = "1인 기업 & 창업"
    url = f"{WP_BASE_URL}/wp-json/wp/v2/categories"
    try:
        response = requests.get(url, params={"search": category_name}, headers=headers, timeout=10)
        if response.status_code == 200:
            categories = response.json()
            for cat in categories:
                if cat['name'] == category_name:
                    return cat['id']
            
            # 카테고리가 없을 경우 생성
            payload = {"name": category_name}
            create_res = requests.post(url, json=payload, headers=headers, timeout=10)
            if create_res.status_code == 201:
                return create_res.json()['id']
    except Exception as e:
        print(f"[Warning] 카테고리 확인/생성 중 오류 발생: {e}")
    
    return 1  # 실패 시 기본 Uncategorized(1)로 반환

def publish_to_wordpress(title, content):
    if not WP_USERNAME or not WP_APP_PASSWORD:
        print("[Error] WP_USERNAME 또는 WP_APP_PASSWORD가 설정되지 않았습니다.")
        sys.exit(1)
    
    credentials = f"{WP_USERNAME}:{WP_APP_PASSWORD}"
    token = base64.b64encode(credentials.encode()).decode()
    headers = {
        "Authorization": f"Basic {token}",
        "Content-Type": "application/json"
    }
    
    # KST 기준 익일 오전 9시 예약 시간 계산
    kst = ZoneInfo("Asia/Seoul")
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
    try:
        response = requests.post(post_url, json=post_data, headers=headers, timeout=15)
        if response.status_code == 201:
            print(f"[Success] 포스팅 예약 성공! (예약 시간: {wp_date_str})")
        else:
            print(f"[Error] 워드프레스 발행 실패 (Status: {response.status_code}): {response.text}")
    except Exception as e:
        print(f"[Error] 워드프레스 API 요청 실패: {e}")

def main():
    client = setup_gemini()
    blog_data = generate_blog_content(client)
    title = blog_data.get('title', '제목 없음')
    html_content = construct_html_post(blog_data)
    
    if DRY_RUN:
        print("\n--- [DRY RUN MODE] ---")
        print(f"Title: {title}")
        print(f"Content:\n{html_content}")
    else:
        publish_to_wordpress(title, html_content)

if __name__ == "__main__":
    main()

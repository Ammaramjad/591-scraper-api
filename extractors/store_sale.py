import requests
from bs4 import BeautifulSoup

def extract_store_sale(url: str) -> dict:
    headers = {"User-Agent": "Mozilla/5.0", "Referer": "https://store.591.com.tw/"}
    res = requests.get(url, headers=headers, verify=False)
    soup = BeautifulSoup(res.text, 'html.parser')

    def safe_select_text(selector):
        el = soup.select_one(selector)
        return el.get_text(strip=True) if el else ""

    # Fallbacks and custom parsing
    title = soup.title.get_text(strip=True) if soup.title else ""

    # Description: collect all bullet points with ● or specific container
    desc_lines = [line.strip() for line in soup.get_text().split('\n') if line.strip().startswith("●")]
    description = "\n".join(desc_lines)

    return {
        "title": title,
        "total_price": safe_select_text(".price .price-num"),  # e.g. 2000 萬元
        "unit_price": safe_select_text(".price .unit-price"),  # e.g. 28.46 萬/坪
        "building_type": safe_select_text("ul.detail-list li:contains('型態')"),  # use with extra logic if needed
        "floor": safe_select_text("ul.detail-list li:contains('樓層')"),
        "width_depth": safe_select_text("ul.detail-list li:contains('面寬')"),
        "status": safe_select_text("ul.detail-list li:contains('經營狀態')"),
        "agent": safe_select_text(".agent-name, .agent-info"),  # selector based on agent section
        "agent_phone": safe_select_text(".agent-phone"),  # may vary
        "description": description,
        "url": url
    }

import requests
from bs4 import BeautifulSoup

def extract_land_sale(url: str) -> dict:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Referer": "https://land.591.com.tw/",
    }

    response = requests.get(url, headers=headers, verify=False)
    soup = BeautifulSoup(response.text, 'html.parser')
    text = soup.get_text()

    def extract_near(keyword, after=10, before=10):
        idx = text.find(keyword)
        if idx != -1:
            start = max(0, idx - before)
            end = idx + len(keyword) + after
            return text[start:end].strip()
        return ""

    return {
        "title": soup.find("title").text.strip() if soup.find("title") else "",
        "total_price": extract_near("萬元", after=10),
        "unit_price": extract_near("單價", after=15),
        "area_ping": extract_near("坪", before=6, after=6),
        "land_type": extract_near("住宅用地", after=5),
        "zone_usage": extract_near("使用分區", after=15),
        "address_hint": extract_near("美濃區", after=20),
        "road_width": extract_near("臨路路寬", after=10),
        "width_depth": extract_near("面寬縱深", after=25),
        "status": extract_near("現況", after=15),
        "agent": extract_near("仲介:", after=20),
        "agent_phone": extract_near("☎", after=15),
        "description": "\n".join([
            line.strip() for line in text.split("\n")
            if line.strip().startswith("❤") or line.strip().startswith("♥")
        ]),
        "url": url
    }

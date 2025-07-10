import requests
from bs4 import BeautifulSoup

def extract_store_sale(url: str) -> dict:
    headers = {"User-Agent": "Mozilla/5.0", "Referer": "https://store.591.com.tw/"}
    res = requests.get(url, headers=headers, verify=False)
    soup = BeautifulSoup(res.text, 'html.parser')
    text = soup.get_text(separator="\n")

    def near(key, after=20):
        idx = text.find(key)
        return text[idx:idx+after].strip() if idx != -1 else ""

    return {
        "title": soup.find("title").text.strip() if soup.find("title") else "",
        "total_price": near("萬元", 10),
        "unit_price": near("萬/坪", 15),
        "building_type": near("型態", 15),
        "floor": near("樓層", 15),
        "width_depth": near("面寬", 20),
        "status": near("經營狀態", 15),
        "agent": near("仲介", 15),
        "agent_phone": near("☎", 15),
        "description": "\n".join([l for l in text.split("\n") if l.strip().startswith("●") or "歡迎賞屋" in l]),
        "url": url
    }

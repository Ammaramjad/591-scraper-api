import requests
from bs4 import BeautifulSoup

def extract_land_sale(url: str) -> dict:
    headers = {"User-Agent": "Mozilla/5.0", "Referer": "https://land.591.com.tw/"}
    res = requests.get(url, headers=headers, verify=False)
    soup = BeautifulSoup(res.text, 'html.parser')
    text = soup.get_text(separator="\n")

    def near(key, after=20):
        idx = text.find(key)
        return text[idx:idx+after].strip() if idx != -1 else ""

    return {
        "title": soup.find("title").text.strip() if soup.find("title") else "",
        "price": near("萬元", 10),
        "unit_price": near("萬/坪", 15),
        "area": near("坪", 10),
        "zone": near("使用分區", 15),
        "road_width": near("臨路路寬", 15),
        "status": near("現況", 15),
        "agent": near("仲介", 15),
        "agent_phone": near("☎", 15),
        "description": "\n".join([l for l in text.split("\n") if l.strip().startswith("❤")]),
        "url": url
    }

import requests
from bs4 import BeautifulSoup

def extract_land_rent(url: str) -> dict:
    headers = {"User-Agent": "Mozilla/5.0", "Referer": "https://land.591.com.tw/"}
    res = requests.get(url, headers=headers, verify=False)
    soup = BeautifulSoup(res.text, 'html.parser')
    text = soup.get_text(separator="\n")

    def near(key, after=20):
        idx = text.find(key)
        return text[idx:idx+after].strip() if idx != -1 else ""

    return {
        "title": soup.find("title").text.strip() if soup.find("title") else "",
        "rent_price": near("元/月"),
        "unit_price": near("元/坪/月"),
        "deposit": near("押金", 15),
        "area": near("坪", 10),
        "land_type": near("類別", 10),
        "zone": near("使用分區", 10),
        "status": near("土地現況", 10),
        "min_lease": near("最短租期", 10),
        "agent": near("仲介", 15),
        "agent_phone": near("☎", 15),
        "description": "\n".join([l for l in text.split("\n") if l.strip().startswith("❤") or "特色" in l]),
        "url": url
    }

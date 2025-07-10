from bs4 import BeautifulSoup
import re

def extract_land_rent_info(soup: BeautifulSoup, full_text: str, url: str):
    def get_near(keyword, after=30):
        match = re.search(re.escape(keyword) + r"[:：]?\s*(\S+)", full_text)
        return match.group(1).strip() if match else ""

    return {
        "title": soup.title.text.strip() if soup.title else "",
        "total_price": get_near("元/月"),
        "unit_price": get_near("元/坪/月"),
        "area_ping": get_near("土地面積"),
        "land_type": get_near("類別"),
        "zone_usage": get_near("使用分區"),
        "road_width": get_near("臨路路寬") or get_near("路寬"),
        "agent": get_near("仲介") or get_near("聯絡人"),
        "agent_phone": get_near("☎") or get_near("電話"),
        "description": "\n".join([
            line.strip() for line in full_text.split("\n")
            if line.strip().startswith("❤") or line.strip().startswith("★")
        ]),
        "url": url
    }

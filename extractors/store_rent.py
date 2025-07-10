from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

def extract_store_rent(url: str) -> dict:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url, timeout=60000)
        page.wait_for_timeout(3000)
        html = page.content()
        browser.close()

    soup = BeautifulSoup(html, 'html.parser')

    def get_text_by_label(label):
        for item in soup.select("div.info-item, li"):
            if label in item.text:
                return item.text.replace(label, '').strip()
        return ""

    # Fallback for agent name and phone
    agent_name = soup.select_one(".user-name")
    agent_phone = soup.select_one("a.phoneNum")

    # Description extraction
    description = soup.select_one(".profile-word")
    description_text = description.get_text(separator="\n", strip=True) if description else ""

    return {
        "title": soup.title.get_text(strip=True) if soup.title else "",
        "rent_price": get_text_by_label("租金"),
        "unit_price": get_text_by_label("單價"),
        "area": get_text_by_label("使用坪數"),
        "floor": get_text_by_label("樓層"),
        "type": get_text_by_label("型態"),
        "lease": get_text_by_label("最短租期"),
        "agent": agent_name.get_text(strip=True) if agent_name else "",
        "agent_phone": agent_phone.get_text(strip=True) if agent_phone else "",
        "description": description_text,
        "url": url
    }

import requests
from bs4 import BeautifulSoup

def extract_land_rent(url: str) -> dict:
    headers = {
        "User-Agent": "Mozilla/5.0",
        # Add required tokens if needed
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200:
            return {"error": f"Failed to fetch URL, status code: {response.status_code}"}

        soup = BeautifulSoup(response.text, 'html.parser')

        # Initialize dictionary
        data = {
            "title": "",
            "total_price": "",
            "unit_price": "",
            "area_ping": "",
            "land_type": "",
            "road_width": "",
            "agent": "",
            "agent_phone": "",
            "description": "",
            "url": url
        }

        # Basic extraction logic — update selectors as needed
        try:
            data['title'] = soup.select_one("h1.title").text.strip()
        except:
            data['title'] = ""

        try:
            data['total_price'] = soup.select_one(".price span").text.strip()
        except:
            data['total_price'] = ""

        try:
            data['unit_price'] = soup.find(string="元/坪/月").find_previous("div").text.strip()
        except:
            data['unit_price'] = ""

        try:
            data['area_ping'] = soup.find(string="土地面積").find_next("div").text.strip()
        except:
            data['area_ping'] = ""

        try:
            data['land_type'] = soup.find(string="類別").find_next("div").text.strip()
        except:
            data['land_type'] = ""

        try:
            data['road_width'] = soup.find(string="臨路路寬").find_next("div").text.strip()
        except:
            data['road_width'] = ""

        try:
            data['agent'] = soup.select_one(".agent-name").text.strip()
        except:
            data['agent'] = ""

        try:
            data['agent_phone'] = soup.select_one("a.phone").text.strip()
        except:
            data['agent_phone'] = ""

        try:
            data['description'] = soup.select_one(".desc").text.strip()
        except:
            data['description'] = ""

        return data

    except Exception as e:
        return {"error": f"Exception during scraping: {str(e)}"}

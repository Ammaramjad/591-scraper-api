from fastapi import APIRouter, Request
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from extract.land_rent import extract_land_rent_info

router = APIRouter()

@router.get("/land-rent/{listing_id}")
def get_land_rent(listing_id: str, request: Request):
    # Playwright fetch
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(f"https://land.591.com.tw/rent/{listing_id}")
        page.wait_for_timeout(2000)
        content = page.content()
        browser.close()

    soup = BeautifulSoup(content, "html.parser")
    text = soup.get_text(separator="\n")
    data = extract_land_rent_info(soup, text, f"https://land.591.com.tw/rent/{listing_id}")

    return {"status": "success", "data": data}






@router.get("/land-sale/{listing_id}")
def get_land_sale(listing_id: str, request: Request):
    check_auth(request)
    url = f"https://land.591.com.tw/sale/{listing_id}"
    return {"status": "success", "data": extract_land_sale(url)}

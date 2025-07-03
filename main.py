from fastapi import FastAPI, HTTPException, Request, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from bs4 import BeautifulSoup

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

AUTH_TOKEN = "secure_591_token"
ENABLE_AUTH = True  # Disable this temporarily if needed


def check_auth(request: Request):
    token = request.headers.get("X-Auth-Token") or request.query_params.get("token")
    if ENABLE_AUTH and token != AUTH_TOKEN:
        raise HTTPException(status_code=403, detail="Unauthorized")


def create_retry_session():
    session = requests.Session()
    retry = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[500, 502, 503, 504],
        raise_on_status=False
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session


def get_session_and_tokens():
    session = create_retry_session()
    headers = {
        "User-Agent": "Mozilla/5.0",
        "device": "pc"
    }
    res = session.get("https://rent.591.com.tw/", headers=headers, verify=False, timeout=5)
    res.raise_for_status()
    token = session.cookies.get("XSRF-TOKEN")
    deviceid = session.cookies.get("T591_TOKEN")
    return session, token, deviceid


def fetch_listing_details(listing_id):
    session, xsrf_token, deviceid = get_session_and_tokens()
    headers = {
        "User-Agent": "Mozilla/5.0",
        "device": "pc",
        "deviceid": deviceid,
        "X-XSRF-TOKEN": xsrf_token,
        "Referer": f"https://rent.591.com.tw/{listing_id}"
    }
    url = f"https://bff.591.com.tw/v1/house/rent/detail?id={listing_id}"
    response = session.get(url, headers=headers, verify=False, timeout=5)
    response.raise_for_status()
    return response.json()["data"]


def parse_listing_info(data):
    return {
        "title": data.get("title", ""),
        "rent": data.get("price", ""),
        "deposit": data.get("deposit", ""),
        "rooms": next((i["value"] for i in data.get("info", []) if i["key"] == "layout"), ""),
        "area": next((i["value"] for i in data.get("info", []) if i["key"] == "area"), ""),
        "floor": next((i["value"] for i in data.get("info", []) if i["key"] == "floor"), ""),
        "building_type": next((i["value"] for i in data.get("info", []) if i["key"] == "shape"), ""),
        "address": data.get("positionRound", {}).get("address", ""),
        "community": data.get("positionRound", {}).get("communityName", ""),
        "equipments": [f["name"] for f in data.get("service", {}).get("facility", []) if f.get("active")],
        "rules": data.get("service", {}).get("rule", ""),
        "shortest_lease": data.get("service", {}).get("desc", ""),
        "agent": data.get("linkInfo", {}).get("name", ""),
        "agency": data.get("linkInfo", {}).get("roleTxt", ""),
        "description": data.get("remark", {}).get("content", "")
    }


def extract_land_listing(listing_id: str):
    url = f"https://land.591.com.tw/sale/{listing_id}"
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept-Language": "zh-TW,zh;q=0.9"
    }
    res = requests.get(url, headers=headers, verify=False, timeout=5)
    res.raise_for_status()

    soup = BeautifulSoup(res.text, "html.parser")

    def extract(selector):
        el = soup.select_one(selector)
        return el.get_text(strip=True) if el else ""

    return {
        "title": extract("h1.house-title"),
        "price": extract(".price .total"),
        "unit_price": extract(".price .unit-price"),
        "area": extract("div:has(span:contains('土地面積')) span.value"),
        "zone": extract("div:has(span:contains('使用分區')) span.value"),
        "road_width": extract("div:has(span:contains('臨路路寬')) span.value"),
        "location": extract(".position .info .addr"),
        "agent": extract(".avatar .name"),
        "agent_info": extract(".avatar .info"),
        "description": extract(".house-content .desc")
    }


def process_listing_task(listing_id: str):
    # Simulate processing and caching
    try:
        raw_data = fetch_listing_details(listing_id)
        result = parse_listing_info(raw_data)
        # Optionally store in database/cache
        print(f"Fetched listing {listing_id}: {result}")
    except Exception as e:
        print(f"Error processing listing {listing_id}: {e}")


@app.get("/listing/{listing_id}")
def get_listing(listing_id: str, request: Request, background_tasks: BackgroundTasks):
    check_auth(request)
    background_tasks.add_task(process_listing_task, listing_id)
    return {
        "status": "processing",
        "message": f"Fetching data for listing {listing_id}. Please check back shortly."
    }


@app.get("/land/{listing_id}")
def get_land(listing_id: str, request: Request):
    check_auth(request)
    try:
        data = extract_land_listing(listing_id)
        return {"status": "success", "data": data}
    except requests.exceptions.Timeout:
        raise HTTPException(status_code=504, detail="Timeout from 591.com.tw")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Parse error: {str(e)}")

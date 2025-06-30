from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

AUTH_TOKEN = "secure_591_token"

# Retry-enabled session
def create_retry_session():
    session = requests.Session()
    retry = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[500, 502, 503, 504]
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session

# Get session and 591 tokens
def get_session_and_tokens():
    session = create_retry_session()
    headers = {
        "User-Agent": "Mozilla/5.0",
        "device": "pc"
    }
    res = session.get("https://rent.591.com.tw/", headers=headers, verify=False, timeout=10)
    res.raise_for_status()
    token = session.cookies.get("XSRF-TOKEN")
    deviceid = session.cookies.get("T591_TOKEN")
    return session, token, deviceid

# Fetch listing details from 591 API
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
    response = session.get(url, headers=headers, verify=False, timeout=10)
    response.raise_for_status()
    return response.json()["data"]

# Parse and clean the data
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

# API route
@app.get("/listing/{listing_id}")
def get_listing(listing_id: str, request: Request):
    token = request.headers.get("X-Auth-Token") or request.query_params.get("token")
    if token != AUTH_TOKEN:
        raise HTTPException(status_code=403, detail="Unauthorized")

    try:
        raw_data = fetch_listing_details(listing_id)
        return {"status": "success", "data": parse_listing_info(raw_data)}
    except requests.exceptions.Timeout:
        raise HTTPException(status_code=504, detail="Timeout from 591.com.tw")
    except requests.exceptions.SSLError:
        raise HTTPException(status_code=502, detail="SSL certificate verification failed")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

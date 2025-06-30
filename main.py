from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

AUTH_TOKEN = "secure_591_token"  # This should match your frontend or Postman usage

def get_session_and_tokens():
    session = requests.Session()

    # Retry logic to prevent 30+ second delays
    retries = Retry(total=3, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
    adapter = HTTPAdapter(max_retries=retries)
    session.mount("https://", adapter)
    session.mount("http://", adapter)

    headers = {
        "User-Agent": "Mozilla/5.0",
        "device": "pc"
    }

    res = session.get("https://rent.591.com.tw/", headers=headers, timeout=10, verify=False)
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
    response = session.get(url, headers=headers, timeout=10, verify=False)
    response.raise_for_status()

    return response.json()["data"]

def parse_listing_info(data):
    return {
        "title": data["title"],
        "rent": data["price"],
        "deposit": data["deposit"],
        "rooms": next((i["value"] for i in data["info"] if i["key"] == "layout"), ""),
        "area": next((i["value"] for i in data["info"] if i["key"] == "area"), ""),
        "floor": next((i["value"] for i in data["info"] if i["key"] == "floor"), ""),
        "building_type": next((i["value"] for i in data["info"] if i["key"] == "shape"), ""),
        "address": data["positionRound"]["address"],
        "community": data["positionRound"]["communityName"],
        "equipments": [f["name"] for f in data["service"]["facility"] if f["active"]],
        "rules": data["service"]["rule"],
        "shortest_lease": data["service"]["desc"],
        "agent": data["linkInfo"]["name"],
        "agency": data["linkInfo"]["roleTxt"],
        "description": data["remark"]["content"]
    }

@app.get("/listing/{listing_id}")
def get_listing(listing_id: str, request: Request):
    token = request.query_params.get("token")
    if token != AUTH_TOKEN:
        raise HTTPException(status_code=403, detail="Unauthorized")

    try:
        raw_data = fetch_listing_details(listing_id)
        return {"status": "success", "data": parse_listing_info(raw_data)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

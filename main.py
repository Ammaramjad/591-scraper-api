from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
import requests

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

AUTH_TOKEN = "secure_591_token"

def get_session_and_tokens():
    session = requests.Session()
    headers = {
        "User-Agent": "Mozilla/5.0",
        "device": "pc"
    }
    res = session.get("https://rent.591.com.tw/", headers=headers, verify=False)  # ⬅️ Added verify=False
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
    response = session.get(url, headers=headers, verify=False)  # ⬅️ Added verify=False
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
    token = request.headers.get("X-Auth-Token")
    if token != AUTH_TOKEN:
        raise HTTPException(status_code=403, detail="Unauthorized")

    try:
        raw_data = fetch_listing_details(listing_id)
        return {"status": "success", "data": parse_listing_info(raw_data)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.route_land import router as land_router
from routes.route_store import router as store_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

<<<<<<< HEAD
app.include_router(land_router)
app.include_router(store_router)
=======
AUTH_TOKEN = "secure_591_token"
ENABLE_AUTH = False  # Set to True for secure access


def check_auth(request: Request):
    token = request.headers.get("X-Auth-Token") or request.query_params.get("token")
    if ENABLE_AUTH and token != AUTH_TOKEN:
        raise HTTPException(status_code=403, detail="Unauthorized")


def create_retry_session():
    session = requests.Session()
    retry = Retry(total=3, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session


def get_session_and_tokens():
    session = create_retry_session()
    headers = {"User-Agent": "Mozilla/5.0", "device": "pc"}
    res = session.get("https://rent.591.com.tw/", headers=headers, verify=False, timeout=10)
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
        "Referer": f"https://rent.591.com.tw/{listing_id}",
    }
    url = f"https://bff.591.com.tw/v1/house/rent/detail?id={listing_id}"
    response = session.get(url, headers=headers, verify=False, timeout=10)
    response.raise_for_status()
    json_data = response.json()
    if not isinstance(json_data, dict) or "data" not in json_data:
        raise HTTPException(status_code=500, detail="Unexpected data format received from 591")
    return json_data["data"]


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
        "description": data.get("remark", {}).get("content", ""),
    }


def extract_near(text, keyword, before=0, after=20):
    idx = text.find(keyword)
    if idx == -1:
        return ""
    start = max(0, idx - before)
    end = idx + len(keyword) + after
    snippet = text[start:end]
    snippet = re.sub(r"[\r\n\t]+", " ", snippet)
    return snippet.strip()


def extract_land_page_static(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Referer": "https://land.591.com.tw/",
    }
    response = requests.get(url, headers=headers, verify=False)
    soup = BeautifulSoup(response.text, 'html.parser')
    text = soup.get_text(separator="\n")

    def extract_near(keyword, after=10, before=10):
        idx = text.find(keyword)
        if idx != -1:
            start = max(0, idx - before)
            end = idx + len(keyword) + after
            return text[start:end].strip()
        return ""

    return {
        "title": soup.find("title").text.strip() if soup.find("title") else None,
        "total_price": extract_near("萬元", after=10),
        "unit_price": extract_near("單價", after=15),
        "area_ping": extract_near("坪", before=6, after=6),
        "land_type": extract_near("住宅用地", after=5),
        "zone_usage": extract_near("使用分區", after=15),
        "address_hint": extract_near("區", after=20),  # fallback
        "road_width": extract_near("臨路路寬", after=10),
        "width_depth": extract_near("面寬縱深", after=25),
        "status": extract_near("現況", after=15),
        "agent": extract_near("仲介:", after=20),
        "agent_phone": extract_near("☎", after=15),
        "description": "\n".join([
            line.strip() for line in text.split("\n")
            if line.strip().startswith("❤") or line.strip().startswith("♥")
        ]),
        "url": url
    }



@app.get("/listing/{listing_id}")
def get_listing(listing_id: str, request: Request):
    check_auth(request)
    raw_data = fetch_listing_details(listing_id)
    return {"status": "success", "data": parse_listing_info(raw_data)}


@app.get("/land/{listing_id}")
def get_land(listing_id: str, request: Request):
    check_auth(request)
    url = f"https://land.591.com.tw/sale/{listing_id}"
    return {"status": "success", "data": extract_land_page_static(url)}



@app.get("/land-rent/{listing_id}")
def get_land_rent(listing_id: str, request: Request):
    check_auth(request)
    url = f"https://land.591.com.tw/rent/{listing_id}"
    return {"status": "success", "data": extract_general_page(url)}


@app.get("/business/{listing_id}")
def get_business(listing_id: str, request: Request):
    check_auth(request)
    url = f"https://business.591.com.tw/rent/{listing_id}" if "rent" in request.url.path else f"https://business.591.com.tw/sale/{listing_id}"
    return {"status": "success", "data": extract_general_page(url)}


@app.get("/store/{listing_id}")
def get_store(listing_id: str, request: Request):
    check_auth(request)
    url = f"https://store.591.com.tw/ding-detail-{listing_id}.html"
    return {"status": "success", "data": extract_general_page(url)}
>>>>>>> de47772 (Add Dockerfile and requirements)

from fastapi import APIRouter
from extractors.land_rent import extract_land_rent
from extractors.land_sale import extract_land_sale

router = APIRouter()

@router.get("/land-rent/{listing_id}")
def get_land_rent(listing_id: str, token: str):
    url = f"https://land.591.com.tw/rent/{listing_id}"
    data = extract_land_rent(url)
    return {"status": "success", "data": data, "token": token}

@router.get("/land-sale/{listing_id}")
def get_land_sale(listing_id: str, token: str):
    url = f"https://land.591.com.tw/sale/{listing_id}"
    data = extract_land_sale(url)
    return {"status": "success", "data": data, "token": token}


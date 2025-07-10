from fastapi import APIRouter
from extractors.store_rent import extract_store_rent
from extractors.store_sale import extract_store_sale

router = APIRouter()

@router.get("/store-rent/{listing_id}")
def get_store_rent(listing_id: str, token: str):
    url = f"https://business.591.com.tw/rent/{listing_id}"
    data = extract_store_rent(url)
    return {"status": "success", "data": data, "token": token}

@router.get("/store-sale/{listing_id}")
def get_store_sale(listing_id: str, token: str):
    url = f"https://business.591.com.tw/sale/{listing_id}"
    data = extract_store_sale(url)
    return {"status": "success", "data": data, "token": token}


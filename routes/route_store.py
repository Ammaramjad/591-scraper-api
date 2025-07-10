from fastapi import APIRouter, Request
from extract.store_rent import extract_store_rent
from extract.store_sale import extract_store_sale
from auth import check_auth

router = APIRouter()

@router.get("/store-rent/{listing_id}")
def get_store_rent(listing_id: str, request: Request):
    check_auth(request)
    url = f"https://store.591.com.tw/rent/{listing_id}"
    return {"status": "success", "data": extract_store_rent(url)}

@router.get("/store-sale/{listing_id}")
def get_store_sale(listing_id: str, request: Request):
    check_auth(request)
    url = f"https://store.591.com.tw/sale/{listing_id}"
    return {"status": "success", "data": extract_store_sale(url)}

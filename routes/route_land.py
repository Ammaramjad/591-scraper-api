from fastapi import APIRouter, Request
from extract.land_rent import extract_land_rent
from extract.land_sale import extract_land_sale
from auth import check_auth

router = APIRouter()

@router.get("/land-rent/{listing_id}")
def get_land_rent(listing_id: str, request: Request):
    check_auth(request)
    url = f"https://land.591.com.tw/rent/{listing_id}"
    return {"status": "success", "data": extract_land_rent(url)}

@router.get("/land-sale/{listing_id}")
def get_land_sale(listing_id: str, request: Request):
    check_auth(request)
    url = f"https://land.591.com.tw/sale/{listing_id}"
    return {"status": "success", "data": extract_land_sale(url)}

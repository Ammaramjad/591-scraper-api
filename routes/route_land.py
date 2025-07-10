
from fastapi import APIRouter, Query
from extract.land_rent import extract_land_rent

router = APIRouter()

@router.get("/land-rent/{item_id}")
def get_land_rent(item_id: int, token: str = Query(...)):
    url = f"https://land.591.com.tw/rent/{item_id}"
    data = extract_land_rent(url)
    return {"status": "success", "data": data}






@router.get("/land-sale/{listing_id}")
def get_land_sale(listing_id: str, request: Request):
    check_auth(request)
    url = f"https://land.591.com.tw/sale/{listing_id}"
    return {"status": "success", "data": extract_land_sale(url)}

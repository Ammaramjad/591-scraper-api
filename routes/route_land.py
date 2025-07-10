from fastapi import APIRouter, Query
from extract.land_rent import extract_land_rent
from extract.land_sale import extract_land_sale

router = APIRouter()

@router.get("/land-rent/{item_id}")
def get_land_rent(item_id: int, token: str = Query(...)):
    url = f"https://land.591.com.tw/rent/{item_id}"
    data = extract_land_rent(url)
    return {"status": "success", "data": data}

@router.get("/land-sale/{item_id}")
def get_land_sale(item_id: int, token: str = Query(...)):
    url = f"https://land.591.com.tw/sale/{item_id}"
    data = extract_land_sale(url)
    return {"status": "success", "data": data}

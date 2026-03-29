from fastapi import APIRouter, Depends
from pydantic import BaseModel

from core.auth.security import PermissionChecker, get_current_user
from schemas.user_schemas import UserInfoForAdmin


router = APIRouter(prefix="/products", tags=["Mock Products"])

class ProductCreate(BaseModel):
    name: str
    price: float

MOCK_PRODUCTS = [
    {"id": 1, "name": "Ноутбук", "price": 1200.00, "owner_id": 1},
    {"id": 2, "name": "Смартфон", "price": 800.00, "owner_id": 1},
    {"id": 3, "name": "Наушники", "price": 150.00, "owner_id": 2},
]

@router.post("/")
async def create_product(
    product_data: ProductCreate,
    current_user: UserInfoForAdmin = Depends(get_current_user),
    rule = Depends(PermissionChecker("products", "create"))
):
    new_product = {
        "id": len(MOCK_PRODUCTS) + 1,
        "name": product_data.name,
        "price": product_data.price,
        "owner_id": current_user.id
    }
    
    return {
        "msg": "Product successfully created (Mock)", 
        "product": new_product
    }


@router.delete("/{product_id}")
async def delete_product(
    product_id: int,
    current_user: UserInfoForAdmin = Depends(get_current_user),
    rule = Depends(PermissionChecker("products", "delete"))
):
    target_product = next((p for p in MOCK_PRODUCTS if p["id"] == product_id), None)
     
    if not target_product:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Product not found")

    # Если это НЕ его товар, и у него НЕТ права удалять ВСЕ товары (delete_all_permission)
    if target_product["owner_id"] != current_user.id and not rule.delete_all_permission:
        from fastapi import HTTPException
        raise HTTPException(
            status_code=403, 
            detail="You don't have permission to delete other users products"
        )

    return {"msg": f"Product {product_id} successfully deleted (Mock)"}
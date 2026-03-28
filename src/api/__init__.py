from fastapi import APIRouter

from .auth.route import router as auth_router

router_list = (
    auth_router,
)

main_router = APIRouter()

for router in router_list:
    main_router.include_router(router)
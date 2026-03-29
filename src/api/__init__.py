from fastapi import APIRouter

from .auth.route import router as auth_router
from .user.route import router as user_router
from .admin.route import router as admin_router
from .mock.router import router as mock_router

router_list = (
    auth_router,
    user_router,
    admin_router,
    mock_router,
)

main_router = APIRouter()

for router in router_list:
    main_router.include_router(router)
# coding: utf-8

from typing import Dict, List  # noqa: F401
import importlib
import pkgutil

from library_api.apis.members_api_base import BaseMembersApi
import library_api.impl

from fastapi import (  # noqa: F401
    APIRouter,
    Body,
    Cookie,
    Depends,
    Form,
    Header,
    HTTPException,
    Path,
    Query,
    Response,
    Security,
    status,
)

from library_api.models.extra_models import TokenModel  # noqa: F401
from typing import Optional
from library_api.models.ly_danh_sch_th_nh_vi_n200_response import LYDanhSChThNhViN200Response
from library_api.models.ng_kth_nh_vi_nmi201_response import NgKThNhViNMI201Response
from library_api.models.ng_kth_nh_vi_nmi_request import NgKThNhViNMIRequest


router = APIRouter()

ns_pkg = library_api.impl
for _, name, _ in pkgutil.iter_modules(ns_pkg.__path__, ns_pkg.__name__ + "."):
    importlib.import_module(name)


@router.get(
    "/members",
    responses={
        200: {"model": LYDanhSChThNhViN200Response, "description": "OK"},
    },
    tags=["Members"],
    summary="Lấy danh sách thành viên",
    response_model_by_alias=True,
)
async def ly_danh_sch_thnh_vin(
) -> LYDanhSChThNhViN200Response:
    """"""
    if not BaseMembersApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseMembersApi.subclasses[0]().ly_danh_sch_thnh_vin()


@router.post(
    "/members",
    responses={
        201: {"model": NgKThNhViNMI201Response, "description": "Created"},
    },
    tags=["Members"],
    summary="Đăng ký thành viên mới",
    response_model_by_alias=True,
)
async def ng_k_thnh_vin_mi(
    ng_kth_nh_vi_nmi_request: Optional[NgKThNhViNMIRequest] = Body(None, description=""),
) -> NgKThNhViNMI201Response:
    """"""
    if not BaseMembersApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseMembersApi.subclasses[0]().ng_k_thnh_vin_mi(ng_kth_nh_vi_nmi_request)

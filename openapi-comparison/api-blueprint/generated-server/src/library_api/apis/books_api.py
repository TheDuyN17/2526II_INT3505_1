# coding: utf-8

from typing import Dict, List  # noqa: F401
import importlib
import pkgutil

from library_api.apis.books_api_base import BaseBooksApi
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
from pydantic import Field, field_validator
from typing import Optional, Union
from typing_extensions import Annotated
from library_api.models.cpnh_tsch200_response import CPNhTSCh200Response
from library_api.models.cpnh_tsch_request import CPNhTSChRequest
from library_api.models.ly_danh_sch_sch200_response import LYDanhSChSCh200Response
from library_api.models.lyth_ng_tin_mtsch200_response import LYThNgTinMTSCh200Response
from library_api.models.th_msch_mi201_response import ThMSChMI201Response
from library_api.models.th_msch_mi400_response import ThMSChMI400Response
from library_api.models.th_msch_mi_request import ThMSChMIRequest
from library_api.models.xo_sch200_response import XoSCh200Response


router = APIRouter()

ns_pkg = library_api.impl
for _, name, _ in pkgutil.iter_modules(ns_pkg.__path__, ns_pkg.__name__ + "."):
    importlib.import_module(name)


@router.get(
    "/books",
    responses={
        200: {"model": LYDanhSChSCh200Response, "description": "OK"},
    },
    tags=["Books"],
    summary="Lấy danh sách sách",
    response_model_by_alias=True,
)
async def ly_danh_sch_sch(
    page: Annotated[Optional[float], Field(description="Số trang")] = Query(1, description="Số trang", alias="page"),
    limit: Annotated[Optional[float], Field(description="Số lượng mỗi trang")] = Query(10, description="Số lượng mỗi trang", alias="limit"),
    search: Annotated[Optional[str], Field(description="Tìm theo tiêu đề hoặc tác giả")] = Query(None, description="Tìm theo tiêu đề hoặc tác giả", alias="search"),
    genre: Annotated[Optional[str], Field(description="Lọc theo thể loại")] = Query(None, description="Lọc theo thể loại", alias="genre"),
) -> LYDanhSChSCh200Response:
    """"""
    if not BaseBooksApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseBooksApi.subclasses[0]().ly_danh_sch_sch(page, limit, search, genre)


@router.post(
    "/books",
    responses={
        201: {"model": ThMSChMI201Response, "description": "Created"},
        400: {"model": ThMSChMI400Response, "description": "Bad Request"},
        409: {"model": ThMSChMI400Response, "description": "Conflict"},
    },
    tags=["Books"],
    summary="Thêm sách mới",
    response_model_by_alias=True,
)
async def thm_sch_mi(
    th_msch_mi_request: Optional[ThMSChMIRequest] = Body(None, description=""),
) -> ThMSChMI201Response:
    """"""
    if not BaseBooksApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseBooksApi.subclasses[0]().thm_sch_mi(th_msch_mi_request)


@router.get(
    "/books/{id}",
    responses={
        200: {"model": LYThNgTinMTSCh200Response, "description": "OK"},
        404: {"model": ThMSChMI400Response, "description": "Not Found"},
    },
    tags=["Books"],
    summary="Lấy thông tin một sách",
    response_model_by_alias=True,
)
async def ly_thng_tin_mt_sch(
    id: Annotated[float, Field(description="ID của sách")] = Path(..., description="ID của sách"),
) -> LYThNgTinMTSCh200Response:
    """"""
    if not BaseBooksApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseBooksApi.subclasses[0]().ly_thng_tin_mt_sch(id)


@router.put(
    "/books/{id}",
    responses={
        200: {"model": CPNhTSCh200Response, "description": "OK"},
        404: {"model": ThMSChMI400Response, "description": "Not Found"},
    },
    tags=["Books"],
    summary="Cập nhật sách",
    response_model_by_alias=True,
)
async def cp_nht_sch(
    id: Annotated[float, Field(description="ID của sách")] = Path(..., description="ID của sách"),
    cpnh_tsch_request: Optional[CPNhTSChRequest] = Body(None, description=""),
) -> CPNhTSCh200Response:
    """"""
    if not BaseBooksApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseBooksApi.subclasses[0]().cp_nht_sch(id, cpnh_tsch_request)


@router.delete(
    "/books/{id}",
    responses={
        200: {"model": XoSCh200Response, "description": "OK"},
        404: {"model": ThMSChMI400Response, "description": "Not Found"},
    },
    tags=["Books"],
    summary="Xoá sách",
    response_model_by_alias=True,
)
async def xo_sch(
    id: Annotated[float, Field(description="ID của sách")] = Path(..., description="ID của sách"),
) -> XoSCh200Response:
    """"""
    if not BaseBooksApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseBooksApi.subclasses[0]().xo_sch(id)

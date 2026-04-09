# coding: utf-8

from typing import ClassVar, Dict, List, Tuple  # noqa: F401

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


class BaseBooksApi:
    subclasses: ClassVar[Tuple] = ()

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        BaseBooksApi.subclasses = BaseBooksApi.subclasses + (cls,)
    async def ly_danh_sch_sch(
        self,
        page: Annotated[Optional[float], Field(description="Số trang")],
        limit: Annotated[Optional[float], Field(description="Số lượng mỗi trang")],
        search: Annotated[Optional[str], Field(description="Tìm theo tiêu đề hoặc tác giả")],
        genre: Annotated[Optional[str], Field(description="Lọc theo thể loại")],
    ) -> LYDanhSChSCh200Response:
        """"""
        ...


    async def thm_sch_mi(
        self,
        th_msch_mi_request: Optional[ThMSChMIRequest],
    ) -> ThMSChMI201Response:
        """"""
        ...


    async def ly_thng_tin_mt_sch(
        self,
        id: Annotated[float, Field(description="ID của sách")],
    ) -> LYThNgTinMTSCh200Response:
        """"""
        ...


    async def cp_nht_sch(
        self,
        id: Annotated[float, Field(description="ID của sách")],
        cpnh_tsch_request: Optional[CPNhTSChRequest],
    ) -> CPNhTSCh200Response:
        """"""
        ...


    async def xo_sch(
        self,
        id: Annotated[float, Field(description="ID của sách")],
    ) -> XoSCh200Response:
        """"""
        ...

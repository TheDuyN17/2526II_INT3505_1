# coding: utf-8

from typing import ClassVar, Dict, List, Tuple  # noqa: F401

from typing import Optional
from library_api.models.ly_danh_sch_th_nh_vi_n200_response import LYDanhSChThNhViN200Response
from library_api.models.ng_kth_nh_vi_nmi201_response import NgKThNhViNMI201Response
from library_api.models.ng_kth_nh_vi_nmi_request import NgKThNhViNMIRequest


class BaseMembersApi:
    subclasses: ClassVar[Tuple] = ()

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        BaseMembersApi.subclasses = BaseMembersApi.subclasses + (cls,)
    async def ly_danh_sch_thnh_vin(
        self,
    ) -> LYDanhSChThNhViN200Response:
        """"""
        ...


    async def ng_k_thnh_vin_mi(
        self,
        ng_kth_nh_vi_nmi_request: Optional[NgKThNhViNMIRequest],
    ) -> NgKThNhViNMI201Response:
        """"""
        ...

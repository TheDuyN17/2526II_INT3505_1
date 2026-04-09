# coding: utf-8

from fastapi.testclient import TestClient


from pydantic import Field, StrictFloat, StrictInt, StrictStr, field_validator  # noqa: F401
from typing import Optional, Union  # noqa: F401
from typing_extensions import Annotated  # noqa: F401
from library_api.models.cpnh_tsch200_response import CPNhTSCh200Response  # noqa: F401
from library_api.models.cpnh_tsch_request import CPNhTSChRequest  # noqa: F401
from library_api.models.ly_danh_sch_sch200_response import LYDanhSChSCh200Response  # noqa: F401
from library_api.models.lyth_ng_tin_mtsch200_response import LYThNgTinMTSCh200Response  # noqa: F401
from library_api.models.th_msch_mi201_response import ThMSChMI201Response  # noqa: F401
from library_api.models.th_msch_mi400_response import ThMSChMI400Response  # noqa: F401
from library_api.models.th_msch_mi_request import ThMSChMIRequest  # noqa: F401
from library_api.models.xo_sch200_response import XoSCh200Response  # noqa: F401


def test_ly_danh_sch_sch(client: TestClient):
    """Test case for ly_danh_sch_sch

    Lấy danh sách sách
    """
    params = [("page", 1),     ("limit", 10),     ("search", 'search_example'),     ("genre", 'genre_example')]
    headers = {
    }
    # uncomment below to make a request
    #response = client.request(
    #    "GET",
    #    "/books",
    #    headers=headers,
    #    params=params,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_thm_sch_mi(client: TestClient):
    """Test case for thm_sch_mi

    Thêm sách mới
    """
    th_msch_mi_request = {"title":"Clean Code","author":"Robert C. Martin","isbn":"9780132350884","genre":"technology","price":320000,"published_year":2008,"available":true}

    headers = {
    }
    # uncomment below to make a request
    #response = client.request(
    #    "POST",
    #    "/books",
    #    headers=headers,
    #    json=th_msch_mi_request,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_ly_thng_tin_mt_sch(client: TestClient):
    """Test case for ly_thng_tin_mt_sch

    Lấy thông tin một sách
    """

    headers = {
    }
    # uncomment below to make a request
    #response = client.request(
    #    "GET",
    #    "/books/{id}".format(id=3.4),
    #    headers=headers,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_cp_nht_sch(client: TestClient):
    """Test case for cp_nht_sch

    Cập nhật sách
    """
    cpnh_tsch_request = {"title":"Clean Code (Updated)","author":"Robert C. Martin","genre":"technology","price":350000,"available":true}

    headers = {
    }
    # uncomment below to make a request
    #response = client.request(
    #    "PUT",
    #    "/books/{id}".format(id=3.4),
    #    headers=headers,
    #    json=cpnh_tsch_request,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_xo_sch(client: TestClient):
    """Test case for xo_sch

    Xoá sách
    """

    headers = {
    }
    # uncomment below to make a request
    #response = client.request(
    #    "DELETE",
    #    "/books/{id}".format(id=3.4),
    #    headers=headers,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


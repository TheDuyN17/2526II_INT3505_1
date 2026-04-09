# coding: utf-8

from fastapi.testclient import TestClient


from typing import Optional  # noqa: F401
from library_api.models.ly_danh_sch_th_nh_vi_n200_response import LYDanhSChThNhViN200Response  # noqa: F401
from library_api.models.ng_kth_nh_vi_nmi201_response import NgKThNhViNMI201Response  # noqa: F401
from library_api.models.ng_kth_nh_vi_nmi_request import NgKThNhViNMIRequest  # noqa: F401


def test_ly_danh_sch_thnh_vin(client: TestClient):
    """Test case for ly_danh_sch_thnh_vin

    Lấy danh sách thành viên
    """

    headers = {
    }
    # uncomment below to make a request
    #response = client.request(
    #    "GET",
    #    "/members",
    #    headers=headers,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_ng_k_thnh_vin_mi(client: TestClient):
    """Test case for ng_k_thnh_vin_mi

    Đăng ký thành viên mới
    """
    ng_kth_nh_vi_nmi_request = {"name":"Nguyễn Văn B","email":"nguyenvanb@email.com"}

    headers = {
    }
    # uncomment below to make a request
    #response = client.request(
    #    "POST",
    #    "/members",
    #    headers=headers,
    #    json=ng_kth_nh_vi_nmi_request,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


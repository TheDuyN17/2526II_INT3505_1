from typing import Optional
from library_api.apis.books_api_base import BaseBooksApi
from library_api.models.cpnh_tsch200_response import CPNhTSCh200Response
from library_api.models.cpnh_tsch_request import CPNhTSChRequest
from library_api.models.ly_danh_sch_sch200_response import LYDanhSChSCh200Response
from library_api.models.lyth_ng_tin_mtsch200_response import LYThNgTinMTSCh200Response
from library_api.models.th_msch_mi201_response import ThMSChMI201Response
from library_api.models.th_msch_mi400_response import ThMSChMI400Response
from library_api.models.th_msch_mi_request import ThMSChMIRequest
from library_api.models.xo_sch200_response import XoSCh200Response

class BooksApiImpl(BaseBooksApi):
    
    # 1. API: Lấy danh sách sách
    async def ly_danh_sch_sch(
        self,
        page: Optional[int],
        limit: Optional[int],
        search: Optional[str],
        genre: Optional[str],
    ) -> LYDanhSChSCh200Response:
        
        mock_data = [
            {
                "id": 1,
                "title": "Nhà Giả Kim (Bản đã lập trình)",
                "author": "Paulo Coelho",
                "genre": "fiction",
                "price": 85000,
                "available": True
            },
            {
                "id": 2,
                "title": "Code Dạo Ký Sự",
                "author": "Phạm Huy Hoàng",
                "genre": "technology",
                "price": 105000,
                "available": True
            }
        ]
        
        return LYDanhSChSCh200Response(
            total=len(mock_data),
            page=page if page is not None else 1,
            limit=limit if limit is not None else 10,
            data=mock_data
        )

    # 2. API: Lấy thông tin một sách theo ID
    async def ly_thng_tin_mt_sch(
        self,
        id: int,
    ) -> LYThNgTinMTSCh200Response:
        
        # Giả lập trả về sách đầu tiên luôn
        return LYThNgTinMTSCh200Response(
            data={
                "id": id,
                "title": f"Sách số {id}",
                "author": "Tác giả ngẫu nhiên",
                "genre": "technology",
                "price": 50000,
                "available": True
            }
        )

    # (Các hàm thêm/sửa/xoá khác nếu cần cũng có thể implement như trên)
    async def thm_sch_mi(self, th_msch_mi_request: Optional[ThMSChMIRequest]) -> ThMSChMI201Response:
        pass
    
    async def cp_nht_sch(self, id: int, cpnh_tsch_request: Optional[CPNhTSChRequest]) -> CPNhTSCh200Response:
        pass

    async def xo_sch(self, id: int) -> XoSCh200Response:
        pass

# Mẫu thiết kế HATEOAS

## Mô tả
**HATEOAS** (Hypermedia As The Engine Of Application State) là một ràng buộc của REST application architecture. Một máy khách tương tác với mạng lưới thông qua siêu phương tiện (hypermedia) được cung cấp một cách linh hoạt bởi máy chủ.

Nói một cách đơn giản, API trả về dữ liệu KÈM THEO các hành động có thể thực hiện tiếp theo. 

## Ví dụ
Khi một Đơn hàng (Order) ở trạng thái `PENDING`, API sẽ trả về link `/pay` và `/cancel`. 
Khi Đơn hàng ở trạng thái `PAID`, API sẽ trả về link `/ship` và `/refund`.

Client không cần hard-code các nút bấm nữa, mà chỉ cần đọc trường `_links` từ API trả về và hiển thị UI tương ứng.

## Chạy thử
```bash
python app.py
```

```bash
# Sẽ trả về các link pay và cancel
curl http://localhost:5003/orders/ORD123

# Sẽ trả về các link ship và refund
curl http://localhost:5003/orders/ORD124
```

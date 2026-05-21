# Case Studies: Phân tích API Design Patterns của Stripe và GitHub

Trong thực tế, các công ty công nghệ lớn hiếm khi chỉ sử dụng một pattern duy nhất. Họ kết hợp (hybrid) nhiều mẫu thiết kế để giải quyết các bài toán khác nhau.

## 1. Stripe API (Cổng thanh toán toàn cầu)

**Patterns sử dụng chính:** REST (CRUD) kết hợp với Webhooks & Idempotency.

### Phân tích:
- **CRUD & RESTful chuẩn mực:** Stripe là chuẩn mực của REST. Họ định nghĩa tài nguyên cực kỳ rõ ràng như `/v1/customers`, `/v1/charges`. Mọi thao tác đều dùng đúng HTTP methods (POST để tạo charge, GET để lấy danh sách).
- **Idempotency Pattern:** Bất kỳ thao tác POST (chuyển tiền) nào trên Stripe đều yêu cầu (hoặc khuyến khích) gửi kèm `Idempotency-Key` ở Header để đảm bảo nếu mạng bị rớt, gửi lại request sẽ không bị trừ tiền 2 lần. (Giống phần thực hành ở Lecture 9 của chúng ta).
- **Webhook Pattern (Bắt buộc):** Khi người dùng thanh toán qua thẻ, việc kiểm tra với ngân hàng mất nhiều thời gian (bất đồng bộ). Thay vì bắt người dùng chờ, API trả về trạng thái `processing`. Sau khi ngân hàng phản hồi, Stripe sẽ gọi một Webhook về hệ thống của chúng ta để báo `charge.succeeded` hoặc `charge.failed`.

## 2. GitHub API

**Patterns sử dụng chính:** REST kết hợp GraphQL, HATEOAS và Webhooks.

### Phân tích:
- **Từ REST sang GraphQL:** 
  - GitHub v3 sử dụng REST. Vấn đề là dữ liệu trên GitHub rất chằng chịt (Repository -> Pull Requests -> Commits -> Authors). Nếu dùng REST, để lấy ra toàn bộ thông tin này cần gọi hàng chục API khác nhau (Under-fetching).
  - Do đó, GitHub ra mắt **API v4 hoàn toàn bằng GraphQL**. Nó cho phép lập trình viên viết một câu Query duy nhất để lấy đúng những thông tin chằng chịt đó trong 1 lần gọi.
- **HATEOAS (Pagination Links):** 
  - Trong API v3 (REST), khi lấy danh sách repos, GitHub trả về các link chuyển trang nằm ngay trong **HTTP Header `Link`** (ví dụ: `<https://api.github.com/user/repos?page=2>; rel="next"`). Lập trình viên không cần tự tính toán trang tiếp theo, chỉ cần đọc URL ở header `next` và gọi.
- **Webhook Pattern:** GitHub cung cấp Webhook cực kỳ mạnh mẽ để xây dựng hệ thống CI/CD. Cứ mỗi khi có người push code hoặc tạo Pull Request, GitHub sẽ bắn event về server Jenkins/Github Actions của bạn để tự động build code.

## 3. Tổng kết (Kết hợp Patterns)
- Khi thiết kế API, hãy dùng **CRUD (REST)** làm nền tảng.
- Thêm **Query Pattern** khi tài nguyên có nhiều dữ liệu cần tìm kiếm.
- Khi tác vụ tốn thời gian, bắt buộc phải đổi sang kiến trúc Event-Driven (**Webhooks**).
- Đừng rập khuôn. Tùy biến và kết hợp các Patterns dựa trên nghiệp vụ thực tế mới là kỹ năng quan trọng nhất!

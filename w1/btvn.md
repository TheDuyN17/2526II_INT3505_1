Bài tập về nhà: Tìm và phân tích 3 API công khai
1. GitHub API
- URL gốc: https://api.github.com
- Loại API: REST API
- Mục đích: Truy xuất thông tin về người dùng, repository, commit, issues, pull
request… trên GitHub.
- Phương thức HTTP: GET, POST, PATCH, DELETE Định dạng dữ liệu: JSON
- Ví dụ request: GET https://api.github.com/users/octocat
- Ví dụ response:
{
 "login": "octocat",
 "id": 583231,
 "public_repos": 8,
 "followers": 3941
}
Ưu điểm:
● RESTful, dùng JSON nên dễ xử lý.
● Hỗ trợ OAuth 2.0 để xác thực.
● Phù hợp cho tự động hóa quản lý repository, thống kê dữ liệu lập trình viên.
2. OpenWeather API
- URL gốc: https://api.openweathermap.org/data/2.5/weather
- Loại API: REST API
- Mục đích: Lấy dữ liệu thời tiết theo thành phố, tọa độ, hoặc ID.
- Phương thức HTTP: GET Định dạng dữ liệu: JSON, XML
- Ví dụ request: GET
https://api.openweathermap.org/data/2.5/weather?q=Hanoi&appid=YOUR_AP
I_KEY
- Ví dụ response:
{
 "weather":[{"description":"clear sky"}],
 "main":{"temp":300.15,"humidity":40},
 "wind":{"speed":3.6}
}
Ưu điểm:
● Cung cấp dữ liệu thời tiết hiện tại, dự báo, dữ liệu lịch sử.
● Cần API Key để xác thực.
● Dữ liệu cập nhật liên tục, phù hợp cho ứng dụng thời tiết, du lịch, IoT.
3. The Cat API
- URL gốc: https://api.thecatapi.com/v1/images/search
- Loại API: REST API
- Mục đích: Cung cấp hình ảnh mèo ngẫu nhiên (thường dùng cho ứng dụng
vui nhộn hoặc website thú cưng)
- Phương thức HTTP: GET Định dạng dữ liệu: JSON
- Ví dụ request: GET https://api.thecatapi.com/v1/images/search
- Ví dụ response:
[
 {
 "id": "MTY3ODIyMQ",
 "url": "https://cdn2.thecatapi.com/images/MTY3ODIyMQ.jpg",
 "width": 500,
 "height": 333
 }
]
Ưu điểm:
● Miễn phí, dễ dùng.
● Phù hợp cho học tập, demo, app vui nhộn.
● Có thể lọc theo giống mèo, hình ảnh động, v.v.
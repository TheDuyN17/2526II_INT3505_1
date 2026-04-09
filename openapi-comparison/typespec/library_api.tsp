import "@typespec/http";
import "@typespec/openapi3";

using TypeSpec.Http;
using TypeSpec.Lifecycle;

@service({
  title: "Library Management API",
})
@server("http://localhost:8003/api/v1", "Local development server")
namespace LibraryAPI;

// ─── Enums ───────────────────────────────────────────────────────────────────

enum Genre {
  fiction,
  `non-fiction`,
  science,
  history,
  technology,
  children,
}

// ─── Models ──────────────────────────────────────────────────────────────────

/** Đối tượng sách đầy đủ (bao gồm ID do server cấp) */
model Book {
  /** ID tự tăng do server sinh ra */
  @visibility(Lifecycle.Read)
  id: int32;

  /** Tiêu đề sách */
  @maxLength(255)
  title: string;

  /** Tên tác giả */
  @maxLength(255)
  author: string;

  /** Mã ISBN (10 hoặc 13 chữ số) */
  isbn?: string;

  /** Thể loại sách */
  genre: Genre;

  /** Giá bán (VNĐ) */
  @minValue(0)
  price: float32;

  /** Năm xuất bản */
  @minValue(1000)
  @maxValue(2100)
  published_year?: int32;

  /** Mô tả ngắn về nội dung sách */
  @maxLength(1000)
  description?: string;

  /** Sách còn hàng hay không */
  available: boolean;

  /** Thời điểm tạo */
  @visibility(Lifecycle.Read)
  created_at?: utcDateTime;

  /** Thời điểm cập nhật lần cuối */
  @visibility(Lifecycle.Read)
  updated_at?: utcDateTime;
}

/** Dữ liệu cần thiết để tạo hoặc cập nhật sách */
model BookCreate {
  @maxLength(255)
  title: string;

  @maxLength(255)
  author: string;

  isbn?: string;
  genre: Genre;

  @minValue(0)
  price: float32;

  @minValue(1000)
  @maxValue(2100)
  published_year?: int32;

  @maxLength(1000)
  description?: string;

  available?: boolean = true;
}

/** Response wrapper cho danh sách sách */
model BookListResponse {
  total: int32;
  page: int32;
  limit: int32;
  data: Book[];
}

/** Response wrapper cho một cuốn sách */
model BookResponse {
  data: Book;
}

/** Cấu trúc lỗi chuẩn */
@error
model ApiError {
  error: string;
  message: string;
}

/** Thành viên thư viện */
model Member {
  @visibility(Lifecycle.Read)
  id: int32;

  name: string;
  email: string;

  @visibility(Lifecycle.Read)
  joined_date?: plainDate;
}

/** Dữ liệu tạo thành viên mới */
model MemberCreate {
  name: string;
  email: string;
}

model MemberListResponse {
  total: int32;
  data: Member[];
}

// ─── Query Parameters ────────────────────────────────────────────────────────

model PaginationParams {
  @query
  @minValue(1)
  page?: int32 = 1;

  @query
  @minValue(1)
  @maxValue(100)
  limit?: int32 = 10;
}

model BookQueryParams {
  ...PaginationParams;

  @query
  search?: string;

  @query
  genre?: Genre;
}

// ─── Routes ──────────────────────────────────────────────────────────────────

@route("/books")
@tag("Books")
interface Books {
  /** Lấy danh sách tất cả sách. Hỗ trợ phân trang và tìm kiếm. */
  @get
  list(...BookQueryParams): BookListResponse | ApiError;

  /** Tạo một bản ghi sách mới trong hệ thống. */
  @post
  create(@body book: BookCreate): { @statusCode _: 201; ...BookResponse } | ApiError;

  /** Lấy thông tin chi tiết của một cuốn sách theo ID. */
  @get
  @route("{id}")
  read(@path id: int32): BookResponse | ApiError;

  /** Cập nhật toàn bộ thông tin của một cuốn sách. */
  @put
  @route("{id}")
  update(@path id: int32, @body book: BookCreate): BookResponse | ApiError;

  /** Xoá vĩnh viễn một cuốn sách khỏi hệ thống. */
  @delete
  @route("{id}")
  remove(@path id: int32): { message: string } | ApiError;
}

@route("/members")
@tag("Members")
interface Members {
  /** Lấy danh sách thành viên thư viện. */
  @get
  list(...PaginationParams): MemberListResponse | ApiError;

  /** Đăng ký thành viên mới. */
  @post
  create(@body member: MemberCreate): { @statusCode _: 201; data: Member } | ApiError;
}

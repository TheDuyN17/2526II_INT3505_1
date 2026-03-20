import "@typespec/http";
import "@typespec/openapi3";

using TypeSpec.Http;

@service(#{
  title: "Library Management API",
})
@server("http://localhost:3000/api", "Server phát triển")
namespace LibraryAPI;

model Book {
  id: int32;
  title: string;
  author: string;
  year?: int32;
  genre?: string;
  available?: boolean;
}

model BookInput {
  title: string;
  author: string;
  year?: int32;
  genre?: string;
}

model ErrorResponse {
  message: string;
}

@route("/books")
interface Books {
  @get list(@query search?: string, @query genre?: string): Book[];
  @post create(@body body: BookInput): {
    @statusCode statusCode: 201;
    @body body: Book;
  };
}

@route("/books/{id}")
interface BookById {
  @get read(@path id: int32): Book | {
    @statusCode statusCode: 404;
    @body body: ErrorResponse;
  };
  @put update(@path id: int32, @body body: BookInput): Book | {
    @statusCode statusCode: 404;
    @body body: ErrorResponse;
  };
  @delete remove(@path id: int32): {
    @statusCode statusCode: 200;
    @body body: { message: string };
  } | {
    @statusCode statusCode: 404;
    @body body: ErrorResponse;
  };
}
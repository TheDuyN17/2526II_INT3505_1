import "@typespec/http";
import "@typespec/rest";
import "@typespec/openapi3";

using TypeSpec.Http;
using TypeSpec.Rest;

@service({
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

model Error {
  message: string;
}

@route("/books")
namespace Books {
  @get
  op list(
    @query search?: string,
    @query genre?: string
  ): Book[];

  @post
  op create(@body body: BookInput): {
    @statusCode statusCode: 201;
    @body body: Book;
  } | {
    @statusCode statusCode: 400;
    @body body: Error;
  };

  @route("/{id}")
  @get
  op read(@path id: int32): Book | {
    @statusCode statusCode: 404;
    @body body: Error;
  };

  @route("/{id}")
  @put
  op update(@path id: int32, @body body: BookInput): Book | {
    @statusCode statusCode: 404;
    @body body: Error;
  };

  @route("/{id}")
  @delete
  op delete(@path id: int32): {
    @statusCode statusCode: 200;
    @body body: { message: string };
  } | {
    @statusCode statusCode: 404;
    @body body: Error;
  };
}
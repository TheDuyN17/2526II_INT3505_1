# Week13 - API as a Product

Buoi 13 tap trung vao cach dong goi API nhu mot san pham that su cho developer:

- Developer experience: portal, quickstart, sandbox, docs, vi du request.
- Monetization: freemium, pay-per-call, team/scale plan.
- Analytics va KPI: developer dang ky, call volume, error rate, latency, activation.
- Launch strategy: private beta, public developer portal, pricing va lifecycle.

## Cau truc

- `src/app.py`: Flask app, developer portal HTML va cac endpoint JSON.
- `src/openapi.py`: OpenAPI/Swagger specification cho developer docs.
- `src/server.py`: entrypoint chay server local.
- `tests/test_app.py`: test portal, business model canvas, KPI va pricing.

## Chay local

Tu thu muc goc project:

```bash
python3 -m pip install -r requirements.txt
python3 -m week13.src.server
```

Mac dinh server chay tai:

```text
http://127.0.0.1:5014
```

Developer portal:

```text
http://127.0.0.1:5014/portal
```

Swagger UI:

```text
http://127.0.0.1:5014/apidocs/
```

OpenAPI JSON:

```text
http://127.0.0.1:5014/apispec_1.json
```

## API endpoints

| Method | Endpoint | Muc dich |
| --- | --- | --- |
| GET | `/` | Thong tin service va link nhanh |
| GET | `/portal` | Trang developer portal don gian |
| GET | `/apidocs/` | Swagger UI cho developer docs |
| GET | `/apispec_1.json` | OpenAPI JSON spec |
| GET | `/api/business-model` | Business model canvas cho API |
| GET | `/api/launch-strategy` | Chien luoc ra mat API |
| GET | `/api/pricing` | Mo hinh kiem tien: freemium, pay-per-call, scale |
| GET | `/api/metrics` | KPI snapshot: developer, call volume, error rate |
| GET | `/api/sandbox` | Thong tin sandbox va endpoint mau |
| GET | `/health` | Health check |

## Business Model Canvas

Canvas trong bai gom cac khoi chinh:

- Customer segments: developer hoc tap, nen tang giao duc, team frontend noi bo.
- Value propositions: API co docs ro, sandbox data, OpenAPI va KPI van hanh.
- Channels: developer portal, Swagger/OpenAPI, GitHub examples.
- Revenue streams: free tier, pay-per-call, scale/team plan.
- Key activities: docs, sandbox, analytics, quota, versioning, deprecation.
- Cost structure: cloud, database, logging, monitoring, support, security review.

## Huong dan test

Chay test bang `unittest`:

```bash
python3 -m unittest week13.tests.test_app
```

Ket qua mong doi:

```text
Ran 6 tests
OK
```

## Goi thu API

```bash
curl http://127.0.0.1:5014/api/metrics
curl http://127.0.0.1:5014/api/pricing
curl http://127.0.0.1:5014/api/business-model
```

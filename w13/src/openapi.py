from __future__ import annotations


OPENAPI_SPEC = {
    "openapi": "3.0.3",
    "info": {
        "title": "Week13 API as a Product",
        "version": "1.0.0",
        "description": (
            "Developer portal, sandbox, pricing, business model canvas, "
            "and KPI analytics for packaging an API as a product."
        ),
    },
    "servers": [{"url": "http://127.0.0.1:5014"}],
    "tags": [
        {"name": "Discovery", "description": "Service metadata and health checks"},
        {"name": "Portal", "description": "Developer portal experience"},
        {"name": "Product Strategy", "description": "Launch, monetization, and canvas APIs"},
        {"name": "Analytics", "description": "Developer and operational KPIs"},
        {"name": "Sandbox", "description": "Sandbox onboarding data"},
    ],
    "paths": {
        "/": {
            "get": {
                "tags": ["Discovery"],
                "summary": "Get service metadata and developer links",
                "responses": {
                    "200": {
                        "description": "Service metadata",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/HomeResponse"}
                            }
                        },
                    }
                },
            }
        },
        "/portal": {
            "get": {
                "tags": ["Portal"],
                "summary": "Open the developer portal HTML page",
                "responses": {
                    "200": {
                        "description": "Developer portal page",
                        "content": {"text/html": {"schema": {"type": "string"}}},
                    }
                },
            }
        },
        "/api/business-model": {
            "get": {
                "tags": ["Product Strategy"],
                "summary": "Get the API business model canvas",
                "responses": {
                    "200": {
                        "description": "Business model canvas",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "canvas": {
                                            "$ref": "#/components/schemas/BusinessModelCanvas"
                                        }
                                    },
                                    "required": ["canvas"],
                                }
                            }
                        },
                    }
                },
            }
        },
        "/api/launch-strategy": {
            "get": {
                "tags": ["Product Strategy"],
                "summary": "Get the API launch strategy",
                "responses": {
                    "200": {
                        "description": "Launch strategy phases",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "strategy": {
                                            "type": "object",
                                            "additionalProperties": {
                                                "$ref": "#/components/schemas/LaunchPhase"
                                            },
                                        }
                                    },
                                    "required": ["strategy"],
                                }
                            }
                        },
                    }
                },
            }
        },
        "/api/pricing": {
            "get": {
                "tags": ["Product Strategy"],
                "summary": "Get freemium, pay-per-call, and scale pricing plans",
                "responses": {
                    "200": {
                        "description": "Pricing plans",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "plans": {
                                            "type": "array",
                                            "items": {
                                                "$ref": "#/components/schemas/PricingPlan"
                                            },
                                        }
                                    },
                                    "required": ["plans"],
                                }
                            }
                        },
                    }
                },
            }
        },
        "/api/metrics": {
            "get": {
                "tags": ["Analytics"],
                "summary": "Get API product KPI snapshot",
                "responses": {
                    "200": {
                        "description": "KPI snapshot",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "kpis": {"$ref": "#/components/schemas/KpiSnapshot"}
                                    },
                                    "required": ["kpis"],
                                }
                            }
                        },
                    }
                },
            }
        },
        "/api/sandbox": {
            "get": {
                "tags": ["Sandbox"],
                "summary": "Get sandbox onboarding details and sample endpoints",
                "security": [{"SandboxBearer": []}],
                "responses": {
                    "200": {
                        "description": "Sandbox information",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/SandboxResponse"}
                            }
                        },
                    }
                },
            }
        },
        "/health": {
            "get": {
                "tags": ["Discovery"],
                "summary": "Health check",
                "responses": {
                    "200": {
                        "description": "Service is healthy",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {"status": {"type": "string", "example": "ok"}},
                                    "required": ["status"],
                                }
                            }
                        },
                    }
                },
            }
        },
    },
    "components": {
        "securitySchemes": {
            "SandboxBearer": {
                "type": "http",
                "scheme": "bearer",
                "description": "Demo token: edu_sandbox_demo_key",
            }
        },
        "schemas": {
            "HomeResponse": {
                "type": "object",
                "properties": {
                    "message": {"type": "string"},
                    "developer_portal": {"type": "string", "example": "/portal"},
                    "swagger_docs": {"type": "string", "example": "/apidocs/"},
                    "openapi_json": {"type": "string", "example": "/apispec_1.json"},
                    "business_model_canvas": {
                        "type": "string",
                        "example": "/api/business-model",
                    },
                    "kpis": {"type": "string", "example": "/api/metrics"},
                    "pricing": {"type": "string", "example": "/api/pricing"},
                    "sandbox": {"type": "string", "example": "/api/sandbox"},
                },
                "required": [
                    "message",
                    "developer_portal",
                    "swagger_docs",
                    "openapi_json",
                    "business_model_canvas",
                    "kpis",
                    "pricing",
                    "sandbox",
                ],
            },
            "BusinessModelCanvas": {
                "type": "object",
                "additionalProperties": {
                    "type": "array",
                    "items": {"type": "string"},
                },
                "example": {
                    "customer_segments": [
                        "Student developers building learning and tutoring integrations"
                    ],
                    "value_propositions": [
                        "A documented education API with sandbox data and clear examples"
                    ],
                    "revenue_streams": ["Freemium tier for learning and prototypes"],
                },
            },
            "LaunchPhase": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "example": "Private beta"},
                    "actions": {
                        "type": "array",
                        "items": {"type": "string"},
                        "example": ["Invite a small group of developers"],
                    },
                },
                "required": ["name", "actions"],
            },
            "PricingPlan": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "example": "Growth"},
                    "price": {"type": "string", "example": "$19/month + $0.002/call over quota"},
                    "quota": {"type": "string", "example": "50,000 calls/month"},
                    "best_for": {"type": "string", "example": "Small production integrations"},
                    "features": {"type": "array", "items": {"type": "string"}},
                },
                "required": ["name", "price", "quota", "best_for", "features"],
            },
            "KpiSnapshot": {
                "type": "object",
                "properties": {
                    "registered_developers": {"type": "integer", "example": 128},
                    "active_developers_30d": {"type": "integer", "example": 42},
                    "call_volume_30d": {"type": "integer", "example": 184250},
                    "error_rate_30d": {"type": "number", "format": "float", "example": 0.012},
                    "p95_latency_ms": {"type": "integer", "example": 180},
                    "first_call_conversion_rate": {
                        "type": "number",
                        "format": "float",
                        "example": 0.64,
                    },
                },
                "required": [
                    "registered_developers",
                    "active_developers_30d",
                    "call_volume_30d",
                    "error_rate_30d",
                    "p95_latency_ms",
                    "first_call_conversion_rate",
                ],
            },
            "SandboxEndpoint": {
                "type": "object",
                "properties": {
                    "method": {"type": "string", "example": "GET"},
                    "path": {"type": "string", "example": "/api/metrics"},
                    "purpose": {"type": "string", "example": "Read KPI snapshot"},
                },
                "required": ["method", "path", "purpose"],
            },
            "SandboxResponse": {
                "type": "object",
                "properties": {
                    "environment": {"type": "string", "example": "sandbox"},
                    "base_url": {"type": "string", "example": "http://127.0.0.1:5014/api"},
                    "api_key": {"type": "string", "example": "edu_sandbox_demo_key"},
                    "sample_endpoints": {
                        "type": "array",
                        "items": {"$ref": "#/components/schemas/SandboxEndpoint"},
                    },
                },
                "required": ["environment", "base_url", "api_key", "sample_endpoints"],
            },
        },
    },
}

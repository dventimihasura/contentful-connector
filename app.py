from flask import Flask, request
import functools
import os
import requests

app = Flask(__name__)

base_url = functools.cache(lambda: "https://api.contentful.com")
api_key = functools.cache(lambda: os.getenv("API_KEY"))
space = functools.cache(lambda: os.getenv("SPACE"))
environment = functools.cache(lambda: os.getenv("ENVIRONMENT"))
kapabilities = functools.cache(lambda: {
    "versions": "^0.1.0",
    "capabilities": {
        "query": {
            "relation_comparisons": {},
            "order_by_aggregate": {},
            "foreach": {}
        },
        "explain": {},
        "mutations": {
            "nested_inserts": {},
            "returning": {}
        },
        "relationships": {}
    }
})
content_types = functools.cache(lambda: requests.get(
    f"{base_url()}/spaces/{space()}/environments/{environment()}/content_types",
    headers={
        "Authorization": f"Bearer {api_key()}"
    }).json()["items"])
scalar_types = functools.cache(lambda: {
    "Array": {"aggregate_functions": {}, "comparison_operators": {}},
    "Boolean": {"aggregate_functions": {}, "comparison_operators": {}},
    "Number": {"aggregate_functions": {}, "comparison_operators": {}},
    "Object": {"aggregate_functions": {}, "comparison_operators": {}},
    "String": {"aggregate_functions": {}, "comparison_operators": {}}
})
type_map = functools.cache(lambda: {
    "Symbol": "String",
    "Text": "String",
    "RichText": "String",
    "Integer": "Number",
    "Number": "Number",
    "Date": "String",
    "Location": "Object",
    "Boolean": "Boolean",
    "Link": "Object",
    "Array": "Array",
    "Object": "Object"
})
object_types = functools.cache(lambda: {
    ct["sys"]["id"]: {
        "description": ct["name"],
        "fields": {
            f["id"]: {
                "description": f"{ct['displayField']}: {ct['name']} {ct['description']}",
                "arguments": {},
                "type": {
                    "type": "named",
                    "name": type_map()[f["type"]]
                }
            } for f in ct["fields"]
        }
    } for ct in content_types()
})
collections = functools.cache(lambda: [
    {
        "name": ct["sys"]["id"],
        "description": f"{ct['displayField']}: {ct['name']} {ct['description']}",
        "arguments": {},
        "type": ct["sys"]["id"],
        "deletable": False,
        "uniqueness_constraints": {},
        "foreign_keys": {}
    } for ct in content_types()
])
functions = functools.cache(lambda: [])
procedures = functools.cache(lambda: [])


@app.get("/healthz")
def healthz():
    return ("", 204)


@app.get("/metrics")
def metrics():
    return ("""
# HELP active_requests number of active requests
# TYPE active_requests gauge
active_requests 1
# HELP total_requests number of total requests
# TYPE total_requests counter
total_requests 48
    """, 200, {"content-type": "text/plain"})


@app.get("/capabilities")
def capabilities():
    return kapabilities()


@app.post("/explain")
def explain():
    return {
        "message": "explain is not supported",
        "details": None
    }


@app.get("/schema")
def schema():
    content_types.cache_clear()
    object_types.cache_clear()
    collections.cache_clear()
    return {
        "scalar_types": scalar_types(),
        "object_types": object_types(),
        "collections": collections(),
        "functions": functions(),
        "procedures": procedures()
    }


@app.post("/query")
def query():
    queryRequest = request.get_json()
    if queryRequest.get("query").get("aggregates"):
        return [
            {
                "aggregates": {
                    "name": "star_count",
                    "count": 0
                }
            }
        ], 200
    limit = queryRequest.get("query").get("limit")
    fields = queryRequest.get("query").get("fields")
    response = requests.get(
        url(queryRequest),
        headers={
            "Authorization": f"Bearer {api_key()}"
        }).json()["items"]
    rows = [
        {
            k: {"title": row.get("fields").get(k)} for k, _ in fields.items()
        } for row in response
    ]
    rows = rows[:limit]
    return [
        {
            "rows": rows
        }
    ], 200


def url(queryRequest):
    return f"{path_part(queryRequest)}?{query_part(queryRequest)}"


def path_part(queryRequest):
    return f"{base_url()}/spaces/{space()}/environments/{environment()}/entries"


def query_part(queryRequest):
    collection = queryRequest.get("collection")
    limit = queryRequest.get("query").get("limit")
    params = []
    params = params + [f"include={10}"]
    params = params + [f"content_type={collection}"]
    params = params + [f"limit={limit}"] if limit else []
    return "&".join(params)

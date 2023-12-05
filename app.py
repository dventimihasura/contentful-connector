from flask import Flask, request
import contentful_management
import os

app = Flask(__name__)
client = contentful_management.Client(os.getenv("API_KEY"))
space = client.spaces().find(os.getenv("SPACE"))
environment = space.environments().find(os.getenv("ENVIRONMENT"))


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
    return {
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
    }


@app.post("/explain")
def explain():
    return {
        "message": "explain is not supported",
        "details": None
    }


@app.get("/schema")
def schema():
    client = contentful_management.Client(os.getenv("API_KEY"))
    space = client.spaces().find(os.getenv("SPACE"))
    environment = space.environments().find(os.getenv("ENVIRONMENT"))
    content_types = environment.content_types().all()
    scalar_types = {
        "Int": {
            "aggregate_functions": {},
            "comparison_operators": {}
        },
        "String": {
            "aggregate_functions": {},
            "comparison_operators": {}
        },
        "json": {
            "aggregate_functions": {},
            "comparison_operators": {}
        },
    }
    object_types = {
        ct.id: {
            "description": ct.name,
            "fields": {
                f.id: {
                    "description": f.name,
                    "arguments": {},
                    "type": {
                        "type": "named",
                        "name": "Int"
                    } if f.type == "Integer"
                    else {
                        "type": "named",
                        "name": "String"
                    } if f.type == "Text"
                    else {
                        "type": "array",
                        "element_type": {
                            "type": "named",
                            "name": "json"
                        }
                    } if f.type == "Array"
                    else {
                        "type": "named",
                        "name": "String"
                    }
                } for f in ct.fields
            }
        } for ct in content_types
    }
    collections = [
        {
            "name": f"{ct.id}",
            "description": ct.description,
            "arguments": {},
            "type": ct.id,
            "deletable": False,
            "uniqueness_constraints": {},
            "foreign_keys": {}
        } for ct in content_types
    ]
    functions = []
    procedures = []
    return {
        "scalar_types": scalar_types,
        "object_types": object_types,
        "collections": collections,
        "functions": functions,
        "procedures": procedures
    }


@app.post("/query")
def query():
    queryRequest = request.get_json()
    content_type = environment.content_types().find(queryRequest["collection"])
    fields = []
    limit = None
    where = None
    if "query" in queryRequest:
        if "fields" in queryRequest["query"]:
            fields = queryRequest["query"]["fields"]
        if "limit" in queryRequest["query"]:
            limit = queryRequest["query"]["limit"]
        if "where" in queryRequest["query"]:
            where = queryRequest["query"]["where"]
    response = content_type.entries().all()
    rows = [
        {
            k: {"title": v["en-US"]} for k, v in row.to_json()["fields"].items() if k in fields
        } if fields else
        {
            k: {"title": v["en-US"]} for k, v in row.to_json()["fields"].items()
        } for row in response
    ]
    if where:
        rows = rows
    rows = rows[:limit]
    queryResponse = [
        {
            "rows": rows
        }
    ]
    if "query" in queryRequest:
        if "aggregates" in queryRequest["query"]:
            if "count" in queryRequest["query"]["aggregates"]:
                if "type" in queryRequest["query"]["aggregates"]["count"]:
                    if "star_count"==queryRequest["query"]["aggregates"]["count"]["type"]:
                        queryResponse = [
                            {
                                "aggregates": {
                                    "name": "star_count",
                                    "count": 0
                                }
                            }
                        ]
    return queryResponse, 200

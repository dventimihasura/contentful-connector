import contentful_management
import pprint
import os

client = contentful_management.Client(os.getenv("API_KEY"))

space = client.spaces().find(os.getenv("SPACE"))

environment = space.environments().find(os.getenv("ENVIRONMENT"))

content_types = environment.content_types().all()

{
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

pprint.pp({
    ct.name: {
        "description": ct.name,
        "fields": {
            f.id: {
                "description": f.name,
                "arguments": {},
                "type":
                {
                    "type": "named",
                    "name": "Int"
                } if f.type == "Integer" else
                {
                    "type": "named",
                    "name": "String"
                } if f.type == "Text" else
                {
                    "type": "array",
                    "element_type": {
                        "type": "named",
                        "name": "json"
                    }
                } if f.type == "Array" else
                {
                }
            } for f in ct.fields
        }
    } for ct in content_types
})

pprint.pp([
    {
        "name": f"{ct.name}Collection",
        "description": ct.description,
        "arguments": {},
        "type": ct.name,
        "deletable": False,
        "uniqueness_constraints": {},
        "foreign_keys": {}
    }
    for ct in content_types])

environments = space.environments().all()

entries = client.entries('qzv4c8mn4q4e', 'master').all()

entry = client.entries('qzv4c8mn4q4e', 'master').find('5lUJmelRUz4W6n5O0hNwmO')

pprint.pp(
    (
        client.spaces()
        .find('ofqpbs2ngj8y')
        .environments()
        .find('master')
        .content_types()
        .find('person')
        .entries()
        .all()[0]
    ).to_json()["fields"])

response = \
    (
        client.spaces()
        .find('ofqpbs2ngj8y')
        .environments()
        .find('master')
        .content_types()
        .find('person')
        .entries()
        .all()
    )

response

pprint.pp({
    "rows": [
        {
            k: v["en-US"] for k, v in row.to_json()["fields"].items()
        } for row in response
    ]
})

pprint.pp({
    "collection": "Person",
    "query": {
        "fields": {
            "name": {
                "type": "column",
	        "column": "name"
            },
            "age": {
                "type": "column",
	        "column": "age"
            },
            "nickname": {
                "type": "column",
	        "column": "nickname"
            },
        },
        "where": {
            "type": "binary_comparison_operator",
            "column": {
                "type": "column",
	        "name": "name",
	        "path": []
            },
            "operator": {
                "type": "equal"
            },
            "value": {
                "type": "scalar",
	        "value": "David"
            }
        }
    }
})

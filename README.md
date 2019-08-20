# Auth Server Scope Strawman

A proof of concept application for working out the functionality of the BrightHive Auth Server scope management.

## Disclaimer

This application is not intended for production usage and does not represent how BrightHive's user/client scope mechanism will ultimately be implemented. Use this code with caution.

## Supported Use Cases

### Unknown Client

The client is not known to the Auth Server. The system should reject the request with a The system should reject the request with a `401 Unauthorized` status code.

### Known Client with Invalid or Expired Access Token

The client is valid, but does not present a valid access token to the Auth Server. The system should reject the request with a `401 Unauthorized` status code.

### Known Client with Valid Access Token and Inappropriate Scope(s)

The client is valid and presents a valid access token to the Auth Server; however, the client does not have a scope that permits access to a specified resource. The system should reject the request with a `401 Unauthorized` status code.

### Known Client with Valid Access Token and Appropriate Scope(s)

The client is valid and presents a valid access token to the Auth Server. The system should honor the request and return the appropriate result with a valid status code, such as `201 OK`.

## Other Design Considerations

In addition to the use cases defined above, the application is also expected to handle the following levels of access restrictions:

### Column-Level Restrictions

Auth Server should be able to restrict the kinds of columns that a user can access. For example, if a client should not have access to a `Social Security Number` field, the system should be configurable to either completely hide the field or redact data in the field.

### Row-Level Restrictions

Auth Server should be able to restrict the kinds of rows that a client can access. For example, if a client should not have access to records for users between 18 and 45 (i.e. `Age >= 18 && Age < 46`), the system should be configurable to either completely hide the field or redact data in the field.

### URL-Specific Restrictions

Auth Server should be configurable to support restriction at the URL level. For example, the scope should be applied to a specific URL using regular expressions such as: `https://path.to.application/endpoint/[A-Z0-9]+`.

### Proposed Configuration

The following JSON document describes the proposed configuration model for the scope configuration.

```json
{
   "scope": "name-of-scope",
   "ruleset": [
       {
           "rule": {
               "resource": "/path/to/resource",
               "allowed_methods": [
                   "GET",
                   "POST",
                   "PUT",
                   "PATCH",
                   "DELETE"
               ],
               "restricted_fields": [
                   "field1",
                   "field2",
                   "field3",
                   "field4"
               ],
               "redacted_fields": [
                   "field5",
                   "field6",
                   "field7",
                   "field8"
               ],
               "policies": [

               ]
           }
       }
   ],
   "custom_rules": [
       {
           "custom_rule": {
               "description": "description of rule",
               "formula": "${age} > 17 || ${age} <= 65"
           }
       }
   ]
}
```

#### Scope

**scope** *(string)*: A human-readable name for the OAuth 2.0 scope. This serves as the identifier for the scope that is assigned to clients (and eventually human users).

#### Ruleset

**ruleset** *(list)*: The collection of rules associated with the scope.

#### Rule

**rule** *(map)*: A specific rule that governs a client's access to a resource.

```json
"rule": {
    "resource": "/path/to/resource",
    "allowed_http_methods": [
        "GET",
        "POST",
        "PUT",
        "PATCH",
        "DELETE"
    ],
    "restricted_fields": [
        {
            "field": "field1",
            "request": {
                "policy": ""
            },
            "response": {
                "policy": ""
            }
        },
        {
            "field": "field2",
            "request": {
                "policy": ""
            },
            "response": {
                "policy": ""
            }
        },
        {
            "field": "field3",
            "request": {
                "policy": ""
            },
            "response": {
                "policy": ""
            }
        },
        {
            "field": "field1",
            "request": {
                "policy": ""
            },
            "response": {
                "policy": ""
            }
        }
    ],
    "redacted_fields": [
        {
            "field": "field5",
            "policy": "*"
        },
        {
            "field": "field6",
            "policy": "*"
        },
        {
            "field": "field7",
            "policy": "*"
        },
        {
            "field": "field8",
            "policy": "${field8} != null"
        }
    ],
    "policies": [
        {
            "description": "description of policy",
            "policy": "${age} >= 18 && ${age} < 46",
            "mode": "restrict"
        }
    ]
}
```

Rules are made up of the following attributes:

#### Resource

**resource** *(string)*: The resource to be secured. This may be expressed as a regular expression, such as `https://mci.brighthive.net/[a-z]+` would apply the ruleset to all resources that match the regular expression.

#### Allowed HTTP methods

**allowed_http_methods** *(list)*: A collection of the HTTP methods (i.e. GET, POST, PUT, PATCH, DELETE) that can be executed on the resource by clients associated with the scope. The asterisk is a special character that implies `enable all HTTP verbs on the resource`.

#### Restricted Fields

**restricted_fields** *(list)*: The names of fields that should be restricted from requests and/or responses. For each field, it is possible to specify a policy for when the restriction should be applied. For example, `${access_date} != '2019-01-05'` would 

#### Redacted Fields

**redacted_fields** *(list)*: The name of fields that should be redacted from responses. For each field, it is possible to specify a policy for when the redaction should be applied. For example, one may

#### Policies

### Technical Considerations

* **Query Complexity**: The elaborate and often convoluted nature of handling these kinds of rules in a timely manner to be useful becomes significantly more complex to handle with standard relational database techniques. To aid in reducing this complexity, the complete solution will make use of GraphQL as a middle-tier between the database and the Auth Server. See [Graphene](https://graphene-python.org/) and [Graphene-SQLAlchemy](https://docs.graphene-python.org/projects/sqlalchemy/en/latest/).

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

## Other Design Goals

In addition to the use cases defined above, the application is also expected to handle the following levels of access restrictions:

### Column-Level Restrictions

Auth Server should be able to restrict the kinds of columns that a user can access. For example, if a client should not have access to a `Social Security Number` field, the system should be configurable to either completely hide the field or redact data in the field.

### Row-Level Restrictions

Auth Server should be able to restrict the kinds of rows that a client can access. For example, if a client should not have access to records for users between 18 and 45 (i.e. `Age >= 18 && Age < 46`), the system should be configurable to either completely hide the field or redact data in the field.

### URL-Specific Restrictions

Auth Server should be configurable to support restriction at the URL level. For example, the scope should be applied to a specific URL using regular expressions such as: `https://path.to.application/endpoint/[A-Z0-9]+`.

### Proposed Scope Configuration Model

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
                {
                    "field": "field1",
                    "request": true,
                    "response": true
                },
                {
                    "field": "field2",
                    "request": true,
                    "response": true
                },
                {
                    "field": "field3",
                    "request": true,
                    "response": true
                },
                {
                    "field": "field4",
                    "request": true,
                    "response": true
                }
               ],
               "redacted_fields": [
                {
                    "field": "field5",
                    "policy": "*"
                },
                {
                    "field": "field6",
                    "policy": "${field6} != null"
                },
               ],
               "access_policies": [
                {
                    "description": "description of policy",
                    "policy": "${age} >= 18 && ${age} < 46",
                    "mode": "restrict"
                }
               ]
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

Rules are made up of the following attributes:

#### Resource

**resource** *(string)*: The resource to be secured. This may be expressed as a regular expression, such as `https://mci.brighthive.net/[a-z]+` would apply the ruleset to all resources that match the regular expression.

#### Allowed HTTP methods

**allowed_http_methods** *(list)*: A collection of the HTTP methods (i.e. GET, POST, PUT, PATCH, DELETE) that can be executed on the resource by clients associated with the scope. The asterisk is a special character that implies `enable all HTTP verbs on the resource`.

#### Restricted Fields

**restricted_fields** *(list)*: The names of fields that should be restricted from requests and/or responses. For each restricted field, the following attributes must be specified:

- **field** *(string)*: The name of the field to restrict.
- **request** *(boolean)*: Determine whether or not the field should be restricted from being used in requests where a request body is provided. If true, the API will return an error status code if the field is specified in a request.
- **response** *(boolean)*: Determine whether the field should be restricted from response content. If true, the field will be stripped from responses.

#### Redacted Fields

**redacted_fields** *(list)*: The name of fields that should be redacted from responses. For each field, a policy for when the redaction should be applied may be specified. For example, one may choose to redact the names and social security numbers of individuals who are younger than 18 years old. For each redacted field, the following attributes must be specified:

- **field** *(string)*: The name of the field to redact.
- **policy** *(string)*: The redaction policy that should be applied to the field.

#### Access Policies

**access_policies** *(list)*: A collection of policies that govern access to the data by clients. For each policy, the following fields must be specified: 

- **description** *(string)*: A human-readable description of the policy.
- **policy** *(string)*: The rules that govern when the policy should be applied.
- **mode** *(string)*: How the policy should be applied to the field (`redact` or `restrict`).

### Technical Considerations

- **Reinventing the Wheel**: There may be certain questions as to why one would choose to implement a brand new security mechanism for this kind of application. A protocol known as [UMA2.0](https://www.riskinsight-wavestone.com/en/2018/09/demystifying-uma2/) that mostly meets this use case exists. UMA2.0 is based on OAuth 2 (actually designed to be an additional OAuth 2.0 flow). It has been successfully used to solve problems such as:
  - A document owner can share it with other people; for example, a patient can share (different) medical data with his/her spouse, relatives or doctor.
  - An application owner can design rules allowing certain enterprise employees (or business partners) to access an application/API.
  
  There are several reference implementations of UMA2 available, such as [Gluu](https://gluu.org/docs/gg/), [HIE of One](https://github.com/shihjay2/hieofone-as) and [Pauldron](https://medium.com/@jafarim/introducing-pauldron-an-experimental-uma-server-63e669fe4a25); however, they are either experimental, in beta, or require some additional middleware to meet the use cases outlined in this document. Ultimately, it would be ideal to converge on a standard such as UMA2.0; however, further research is needed.

- **Query Complexity**: The elaborate and often convoluted nature of handling these kinds of rules in a timely manner to be useful becomes significantly more complex to handle with standard relational database techniques. To aid in reducing this complexity, the complete solution will make use of GraphQL as a middle-tier between the database and the Auth Server. See [Graphene](https://graphene-python.org/) and [Graphene-SQLAlchemy](https://docs.graphene-python.org/projects/sqlalchemy/en/latest/).

## A Few Examples

### Example 1: Full Access

Assume that a scope needs to be created that grants full access to all APIs.

```json
{
   "scope": "all:full-access",
   "ruleset": [
       {
           "rule": {
               "resource": "[\\S]+",
               "allowed_methods": [
                   "*"
               ]
           }
       }
   ]
}
```

### Example 2: Read-Only Access to a `Programs` Resource with a Restriction on Program Address Field

Assume that a scope needs to be created to grant read only access to `https://sandbox.brighthive.net/programs`.

```json
{
   "scope": "programs:read-only",
   "ruleset": [
       {
           "rule": {
               "resource": "https://sandbox.brighthive.net/programs",
               "allowed_methods": [
                   "GET"
               ],
               "restricted_fields": [
                {
                    "field": "program_address",
                    "request": true,
                    "response": true
                }
               ]
           }
       }
   ]
```

### Example 3: Read-Only Access to a `Participants` Resource with a Restriction on Participation Address Field and Redaction on SSN

Assume that a scope needs to be created to grant read only access to `https://sandbox.brighthive.net/participants`, the `participant_address` field needs to be restricted from requests and responses, and the SSN needs to be redacted for all records.

```json
{
   "scope": "get:participants-redaction",
   "ruleset": [
       {
           "rule": {
               "resource": "https://sandbox.brighthive.net/participants",
               "allowed_methods": [
                   "GET",
               ],
               "restricted_fields": [
                {
                    "field": "participation_address",
                    "request": true,
                    "response": true
                }
               ],
               "redacted_fields": [
                {
                    "field": "ssn",
                    "policy": "*"
                },
               ]
           }
       }
   ]
}
```

### Example 4: Read-Only Access to a `Participants` with a Redaction Based on Age

Assume that a scope needs to be created to grant read only access to `https://sandbox.brighthive.net/participants`, the `participant_address` field needs to be restricted from requests and responses, and all fields needs to be redacted for records where an individual is less than 18 years old.

```json
{
   "scope": "get:participants-id-only",
   "ruleset": [
       {
           "rule": {
               "resource": "https://sandbox.brighthive.net/participants",
               "allowed_methods": []
           }
       },
       {
           "rule": {
               "resource": "https://sandbox.brighthive.net/participants/[\\w]+",
               "allowed_methods": [
                   "GET"
               ],
               "restricted_fields": [
                {
                    "field": "participant_address",
                    "request": true,
                    "response": true
                }
               ],
               "access_policies": [
                {
                    "description": "description of policy",
                    "policy": "${age} < 18",
                    "mode": "redact"
                }
               ]
           }
       }
   ]
}
```

### Example 5: Read-Only Access to a `Participants` with a Restriction Based on Age

Assume that a scope needs to be created to grant read only access to `https://sandbox.brighthive.net/participants`, the `participant_address` field needs to be restricted from requests and responses, and all fields needs to be restricted for records where an individual is less than 18 years old.

```json
{
   "scope": "get:participants-id-only",
   "ruleset": [
       {
           "rule": {
               "resource": "https://sandbox.brighthive.net/participants",
               "allowed_methods": []
           }
       },
       {
           "rule": {
               "resource": "https://sandbox.brighthive.net/participants/[\\w]+",
               "allowed_methods": [
                   "GET"
               ],
               "restricted_fields": [
                {
                    "field": "participant_address",
                    "request": true,
                    "response": true
                }
               ],
               "access_policies": [
                {
                    "description": "description of policy",
                    "policy": "${age} < 18",
                    "mode": "redact"
                }
               ]
           }
       }
   ]
}
```

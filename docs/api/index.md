# API overview

25 endpoints. Every screen the SDK draws is one of them, so anything the SDK
can do, you can do yourself.

## Base URLs

| Environment | Base URL |
|-------------|----------|
| Demo | `https://ekyc.demo.elitesoft.iq` |
| Staging | `https://ekyc.stg.elitesoft.iq` |
| Production | Issued with your credentials |

All paths in these docs are relative to `/api`. `POST /core/sessions/start`
means `POST https://ekyc.demo.elitesoft.iq/api/core/sessions/start`.

## Two families

The split matters, because it maps exactly onto the two credentials.

<div class="grid cards" markdown>

-   **`/core/*`**

    ---

    Server-to-server and client operations. Some take an API key, some take a
    session token, and [Authentication](authentication.md) says which.

    Sessions, documents, liveness, record checks, data ingest.

-   **`/flow/*`**

    ---

    The customer-facing journey. Session token only, always. The record is read
    from the token, never from the request.

    Steps, schemas, form submission, change requests.

</div>

## Conventions

**JSON in, JSON out, `snake_case` both ways.** Request bodies are deserialised
as snake_case and responses are serialised the same. `document_type_id`, not
`documentTypeId`.

**Identifiers are ULIDs.** 26 characters, Crockford base32, lexicographically
sortable by creation time. `01H1W1DE6X9Z5YEP5Y8DHR3H7J`. Treat them as opaque
strings.

**Enums travel as integers, sometimes with a string beside them.** `status: 4`
is `Approved`. Webhook payloads include both `status` and `status_value` so you
can log the readable form and branch on the number. Endpoint responses send the
integer.

**Timestamps are UTC ISO 8601.** `2026-08-26T12:30:00Z`.

**Document uploads are `multipart/form-data`.** Everything else is
`application/json`.

**No API version in the path.** The service is versioning-capable but no
endpoint declares a version today, so routes are `/api/core/...` rather than
`/api/v1/core/...`. Breaking changes are coordinated with you before they ship.

## Status codes

| Code | Meaning |
|------|---------|
| `200` | Success with a body |
| `204` | Success, no body |
| `400` | Business rule rejected the request. The body names which. |
| `401` | Credential missing, malformed or wrong |
| `404` | Resource not found, or not yours |
| `409` | Conflict, currently only duplicate ingest on `POST /core/store` |
| `422` | Validation failure. The body names the field. |
| `500` | Ours. Retry, then tell us. |

Error bodies carry a stable `Code`, a human-readable `Description`, and a
`Field` when the failure is a specific one. Show `Description` to a user; branch
on `Code`. See [Errors](errors.md).

## Interactive reference

The service publishes OpenAPI, and Swagger UI is available on non-production
environments at `/swagger`. Every endpoint carries a description, an example
request and example responses.

- Demo: [ekyc.demo.elitesoft.iq/swagger](https://ekyc.demo.elitesoft.iq/swagger)
- Staging: [ekyc.stg.elitesoft.iq/swagger](https://ekyc.stg.elitesoft.iq/swagger)

Use these pages for how the endpoints fit together, and Swagger for the
exhaustive schema of any single one.

## Endpoint index

### Sessions and records

| | Path | Auth | Page |
|-|------|------|------|
| <span class="ek-m post">POST</span> | `/core/sessions/start` | API key | [Sessions](sessions.md#start-a-session) |
| <span class="ek-m post">POST</span> | `/core/records/attempts` | Session | [Sessions](sessions.md#open-an-attempt) |
| <span class="ek-m post">POST</span> | `/core/sessions/complete` | Session | [Sessions](sessions.md#complete-a-session) |
| <span class="ek-m get">GET</span> | `/core/settings` | Either | [Sessions](sessions.md#tenant-settings) |
| <span class="ek-m get">GET</span> | `/core/records/{id}/checks` | Session | [Records](records.md#get-record-checks) |

### Flow

| | Path | Auth | Page |
|-|------|------|------|
| <span class="ek-m get">GET</span> | `/flow/step` | Session | [Flow](flow.md#get-the-current-step) |
| <span class="ek-m post">POST</span> | `/flow/step/previous` | Session | [Flow](flow.md#step-back) |
| <span class="ek-m get">GET</span> | `/flow/conditions` | Session | [Flow](flow.md#conditions) |
| <span class="ek-m post">POST</span> | `/flow/conditions` | Session | [Flow](flow.md#conditions) |
| <span class="ek-m get">GET</span> | `/flow/documents` | Session | [Flow](flow.md#documents-schema) |
| <span class="ek-m get">GET</span> | `/flow/information` | Session | [Flow](flow.md#information) |
| <span class="ek-m post">POST</span> | `/flow/information` | Session | [Flow](flow.md#information) |
| <span class="ek-m post">POST</span> | `/flow/change-request/verify` | None | [Flow](flow.md#verify-a-document-change-request) |

### Documents

| | Path | Auth | Page |
|-|------|------|------|
| <span class="ek-m post">POST</span> | `/core/documents` | Session | [Documents](documents.md#submit-a-document) |
| <span class="ek-m post">POST</span> | `/core/documents/update` | Session | [Documents](documents.md#update-a-document) |
| <span class="ek-m get">GET</span> | `/core/documents/{id}/data` | Session | [Documents](documents.md#read-extracted-data) |
| <span class="ek-m post">POST</span> | `/core/documents/{id}/data` | Session | [Documents](documents.md#submit-customer-entered-data) |
| <span class="ek-m post">POST</span> | `/core/documents/{id}/nfc-data` | Session | [Documents](documents.md#submit-nfc-chip-data) |
| <span class="ek-m post">POST</span> | `/core/documents/store-update` | API key | [Records](records.md#store-a-document-update) |

### Liveness

| | Path | Auth | Page |
|-|------|------|------|
| <span class="ek-m post">POST</span> | `/core/liveness/create` | Session | [Liveness](liveness.md#azure-face) |
| <span class="ek-m post">POST</span> | `/core/liveness/verify` | Session | [Liveness](liveness.md#azure-face) |
| <span class="ek-m post">POST</span> | `/core/liveness/verify/passive` | Session | [Liveness](liveness.md#innovatrics) |
| <span class="ek-m post">POST</span> | `/core/liveness/verify/active` | Session | [Liveness](liveness.md#innovatrics) |

### Data and capabilities

| | Path | Auth | Page |
|-|------|------|------|
| <span class="ek-m post">POST</span> | `/core/store` | API key | [Records](records.md#store-kyc-data) |
| <span class="ek-m post">POST</span> | `/core/records/{id}/international-transactions/access` | API key | [Records](records.md#request-international-transaction-access) |

## Where to start

Reading in order: [Authentication](authentication.md), then
[Sessions and attempts](sessions.md), then [Webhooks](webhooks.md). Those three
are the whole backend integration. The rest matters only if you are drawing the
customer-facing screens yourself.

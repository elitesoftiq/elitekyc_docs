# Security and data

Written for the person doing the security review. Where something is a
deployment choice rather than a product guarantee, it says so.

## Credentials

Two kinds, with deliberately different reach.

| Credential | Who holds it | Reach | Lifetime |
|-----------|-------------|-------|----------|
| API key and secret | Your backend, only | Every `/core/*` endpoint for your tenant | Until rotated |
| Session token | The customer's device | One record, scoped to what that record's flow permits | 30 minutes |

The API key is HTTP Basic: `Authorization: Basic base64(key:secret)`. The
session token is a JWT carrying the tenant, record and session, sent as
`Authorization: Bearer <token>`.

!!! danger "The API key never goes on a device"
    Anything shipped in a mobile binary is extractable. The API key
    authenticates as your whole tenant, so putting it in an app means anyone
    who unpacks the app can start sessions, read records and push data as you.

    Your backend calls `POST /core/sessions/start` and hands the *session
    token* to the app. That token is worth one record for thirty minutes.

    The SDK does accept a secret directly through `KycSession.withSecret()`.
    That path exists so a demo can be wired up in five minutes. It is not for
    production, and this is the only place these docs say otherwise.

## Session scoping

A session token is bound to one record at issue time. The claims carry the
record id, and every `/flow/*` endpoint reads the record from the token rather
than from the request body. A caller cannot address another customer's record
by changing an id, because there is no id in the request to change.

When an attempt is opened on a terminal record and a new attempt is permitted,
a new record is created and a *fresh token* is returned. The old token does not
follow the customer to the new record.

## Tenant isolation

Tenant scoping is enforced at the data-access layer, not in each handler.
Entity Framework global query filters apply the tenant predicate to every query
against a tenant-owned entity, so a handler that forgets to filter still cannot
read across tenants. Bypassing the filter requires calling a differently named
method, which makes every bypass visible in review and in a grep.

The tenant is resolved from the authenticated credential by middleware, before
any handler runs. It is never taken from a request body, header or query
parameter.

## Data at rest and in transit

- Transport is HTTPS, with HSTS and HTTP-to-HTTPS redirection on every
  non-development environment.
- Document images and selfies live in S3-compatible object storage, never in
  the database and never in a public bucket.
- Images reach a reviewer's browser as presigned URLs with a short expiry. The
  URL, not the object, is the thing that is authorised, and it stops working.
- NFC chip data arrives as encrypted data groups and is parsed server side. The
  raw groups are not exposed back through the API.
- Database encryption at rest and key management are properties of the
  deployment. For a managed or on-premise deployment, we work to your standard.

## Personal data

The data EliteKYC holds is, by definition, the most sensitive category your
product touches: government identifiers, dates of birth, portraits, biometric
templates, location.

- **Geolocation is opt-in per tenant** and off by default. When it is on, the
  client collects it and it becomes part of the record.
- **Retention** is a deployment policy rather than a hardcoded product rule.
  Bring your jurisdiction's requirement and we will configure to it.
- **Audit history** records who viewed and who changed what, and is intended to
  outlive operational logs.
- **Logs and errors** go to Serilog and Sentry with personally identifiable
  information disabled in the Sentry integration by default.

## Access control in the back office

Permissions are granular rather than role-shaped, which matters when an auditor
asks who could have approved a specific record.

Separate rights exist for view, view-any, create, update, delete, restore,
maker, checker, editor, AML checker, AML viewer, data correction and PDF
export. Maker and checker are distinct permissions specifically so that
segregation of duties is enforceable: the same person cannot propose and
approve the same change when maker-checker is on.

Every review action writes a history entry with the actor and timestamp,
including automated ones, so the trail does not have gaps where a machine acted.

## Webhook security

You choose how a delivery authenticates itself to your endpoint: bearer token,
basic auth, an API key in a header you name, or custom headers. Configured per
subscription in the back office.

There is no HMAC payload signature today. If you need cryptographic proof of
origin rather than a shared secret, say so during scoping. In the meantime,
treat the webhook as a *notification* rather than as data: before acting, read
the record's current status back with `POST /core/sessions/start` using your
API key. A forged payload then cannot make you act on a status the server does
not agree with, which holds regardless of what signing exists.

See [Webhooks](../api/webhooks.md#verifying-a-delivery-came-from-us).

## Abuse and retry limits

- Session tokens expire in 30 minutes.
- A record with an attempt awaiting review rejects a new attempt with
  `Kyc.AttemptInFlight`, so a customer cannot open unlimited parallel attempts.
- An approved record rejects new attempts outright.
- A rejected record only permits another attempt if the tenant has resubmission
  enabled.
- Re-verification rules carry a per-day trigger cap.
- Webhook delivery has a circuit breaker and a hard 72-hour retry ceiling.

## Questions we expect and answer directly

**Can you run in our infrastructure?** Yes. The service is containerised with
PostgreSQL, Redis and S3-compatible storage as the only stateful dependencies.

**Where is data hosted?** Depends on the deployment. The managed environments
run on DigitalOcean. On-premise and other regions are part of the commercial
conversation.

**Which third parties see customer data?** The OCR, liveness and AML providers
configured for your tenant. Liveness is Azure Face or Innovatrics, selected per
tenant, and you can ask for the current list of subprocessors.

**Can we get a penetration test report?** Ask, and we will tell you what exists
and when it was done. We would rather answer that plainly than not answer it.

---

Next: the [Quickstart](../quickstart.md), or the [API overview](../api/index.md).

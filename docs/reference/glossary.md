# Glossary

Terms as they are used in this system, not as they are used generally.

### Active liveness

Liveness detection that asks the person to do something, verified from a
MagnifEye recording produced by the Innovatrics SDK. Stacks on top of passive
liveness rather than replacing it. See [Liveness](../api/liveness.md).

### AML

Anti-money laundering. Screening a person against sanctions lists, politically
exposed person lists and watchlists. Decisions here are `Ok` or `Hit`, and a
hit routes to a human rather than auto-rejecting.

### Attempt

One pass through the verification flow. A record can have several over time.
Opened with `POST /core/records/attempts`, which is also where every business
rule about whether a new attempt is allowed lives.

### Checker

The reviewer who approves or rejects what a maker proposed. A distinct
permission from Maker, so segregation of duties is enforceable. See
[Reviewing records](../portal/records.md#maker-checker).

### Conditions

The short form at the start of the flow whose answers decide which documents
are required. Configured as a schema in the back office.

### Data group

A numbered block of data on a document's NFC chip. DG1 is the MRZ, DG2 the
portrait, DG11 extended personal details, and so on. Read by the client, parsed
by the server.

### Document change request

A scoped request for the customer to resubmit specific documents. Created when
a reviewer rejects a document, or when a capability like international
transfers needs a document that is not on file. Carries a secret the customer
exchanges for a scoped session token.

### Decision

What a check concluded: `Pending`, `Passed`, `Failed` or `ManualReview`.
Distinct from **status**, which is whether the check ran at all.

### Maker

The reviewer who proposes changes to a record for a checker to approve.

### Manual review

Routing a record to a human. Either because a check could not settle it, or
because the tenant sends every record to review regardless.

### MRZ

Machine-readable zone. The block of monospaced characters at the bottom of a
passport or ID card, with check digits that make it self-validating. More
trustworthy than OCR of the printed fields, less trustworthy than the chip.

### NFC

Near-field communication. Reading the chip embedded in a passport or ID card.
Chip data is signed by the issuing authority, which makes it the most
trustworthy source available. Android and iOS only.

### OCR

Optical character recognition. Reading printed characters from a photograph.
The fallback when there is no chip or MRZ.

### Passive liveness

Liveness detection from a single still selfie, with nothing asked of the
person. Faster than active liveness and less intrusive.

### Record

One customer's verification, identified by your `uid`. Holds the documents,
extracted data, check results and history. Its **status** is the thing your
product gates on. See
[the record lifecycle](../overview/how-it-works.md#the-record-lifecycle).

### Schema

A configuration defining a form or a set of document requirements. Three kinds:
conditions, information and documents. Built in the back office, rendered by
your client. Versioned, so in-flight records keep the schema they started on.

### Session

An authenticated period of work on one record, represented by a JWT valid for
30 minutes. Issued by `POST /core/sessions/start`. Bound to one record at
issue, which is why `/flow/*` endpoints never take a record id.

### Session token

The JWT a client uses. One record, thirty minutes. Distinct from the **API
key**, which authenticates as your whole tenant and never leaves your backend.

### Status (check)

Whether a check ran: `Pending`, `ReadyForProcessing`, `InProgress`, `Succeeded`
or `Failed`. `Failed` here means it could not complete, which is not the same
as a `Failed` **decision**.

### Status (record)

Where a record stands in its lifecycle, from `Pending` to `Approved`,
`Rejected` or `Cancelled`. The one field your product should branch on. Full
table in
[the record lifecycle](../overview/how-it-works.md#the-record-lifecycle).

### Tenant

One customer of EliteKYC, meaning you. Owns its own records, schemas, check
thresholds, webhooks and users. Isolation is enforced in the data layer rather
than in each handler.

### UID

Your identifier for a customer, supplied when starting a session. Max 50
characters, alphanumeric with dashes and underscores. What joins an EliteKYC
record back to your user.

### ULID

The identifier format used throughout. 26 characters, Crockford base32,
lexicographically sortable by creation time. Treat as an opaque string.

### Verification method

Which liveness provider a tenant uses: Azure or Innovatrics. Determines which
liveness endpoints the client calls. Read it from `GET /core/settings` rather
than hardcoding it.

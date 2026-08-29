# Capabilities

What is supported, stated plainly. Anything marked configurable is a per-tenant
setting your team controls in the back office, not a code change and not a
support ticket.

## Documents

| Document | Key | Sides | Chip | Handler |
|----------|-----|-------|------|---------|
| Iraqi national card | `IQ_NATIONAL_CARD` | Front and back | Yes | Dedicated |
| Iraqi passport | `IQ_PASSPORT` | Front | Yes | Dedicated |
| Iraqi residence card | `IQ_RESIDENCE_CARD` | Front and back | No | Dedicated |
| Iraqi residence permit | `IQ_RESIDENCE_PERMIT` | Front | No | Generic |
| Iraqi visa | `IQ_VISA` | Front | No | Generic |
| International passport | varies | Front | Yes | General passport |
| Supporting documents | varies | Front | No | Image storage only |

Dedicated handlers know the layout of a specific document and extract more
reliably than a generic parser. The image-storage handler exists for utility
bills, bank statements and contracts, where you want the file on the record but
there is nothing to parse.

Adding a document type is configuration on our side, not a release. If you need
one that is not listed, ask.

### How data comes off a document

Four sources, and a field can be filled by more than one.

| Source | What it is | Trustworthiness |
|--------|-----------|-----------------|
| `NFC` | Read from the document's chip | Highest. Cryptographically signed by the issuer. |
| `MRZ` | The machine-readable zone, with check digits | High. Self-validating. |
| `OCR` | Characters recognised from the image | Good, and the fallback when there is no chip or MRZ. |
| `Manual` | Typed or corrected by the customer | Whatever your review process makes it. |

NFC reads data groups DG1, DG2, DG3, DG11, DG12, DG13 and DG14, which covers
the MRZ, the portrait, fingerprints where present, and the extended personal
and document details.

## Checks

Each check produces a status, a decision and a score. Thresholds are per tenant
per check.

| Check | Type | What it answers |
|-------|------|-----------------|
| `Expiration` | Document | Is the document still valid on the date it was submitted? |
| `FrontBack` | Document | Are these two images the front and back of the same card? |
| `Classification` | Document | Is this the document type the customer said it was, above your confidence threshold? |
| `FaceMatch` | Document | Is the portrait on the document the same person as the selfie? |
| `FaceLiveness` | Biometric | Is the face in front of the camera physically present? |
| AML screening | Compliance | Does this person appear on a sanctions or watchlist? |

Decisions are `Pending`, `Passed`, `Failed` or `ManualReview`. A check that
fails technically, say the OCR service was unreachable, carries the status
`Failed` separately from the decision, so an infrastructure problem is never
mistaken for a fraud signal.

The classification threshold accepts `0`, which skips classification entirely.
Useful for tenants with a single document type where the step adds nothing.

## Liveness

Two providers. Your tenant is set to one of them, and the client reads which
from `GET /core/settings` rather than hardcoding it.

=== "Azure Face"

    Server creates a one-time session, the client hands the session id and
    token to the Azure SDK, the client confirms completion. Works on Android,
    iOS and web.

    See [Liveness](../api/liveness.md#azure-face).

=== "Innovatrics"

    Passive liveness from a single still selfie, submitted as base64. If the
    tenant also requires active liveness, the passive response says
    `PendingActive` and the client follows with a MagnifEye recording. Android
    and iOS only.

    See [Liveness](../api/liveness.md#innovatrics).

Passive and active liveness are independently switchable, so a tenant can
require passive only, or both.

## The flow itself

Three schemas, all built in the back office by people who do not write code.

**Conditions** is a form whose answers select which documents are required.
Answer "resident" and you are asked for a residence card. Answer "citizen" and
you are asked for a national ID.

**Documents** defines the acceptable combinations. Groups express either/or, so
"national card, or passport plus visa" is a configuration, not a special case
in your code.

**Information** collects whatever else you need. Available field types: string,
number, select, textarea, checkbox, date, file, image, language, phone number,
signature, repeater, plus headers and paragraphs for structure. Fields carry
validation rules and visibility rules, so a field can appear only when an
earlier answer makes it relevant.

Any field can be mapped to a document field, which prefills it from OCR or NFC.

## Review and workflow

| Capability | Detail |
|-----------|--------|
| Manual review | Optionally route every record to a human, including ones that passed every check. |
| Maker-checker | One reviewer proposes changes, a second approves them. Switchable per tenant. |
| Record claiming | A reviewer claims a record so two people never work the same case. |
| Field-level review | Individual fields can be corrected, with the original preserved. |
| Rejection reasons | Your own catalogue, reusable, shown to the customer with the reviewer's comment. |
| Document-level rejection | Reject one document, not the whole application. |
| Audit history | Every action recorded with actor and timestamp, including automated ones. |
| PDF export | A record and its evidence as a single file. |
| Permissions | Separate view, create, update, delete, maker, checker, editor, AML checker, AML viewer, data correction and export rights. |

## Re-verification

Rules that fire after approval.

- **Triggers:** document expiry, a fixed interval in days, or membership of a
  targeted group.
- **Targeting:** limit a rule to users matching criteria on their own record
  data. Empty targeting means everyone the triggers match.
- **Blocking:** mark a rule blocking and we tell you the customer should be
  locked out until they re-verify. Your app enforces it.
- **Deadlines and reminders:** give the customer N days, remind them M days
  before the deadline.
- **Rate caps:** limit how many re-verifications start per day, so a rule
  covering a million users does not page your support team on day one.
- **Rehearsal mode:** run the rule and record what it would have done without
  contacting anyone. Available per rule and per tenant.

## Integration surface

| Surface | Detail |
|---------|--------|
| Mobile SDK | Flutter. Android and iOS in full, web with Azure liveness and no NFC. |
| REST API | 25 endpoints, snake_case JSON, OpenAPI described. |
| Webhooks | 8 event types, per-subscription auth, exponential backoff with a 72-hour retry window. |
| Server-to-server ingest | Push records verified elsewhere into EliteKYC with `POST /core/store`. |
| Languages | English, Arabic and Kurdish Sorani, with automatic right-to-left layout. |

## What we do not do

Worth stating so you do not discover it at integration time.

- No native iOS or Android SDK. The mobile SDK is Flutter. If your app is
  native, you either embed a Flutter module or drive the API yourself.
- No hosted web verification flow you can link to. The SDK targets your app.
- No HMAC signature on webhook payloads today. Authenticate the delivery with
  the per-subscription bearer token, basic auth or API key header instead, and
  see [Webhooks](../api/webhooks.md#verifying-a-delivery-came-from-us).
- Document coverage is strongest for Iraq. Other jurisdictions go through the
  general passport handler or a new dedicated handler we build.

---

Next: [Architecture](architecture.md), or [Security and data](security.md) if
you are here for the security review.

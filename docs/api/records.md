# Records and data

Reading check results, pushing records verified elsewhere, and requesting extra
capabilities on an approved customer.

API key on everything here except `GET /core/records/{id}/checks`, which takes
a session token.

---

## Get record checks

<span class="ek-m get">GET</span> <span class="ek-path">/core/records/{id}/checks</span> <span class="ek-auth">session</span>

Every check result on a record: document, biometric and AML.

### Response `200`

```json
{
  "document_checks": [
    {
      "id": "01H1W1DH0M4P5Q6R7S8T9V0W1X",
      "document_id": "01H1W1DF8K2M3N4P5Q6R7S8T9V",
      "document_type": "national_id",
      "check_type": "Expiration",
      "status": 4,
      "decision": 2,
      "score": 0.95,
      "started_at": "2026-08-26T10:00:00Z",
      "completed_at": "2026-08-26T10:01:00Z",
      "completed": true
    },
    {
      "id": "01H1W1DH1N5Q6R7S8T9V0W1X2Y",
      "document_id": "01H1W1DF8K2M3N4P5Q6R7S8T9V",
      "document_type": "national_id",
      "check_type": "FrontBack",
      "status": 4,
      "decision": 2,
      "score": 0.98,
      "started_at": "2026-08-26T10:00:00Z",
      "completed_at": "2026-08-26T10:01:00Z",
      "completed": true
    }
  ],
  "biometric_checks": [
    {
      "id": "01H1W1DH2P6R7S8T9V0W1X2Y3Z",
      "check_type": "Liveness",
      "status": 4,
      "decision": 2,
      "score": 0.92,
      "started_at": "2026-08-26T10:00:00Z",
      "completed_at": "2026-08-26T10:01:00Z",
      "completed": true
    }
  ],
  "aml_checks": [
    {
      "id": "01H1W1DH3Q7S8T9V0W1X2Y3Z4A",
      "status": 4,
      "decision": 1,
      "score": 0,
      "started_at": "2026-08-26T10:00:00Z",
      "completed_at": "2026-08-26T10:02:00Z",
      "completed": true
    }
  ]
}
```

### Reading the numbers

Two fields that are easy to conflate, and they answer different questions.

**`status`** is whether the check *ran*.

| Value | Status | Meaning |
|:-----:|--------|---------|
| `1` | `Pending` | Created, not queued. |
| `2` | `ReadyForProcessing` | Queued. |
| `3` | `InProgress` | Running. |
| `4` | `Succeeded` | Completed. |
| `5` | `Failed` | Could not complete. A technical failure, not a verdict. |

**`decision`** is what it *concluded*.

| Value | Decision |
|:-----:|----------|
| `1` | `Pending` |
| `2` | `Passed` |
| `3` | `Failed` |
| `4` | `ManualReview` |

AML decisions use their own scale: `1` is `Ok`, `2` is `Hit`. An AML check's
`decision` is nullable, so it can be absent before screening resolves.

!!! info "`status: 5` is not a fraud signal"
    A check with `status: 5` never produced a verdict. The OCR service was
    unreachable, or the image could not be processed. Keeping this separate
    from `decision: 3` is deliberate: an infrastructure problem should never
    look like a failed customer.

`completed` tells you whether the check has finished, and `score` is nullable
until it has. A record carries superseded checks too, from before a document
was replaced and its checks rerun, so a document with several entries of the
same `check_type` is normal. The newest id wins, and ULIDs sort by creation
time, so ordering by id descending gives you the current picture. Keep the rest
for the audit trail.

### When to call this

For diagnostics, and for showing a reviewer or support agent why a record
landed where it did. Not for driving your product state.

!!! warning "This one takes a session token, unlike the rest of this page"
    Your API key will not open it. A backend that wants to read checks has to
    call `POST /core/sessions/start` for that `uid` first and use the token
    that comes back, which also emits a `SessionCreated` webhook.

    That cost is the reason to treat this as a diagnostic call rather than a
    routine one.

**Do not poll this endpoint to find out whether a customer is verified.** The
record's status arrives by [webhook](webhooks.md). Polling costs you latency,
costs us load, fires a `SessionCreated` event per check, and gets the answer
later than the webhook would have.

---

## Store KYC data

<span class="ek-m post">POST</span> <span class="ek-path">/core/store</span> <span class="ek-auth">API key</span>

Push a record that was verified somewhere else. No session, no SDK, no
customer-facing flow. Use it to migrate an existing customer base, or when
another system already does capture and you want EliteKYC to hold the audit
record and run the checks.

### Request

```json
{
  "record": {
    "uid": "123456789",
    "first_name": "John",
    "second_name": "Doe",
    "third_name": "Smith",
    "fourth_name": "Anderson",
    "english_full_name": "John Doe Smith",
    "face_image": "<optional base64 image>"
  },
  "documents": [
    {
      "key": "passport",
      "front_image": "<required base64 image>",
      "back_image": "<optional base64 image>",
      "data": {
        "document_number": "A1234567",
        "expiration_date": "2031-08-26",
        "country": "US"
      },
      "checks": {
        "DocumentExpirationCheck": { "passed": true, "score": 0.98 }
      }
    }
  ],
  "information": {
    "SubmittedBy": "agent@example.com",
    "SubmissionDate": "2026-08-26T10:00:00Z",
    "Source": "BranchOnboarding"
  },
  "attachments": {
    "selfie": "<required base64 image>"
  },
  "checks": {
    "expiration": true,
    "classification": true,
    "liveness": true,
    "face_match": true
  }
}
```

| Section | Purpose |
|---------|---------|
| `record` | Identity fields and an optional face image. |
| `documents` | Images, extracted data, and any check results you already have. |
| `information` | Free-form metadata stored on the record. |
| `attachments` | The selfie. Required. |
| `checks` | Which checks *we* should run. Anything true here is evaluated on our side. |

The `checks` flags matter. Set one true and we run that check ourselves rather
than trusting yours. Set it false and we take the result you supplied in
`documents[].checks`.

### Response `200`

```json
{ "id": "01H1W1DE6X9Z5YEP5Y8DHR3H7J" }
```

### Response `409`

```json
{ "id": "01H1W1DE6X9Z5YEP5Y8DHR3H7J", "kyc_status": "Pending" }
```

A record with that `uid` already exists. The response tells you which one and
where it stands, so a conflict is recoverable rather than a dead end. Retrying
a bulk import is safe.

---

## Store a document update

<span class="ek-m post">POST</span> <span class="ek-path">/core/documents/store-update</span> <span class="ek-auth">API key</span>

The server-to-server counterpart of document resubmission. Use it when the
replacement documents were collected by an external system rather than by the
SDK.

Send **every** document the change request asked for. Partial submissions are
rejected, because a change request completes as a unit.

### Response `200`

```json
{
  "documents": [
    {
      "id": "01H1W1DF8K2M3N4P5Q6R7S8T9V",
      "document_type_id": "01H1W1DG9L3N4P5Q6R7S8T9V0W",
      "document_type_key": "IQ_NATIONAL_CARD",
      "document_number": "AC398204",
      "issue_date": "2026-08-26",
      "expire_date": "2036-08-26"
    }
  ]
}
```

This completes the change request. An already-approved record **stays
approved** while the new document is reviewed, so the customer is not locked
out of your product during a routine document refresh.

---

## Request international transaction access

<span class="ek-m post">POST</span> <span class="ek-path">/core/records/{id}/international-transactions/access</span> <span class="ek-auth">API key</span>

A worked example of gating a product capability behind an extra document.
International transfers typically need a passport, and a customer verified with
a national ID does not have one on file.

Rather than making you build the "ask for one more document" flow yourself,
this endpoint checks and, when needed, creates the change request and hands you
the secret to send the customer into the SDK's resubmission flow.

### Response `200`

=== "Passport already on file"

    ```json
    {
      "access_allowed": true,
      "passport_required": false,
      "redirect_to_kyc": false,
      "selfie_verification_required": false,
      "document_change_request_id": null,
      "document_change_request_secret": null,
      "required_document_types": []
    }
    ```

    Let the transaction through.

=== "Passport needed"

    ```json
    {
      "access_allowed": false,
      "passport_required": true,
      "redirect_to_kyc": true,
      "selfie_verification_required": true,
      "document_change_request_id": "01H1W1DJ4R8T9V0W1X2Y3Z4A5B",
      "document_change_request_secret": "3f9a2b1c8d7e6f5a4b3c2d1e0f9a8b7c",
      "required_document_types": ["IQ_PASSPORT"]
    }
    ```

    Send the customer into the SDK with the secret. See
    [document resubmission](../sdk/advanced.md#document-resubmission).

The change request is created or reused, so calling this repeatedly does not
pile up requests.

### Response `400`

`Kyc.RecordMustBeApproved`. The record has to be approved before extra
capabilities can be requested.

---

Next: [Webhooks](webhooks.md).

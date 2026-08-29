# Errors

Every error carries a stable machine-readable code and a description written
for a human. Branch on the code. Show the description.

## Shape

```json
{
  "Code": "Kyc.AttemptInFlight",
  "Description": "A previous KYC attempt is awaiting review. You cannot open another attempt until it is resolved.",
  "Field": "uid"
}
```

| Key | Notes |
|-----|-------|
| `Code` | Stable. Safe to branch on. Never changes for a given condition. |
| `Description` | Human-readable, and safe to show a user. |
| `Field` | Present only when the failure is about a specific field. |

!!! note "These three keys are PascalCase"
    Everything else in the API is snake_case. Error bodies are the exception,
    so your deserialiser needs to handle `Code`, `Description` and `Field`
    exactly as written.

## Status code mapping

The error's type decides the HTTP status.

| Type | Status | Meaning |
|------|:------:|---------|
| Business | `400` | A rule rejected the request. The request was well-formed. |
| Validation | `422` | The request was malformed or a field was invalid. |
| Resource not found | `404` | It does not exist, or it is not yours. |
| Anything else | `500` | Ours. |

## KYC record

| Code | Status | Meaning |
|------|:------:|---------|
| `Kyc.NotFound` | 404 | No record with that identifier. |
| `Kyc.AlreadyExists` | 400 | A record with that `uid` already exists. |
| `Kyc.StepPrerequisiteNotMet` | 400 | Steps were called out of order. Read `GET /flow/step`. |
| `Kyc.PhoneNumberRequired` | 422 | Phone number required for record creation. |
| `Kyc.GeolocationRequired` | 422 | Geolocation is enabled for this tenant and none was supplied. |
| `Kyc.RecordCancelled` | 400 | The record is cancelled. Document upload is not allowed. |
| `Kyc.RecordRejectedNotResubmittable` | 400 | Rejected, and resubmission is off for this tenant. The session is read-only. |
| `Kyc.AttemptInFlight` | 400 | A previous attempt is awaiting review. |
| `Kyc.RecordAlreadyApproved` | 400 | Already approved. No further attempts. |
| `Kyc.RecordMustBeApproved` | 400 | The record must be approved before requesting this capability. |
| `Kyc.StepBackNotAllowed` | 400 | Step-back is disabled for this tenant. |

## Documents

| Code | Status | Meaning |
|------|:------:|---------|
| `DocumentManagement.DocumentNotFound` | 404 | No document with that identifier. |
| `DocumentManagement.DocumentTypeNotFound` | 404 | Unknown document type key. |
| `DocumentManagement.DocumentNoSideProvided` | 404 | No document side was provided. |
| `DocumentManagement.MissingBackImage` | 400 | Two-sided type, back image missing. |
| `DocumentManagement.NoFaceDetected` | 400 | This type must carry a portrait and none was found. |
| `DocumentManagement.MissingMrz` | 400 | This type must carry a readable MRZ and none was found. |
| `DocumentManagement.DuplicateDocumentTypeFound` | 400 | The same document type appears twice. |
| `DocumentManagement.DocumentUsedOnAnotherRecord` | 400 | This document already belongs to another KYC application. |
| `DocumentManagement.DocumentTypeDoesNotSupportNfc` | 400 | No chip on this document type. |
| `DocumentManagement.DocumentInspectionUnavailable` | 400 | Inspection failed. Retry. |
| `DocumentManagement.FaceExtractionError` | 500 | Could not extract a face from the image. |
| `DocumentManagement.StoringFailure` | 500 | Storage failed. Retry. |

### Change requests

| Code | Status | Meaning |
|------|:------:|---------|
| `DocumentManagement.DocumentResubmission.InvalidSecret` | 400 | The secret is wrong or expired. |
| `DocumentManagement.DocumentResubmission.InvalidCustomerInformation` | 400 | The customer details do not match. |
| `DocumentManagement.DocumentChangeRequestNotFound` | 400 | No such change request. |
| `DocumentManagement.DocumentChangeRequestMismatch` | 400 | The change request does not belong to this record. |

## Liveness and checks

| Code | Status | Meaning |
|------|:------:|---------|
| `AutoChecks.LivenessCheck.SessionNotFound` | 404 | No liveness session for this record. |
| `AutoChecks.LivenessCheck.OperationNotStarted` | 400 | The liveness SDK never ran. |
| `AutoChecks.LivenessCheck.ResultsNotAvailable` | 400 | The operation has not completed yet. |
| `AutoChecks.LivenessCheck.CreateNotSupportedForInnovatrics` | 400 | Innovatrics tenants call `/core/liveness/verify/passive` instead. |
| `AutoChecks.AML.EndpointNotConfigured` | 500 | The AML service is not configured. Ours. Tell us. |
| `FaceMatchCheck.NotFaceDetected` | 500 | No face in the image, so there is nothing to match. |

## Tenant and re-verification

| Code | Status | Meaning |
|------|:------:|---------|
| `TenantManagement.SettingsNotFound` | 404 | No settings for this tenant. |
| `ReVerification.RuleNotFound` | 400 | No such re-verification rule. |
| `ReVerification.NoTriggerSelected` | 400 | A rule needs at least one trigger. |
| `ReVerification.PeriodicIntervalRequired` | 400 | A periodic rule needs a positive interval. |
| `ReVerification.DocumentTypeAlreadyRequired` | 400 | Already required by the change request. |

## Handling errors well

### Distinguish the three kinds

They need different responses, and treating them alike is the usual mistake.

**The customer can fix it.** `MissingBackImage`, `NoFaceDetected`,
`MissingMrz`, `GeolocationRequired`. Show `Description`, let them retry the
step.

**The customer cannot fix it.** `RecordAlreadyApproved`, `AttemptInFlight`,
`RecordRejectedNotResubmittable`, `DocumentUsedOnAnotherRecord`. Do not show a
retry button. Route to support, or to a "we are reviewing this" state.

**You should fix it.** `StepPrerequisiteNotMet`, `DocumentTypeNotFound`,
`DuplicateDocumentTypeFound`. Bugs in your integration. Log with the full
request context.

### A pattern worth copying

```dart
Future<void> handle(ApiError error) async {
  switch (error.code) {
    case 'Kyc.RecordAlreadyApproved':
      return goToVerified();

    case 'Kyc.AttemptInFlight':
      return showPendingReview();

    case 'Kyc.RecordRejectedNotResubmittable':
      return showContactSupport();

    case 'Kyc.GeolocationRequired':
      return promptForLocationPermission();

    case 'DocumentManagement.DocumentUsedOnAnotherRecord':
      // Fraud signal, not a user error. No cheerful retry.
      logSecurityEvent(error);
      return showContactSupport();

    default:
      // Unknown codes will appear as we add them.
      // Description is written to be shown.
      return showMessage(error.description);
  }
}
```

Always keep the default branch. New codes ship, and falling back to
`Description` is safe because it is written for users.

### Retrying

| Situation | Retry? |
|-----------|--------|
| `500` | Yes. Backoff, a few attempts, then surface it. |
| `DocumentInspectionUnavailable` | Yes. Transient. |
| `StoringFailure` | Yes. Transient. |
| `400` business error | No. The rule will say the same thing next time. |
| `422` validation | No. Fix the request. |
| `401` | No. Fix the credential or get a fresh token. |

---

Next: the [back office](../portal/index.md).

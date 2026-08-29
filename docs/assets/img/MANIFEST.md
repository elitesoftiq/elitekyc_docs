# Screenshot manifest

Every image the docs reference, and where it came from.

All customer data in these files is destroyed, not hidden: each redacted region
is downscaled to a few percent and then blurred, so there is no original detail
left in the pixels to recover. Originals are not in this repo.

## Landed

| File | Page | Redacted |
|------|------|----------|
| `sdk-welcome.png` | [SDK overview](../../sdk/index.md) | Debug overlay removed |
| `sdk-conditions.png` | [SDK overview](../../sdk/index.md) | Debug overlay removed |
| `sdk-document-capture.png` | [SDK overview](../../sdk/index.md) | Whole ID card, both portraits. Capture brackets kept |
| `sdk-information.png` | [SDK overview](../../sdk/index.md) | Debug overlay removed |
| `sdk-liveness.png` | [SDK overview](../../sdk/index.md) | Face, inside the capture ring |
| `sdk-complete.png` | [SDK overview](../../sdk/index.md) | Debug overlay removed |
| `sdk-resubmission.png` | [Advanced use](../../sdk/advanced.md) | Debug overlay removed |
| `sdk-theme-comparison.png` | [Branding and language](../../sdk/customization.md) | Composite of two themes |
| `sdk-languages.png` | [Branding and language](../../sdk/customization.md) | Composite of three languages |
| `portal-dashboard.png` | [Back office](../../portal/index.md) | Tenant name, internal URL |
| `portal-record-list.png` | [Reviewing records](../../portal/records.md) | Tenant name, names, dates of birth |
| `portal-record-detail.png` | [Reviewing records](../../portal/records.md) | Tenant name, all name fields, date of birth, selfie |
| `portal-document-review.png` | [Reviewing records](../../portal/records.md) | Tenant name, both card images including the MRZ, selfie, name fields |
| `portal-form-builder.png` | [Building the flow](../../portal/schemas.md) | Tenant name |
| `portal-documents-builder.png` | [Building the flow](../../portal/schemas.md) | Tenant name |
| `portal-conditions-builder.png` | [Building the flow](../../portal/schemas.md) | Tenant name |
| `portal-checks.png` | [Checks and rules](../../portal/checks.md) | Tenant name |
| `portal-reverification.png` | [Checks and rules](../../portal/checks.md) | Tenant name |
| `portal-webhooks.png` | [Webhooks](../../api/webhooks.md) | Tenant name, endpoint URLs, internal IP |

## Still needed

An NFC capture (`sdk-nfc.png`) is the one gap left. Nothing references it yet,
so add the file and a figure on [SDK overview](../../sdk/index.md) together.

## Adding one

Drop the file in this folder under the exact name above. Redact before
committing: blur or pixelate faces, names, document numbers, MRZ lines, dates
of birth, tenant names and any internal hostname or IP. A soft blur over small
text is not enough on its own, downscale the region first.

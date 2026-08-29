# What EliteKYC does

No code on this page. If you are evaluating whether identity verification is
worth buying rather than building, start here.

## The problem

Financial regulators require you to know who your customers are before you let
them move money. In practice that means four questions, and every one of them
is harder than it sounds.

**Is this a real document?** Somebody uploads a photo of an ID card. Is it
expired? Is the front the same card as the back? Is it the type of document
they claimed? Is it a photo of a screen?

**Does the document say what they say it says?** Names, dates and numbers have
to come off the card and into your system, correctly, from documents printed in
Arabic and English, photographed in bad light at an angle.

**Is the person holding it the person on it?** A stolen ID plus a photo of the
victim from social media defeats naive face matching. You need to know the face
in front of the camera is physically present, right now.

**Are they someone you are allowed to onboard?** Sanctions lists, politically
exposed persons, adverse media. This is a screening problem, and it recurs.
Someone clean at signup can be sanctioned six months later.

## What we handle

EliteKYC covers all four, plus the part nobody budgets for: what happens when
the automated answer is "not sure".

<div class="grid cards" markdown>

-   **Document capture and reading**

    ---

    Guided camera capture with live blur, glare and low-light feedback, so the
    photo is usable the first time. Then OCR, machine-readable zone parsing,
    and NFC chip reading for documents that carry one. Iraqi national cards,
    passports, residence cards and visas are supported today, with
    document-specific handlers rather than one generic parser.

-   **Authenticity checks**

    ---

    Expiry, front-and-back consistency, document type classification with a
    confidence threshold you set, and face matching between the document
    portrait and the selfie. Each check produces a score and a decision, and
    each one is individually configurable per tenant.

-   **Liveness detection**

    ---

    Passive liveness from a single still selfie, with optional active liveness
    on top. Two providers are supported, Azure Face and Innovatrics, chosen per
    tenant. Neither is something an attacker defeats with a printed photo.

-   **AML screening**

    ---

    Sanctions and watchlist screening at onboarding, with hits routed to your
    compliance team rather than silently rejecting the customer.

-   **Human review that works**

    ---

    A maker-checker workflow: one reviewer proposes, another approves. Record
    claiming so two people do not review the same case. Full audit history of
    who did what and when. Rejection reasons your team defines, sent back to
    the customer with the specific documents that need redoing.

-   **Re-verification over time**

    ---

    Rules that fire when a document expires or on a fixed interval, targeted at
    a subset of users, with deadlines and reminders. Onboarding is a moment.
    Compliance is a state.

</div>

## What you still own

We are deliberate about where the boundary sits.

- **Your customers' relationship with you.** The SDK renders in your colours
  and your language, inside your app, on your navigation stack. Nothing in the
  flow says EliteKYC to the person using it.
- **The decision to let someone in.** We produce a status and the evidence
  behind it. Whether an approved record means the customer can open an account
  is your business logic, in your system.
- **Enforcement.** When a re-verification rule is marked blocking, we tell you.
  Locking the customer out of your app is your app's job. The verification
  engine never holds your product hostage.

## Why teams pick this over building it

Building the happy path is a sprint. What takes a year is everything else: the
review console, the audit trail, the retry semantics when a customer abandons
halfway, the rejection loop that sends someone back for just the one document
that failed, per-tenant configuration so risk can change a threshold without a
deploy, webhook delivery that survives your endpoint being down for an hour.

That work is already done here, and it is the part of the product we would
point a technical reviewer at first.

---

Next: [How verification works](how-it-works.md) walks through the actual
sequence, or jump to [Capabilities](features.md) for the feature-by-feature
detail.

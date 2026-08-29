# Troubleshooting

Ordered by how often it actually happens.

## The build broke and nothing changed

Almost always the Azure SDK access token. It expires on its own schedule,
typically within days, and the build that worked on Friday fails on Monday.

**Android** fails with:

```
Could not resolve com.azure:azure-ai-vision-face-ui
```

or a bare `401 Unauthorized` during Gradle sync.

**iOS** fails during `pod install` with an authentication error against
`msface.visualstudio.com`.

Ask us for a new token, then:

=== "Android"

    ```properties title="android/gradle.properties"
    elitePluginToken=THE_NEW_TOKEN
    ```

    ```bash
    flutter clean && flutter pub get
    ```

=== "iOS"

    Replace the stored credential in your Git credential helper or Keychain,
    then:

    ```bash
    cd ios
    pod deintegrate
    pod install
    ```

## The app crashes at the NFC step

Two causes, both in your Android host app rather than in the SDK.

**`MainActivity` does not extend `FlutterFragmentActivity`.** The Innovatrics
NFC reader is a native Fragment and needs a `FragmentActivity` host.

```kotlin title="android/app/src/main/kotlin/.../MainActivity.kt"
import io.flutter.embedding.android.FlutterFragmentActivity

class MainActivity : FlutterFragmentActivity()
```

**The Activity theme is not Material or AppCompat.** The reader uses Material
widgets, which throw on inflation under a plain theme.

```xml title="android/app/src/main/res/values/styles.xml"
<style name="NormalTheme" parent="Theme.MaterialComponents.Light.NoActionBar">
```

Set it in `values-night/styles.xml` as well. Details in
[Install and configure](installation.md#mainactivity-and-theme).

## NFC text is unreadable

White text on a light background, or grey on grey. The native reader inherits
`?android:textColorPrimary` from your Activity theme, and in dark mode that
resolves to something that does not work against the reader's own background.

Force the native theme light in `values-night/styles.xml` if your Flutter UI is
always light, and set the text colours explicitly:

```xml
<item name="android:textColorPrimary">#1A1A1A</item>
<item name="android:textColorSecondary">#4B4B4B</item>
```

## The release build crashes but debug is fine

R8 or ProGuard. Minification has to stay off for now.

```gradle title="android/app/build.gradle"
buildTypes {
    release {
        minifyEnabled false
        shrinkResources false
    }
}
```

The SDK ships ProGuard rules for when this changes. Today, turning
minification on strips classes the native SDKs resolve by reflection.

## Duplicate class or META-INF error at build time

```gradle title="android/app/build.gradle"
packaging {
    resources {
        excludes += "/META-INF/versions/9/OSGI-INF/MANIFEST.MF"
    }
}
```

## iOS linker or architecture errors

Three things, and it is usually the last one:

```ruby title="ios/Podfile"
platform :ios, '14.0'
use_frameworks! :linkage => :static
use_modular_headers!
```

`AzureAIVisionFaceUI` requires iOS 14 and static linkage. A dynamic-framework
build fails at link time with errors that do not name the cause.

## `AzureAIVisionFaceUI` spec not found

All three `source` lines have to be in the Podfile, in this order:

```ruby
source 'https://github.com/innovatrics/innovatrics-podspecs'
source 'https://cdn.cocoapods.org/'
source 'https://msface.visualstudio.com/SDK/_git/AzureAIVisionFaceUI.podspec'
```

Missing `cdn.cocoapods.org` breaks every ordinary pod. Missing the msface
source breaks only this one.

## The flow closes immediately after launch

`onFlowCompleted` fires and no screen appears. Startup failed. Two candidates:

**`GET /core/settings` failed.** Bad `baseUrl`, no network, or an invalid
session token. Attach a Dio interceptor and look at the actual response:

```dart
interceptors: [if (kDebugMode) LogInterceptor(responseBody: true)],
```

**Secret-based session start failed.** Wrong secret, or wrong environment for
that secret. The SDK swallows this and exits by design, so the interceptor is
how you see it.

## Liveness fails on every attempt

Check `GET /core/settings` and confirm `verification_method` matches what your
build supports.

| Symptom | Likely cause |
|---------|--------------|
| Azure tenant, liveness never starts | Azure native dependency did not download. Check the token and rebuild. |
| Innovatrics tenant, liveness never starts | `licence` is null or the DOT SDK did not initialise. Confirm the tenant has a licence configured. |
| Innovatrics tenant on web | Not supported. Innovatrics is Android and iOS only. |
| `decision: "Fail"` consistently | Genuine liveness failures, or the wrong recording format. Active liveness needs a MagnifEye recording from the Innovatrics SDK, not a phone-camera video. |

## Blank screen, or language will not switch

Language assets failed to resolve. Confirm `flutter pub get` finished without
errors, then:

```bash
flutter clean && flutter pub get
```

If you generate assets, rerun the generator:

```bash
flutter pub run build_runner build --delete-conflicting-outputs
```

## Session errors from the API

| Error code | What happened | What to do |
|-----------|---------------|------------|
| `Kyc.AttemptInFlight` | A previous attempt is awaiting review | Do not launch. Tell the customer the review is in progress. |
| `Kyc.RecordAlreadyApproved` | Already verified | Do not launch. |
| `Kyc.RecordRejectedNotResubmittable` | Rejected, and your tenant does not allow retries | Do not launch. Route to support. |
| `Kyc.GeolocationRequired` | Your tenant requires location and none was supplied | Implement `getCurrentLocation`. |
| `Kyc.StepPrerequisiteNotMet` | A step was launched out of order | Only relevant with `useCaseStep`. |
| `Kyc.StepBackNotAllowed` | Step-back is off for your tenant | Nothing on your side. The SDK hides the back button when `allow_step_back` is false. |

Full list: [Errors](../api/errors.md).

## Still stuck

Email [support@elitesoft.iq](mailto:support@elitesoft.iq) with the SDK version
from your `pubspec.lock`, the platform and OS version, your tenant's
`verification_method`, and the request and response from the failing call.
Redact the session token.

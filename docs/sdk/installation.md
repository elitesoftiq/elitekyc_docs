# Install and configure

Native setup first, because two of these steps are crash-on-launch if you skip
them. Budget half an hour the first time.

## Requirements

| Requirement | Version |
|-------------|---------|
| Flutter | 3.24 or later, below 4.0 |
| Dart | 3.5 or later, below 4.0 |
| Android `compileSdk` | 36 |
| Android `minSdk` | 26 recommended, 24 minimum |
| Kotlin | 2.1.0 or later |
| Android Gradle Plugin | 8.8.1 or later |
| iOS deployment target | 14.0 |

The iOS floor is 14.0 because the Azure Face liveness framework requires it.

## 1. Add the dependency

=== "Git"

    ```yaml title="pubspec.yaml"
    dependencies:
      elite_kyc:
        git:
          url: https://github.com/elitesoftiq/elitekyc-sdk-flutter.git
    ```

=== "Local path"

    If we sent you the SDK as an archive:

    ```yaml title="pubspec.yaml"
    dependencies:
      elite_kyc:
        path: ../elite_kyc
    ```

```bash
flutter pub get
```

## 2. Get the Azure SDK access token

The Azure Face liveness native frameworks come from private Microsoft
repositories that require authentication. We issue you a token separately.

!!! warning "This token expires, typically within days"
    When it does, Gradle sync fails with `Could not resolve
    com.azure:azure-ai-vision-face-ui`, or `pod install` fails to authenticate.
    Ask us for a new one. This is the single most common reason a build that
    worked yesterday does not work today.

    Renewal steps are in [Troubleshooting](troubleshooting.md#the-build-broke-and-nothing-changed).

## 3. Android

### gradle.properties

```properties title="android/gradle.properties"
android.useAndroidX=true
android.enableJetifier=true
org.gradle.jvmargs=-Xmx4G -XX:MaxMetaspaceSize=2G
elitePluginToken=YOUR_AZURE_SDK_ACCESS_TOKEN
```

The SDK's Gradle plugin reads `elitePluginToken` and injects the Azure Maven
repository for you.

!!! danger "Keep this token out of version control"
    `elitePluginToken` is a credential. Anyone who has it can pull from the
    private Microsoft feed as you, and a token committed to a repository stays
    in the history after you overwrite the line.

    Put it in a file git does not track. `~/.gradle/gradle.properties` in your
    home directory is read by every Gradle build on the machine and never sits
    inside a repo:

    ```properties title="~/.gradle/gradle.properties"
    elitePluginToken=YOUR_AZURE_SDK_ACCESS_TOKEN
    ```

    In CI, set it as `ORG_GRADLE_PROJECT_elitePluginToken` in the secret store
    rather than writing it to a file.

    If you have already committed one, rotating it is the only fix. Deleting
    the line does not remove it from history.

### app/build.gradle

```gradle title="android/app/build.gradle"
android {
    namespace = "com.yourcompany.yourapp"
    compileSdk = 36
    ndkVersion = "28.2.13676358"

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_1_8
        targetCompatibility = JavaVersion.VERSION_1_8
    }

    kotlinOptions {
        jvmTarget = JavaVersion.VERSION_1_8
    }

    defaultConfig {
        minSdk = 26
        targetSdk = 35
    }

    buildTypes {
        release {
            minifyEnabled false   // (1)!
            shrinkResources false
        }
    }

    packaging {
        resources {
            excludes += "/META-INF/versions/9/OSGI-INF/MANIFEST.MF"  // (2)!
        }
    }

    packagingOptions {
        jniLibs {
            excludes += ['lib/x86_64/*.so']
        }
    }
}
```

1.  Minification has to stay off for now. The SDK ships ProGuard rules for when
    that changes, but with R8 on today the release build crashes at runtime.
2.  Without this exclusion the build fails with a duplicate-class error from
    the bundled native dependencies.

### Permissions

```xml title="android/app/src/main/AndroidManifest.xml"
<uses-permission android:name="android.permission.INTERNET" />
<uses-permission android:name="android.permission.CAMERA" />
<uses-permission android:name="android.permission.RECORD_AUDIO" />
<uses-permission android:name="android.permission.ACCESS_FINE_LOCATION" />
```

No activity or service declarations. The SDK registers its own components.

`RECORD_AUDIO` is required by the camera subsystem during liveness video
capture, not because audio is stored.

### MainActivity and theme

!!! danger "Skip this and the NFC step crashes on launch"
    The Innovatrics NFC reader renders as a native Android Fragment using
    Material widgets. It needs a `FragmentActivity` host and a Material or
    AppCompat theme. Neither can be supplied by the SDK, because both are
    properties of your Activity.

**Extend `FlutterFragmentActivity`:**

```kotlin title="android/app/src/main/kotlin/.../MainActivity.kt"
import io.flutter.embedding.android.FlutterFragmentActivity

class MainActivity : FlutterFragmentActivity()
```

**Set a Material theme**, in both `values/styles.xml` and
`values-night/styles.xml`:

```xml title="android/app/src/main/res/values/styles.xml"
<style name="NormalTheme" parent="Theme.MaterialComponents.Light.NoActionBar">
    <item name="android:windowBackground">?android:colorBackground</item>
    <item name="colorPrimary">#2D3648</item>
    <item name="colorOnPrimary">#FFFFFF</item>
    <item name="colorOnSurface">#1A1A1A</item>
    <item name="android:textColorPrimary">#1A1A1A</item>
    <item name="android:textColorSecondary">#4B4B4B</item>
</style>
```

The native NFC prompts, "Hold still" and similar, inherit
`?android:textColorPrimary` from this theme. If your Flutter UI is always
light, force the native theme light as well in the `values-night` variant.
Otherwise the native text follows the system dark mode and can end up white on
a light background.

Arabic translations of the native strings ship with the SDK and follow the
language you pass to `startKyc`. Nothing to do on your side.

### Project repositories

```gradle title="android/settings.gradle"
pluginManagement {
    repositories {
        google()
        mavenCentral()
        gradlePluginPortal()
    }
}
```

## 4. iOS

### Podfile

Three source lines matter, and all three are required:

```ruby title="ios/Podfile" hl_lines="6 7 8"
platform :ios, '14.0'

ENV['COCOAPODS_DISABLE_STATS'] = 'true'

source 'https://github.com/innovatrics/innovatrics-podspecs'
source 'https://cdn.cocoapods.org/'
source 'https://msface.visualstudio.com/SDK/_git/AzureAIVisionFaceUI.podspec'

project 'Runner', {
  'Debug' => :debug,
  'Profile' => :release,
  'Release' => :release,
}

def flutter_root
  generated_xcode_build_settings_path = File.expand_path(
    File.join('..', 'Flutter', 'Generated.xcconfig'), __FILE__)
  unless File.exist?(generated_xcode_build_settings_path)
    raise "#{generated_xcode_build_settings_path} must exist. " \
          "Run flutter pub get first."
  end
  File.foreach(generated_xcode_build_settings_path) do |line|
    matches = line.match(/FLUTTER_ROOT\=(.*)/)
    return matches[1].strip if matches
  end
  raise "FLUTTER_ROOT not found in #{generated_xcode_build_settings_path}."
end

require File.expand_path(
  File.join('packages', 'flutter_tools', 'bin', 'podhelper'), flutter_root)
flutter_ios_podfile_setup

target 'Runner' do
  use_frameworks! :linkage => :static
  use_modular_headers!

  pod 'AzureAIVisionFaceUI'

  flutter_install_all_ios_pods File.dirname(File.realpath(__FILE__))
end

post_install do |installer|
  installer.pods_project.targets.each do |target|
    flutter_additional_ios_build_settings(target)
    target.build_configurations.each do |config|
      config.build_settings['GCC_PREPROCESSOR_DEFINITIONS'] ||= [
        '$(inherited)',
        'PERMISSION_CAMERA=1',
        'PERMISSION_MICROPHONE=1',
      ]
    end
  end
end
```

Both `use_frameworks! :linkage => :static` and `use_modular_headers!` are
required. Dropping either produces linker errors that look unrelated.

### Pod install credentials

The first `pod install` prompts for credentials against
`https://msface.visualstudio.com/SDK/_git/AzureAIVisionFaceUI.podspec`.

- **Username:** leave blank, or `elite`
- **Password:** your Azure SDK access token

### Info.plist

```xml title="ios/Runner/Info.plist"
<key>NSCameraUsageDescription</key>
<string>Camera access is required to scan your identity document and verify your face.</string>

<key>NSMicrophoneUsageDescription</key>
<string>Microphone access is required during video verification.</string>

<key>NSLocationWhenInUseUsageDescription</key>
<string>Your location is recorded as part of identity verification.</string>
```

Write these strings for your users, not for the reviewer. Apple rejects vague
ones, and so do customers.

## 5. Verify the setup

```bash
flutter clean
flutter pub get
cd ios && pod install && cd ..
flutter run
```

Then launch the flow on a physical device and reach the document step. The
emulator is fine for forms, useless for camera, NFC and liveness.

---

Next: [Launching the flow](usage.md).

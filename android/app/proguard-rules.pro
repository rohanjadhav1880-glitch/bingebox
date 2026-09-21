# Proguard / R8 Configuration for BingeBox Android

# MPVLib native JNI bindings preservation
-keep class com.bingebox.mediaplayer.mpv.** { *; }
-keep class is.xyz.mpv.** { *; }
-keepclassmembers class is.xyz.mpv.MPVLib {
    native <methods>;
}

# AndroidX and Compose rules
-keep class androidx.compose.** { *; }
-dontwarn androidx.compose.**

# Coil image loader
-keep class io.coilkt.** { *; }
-dontwarn io.coilkt.**

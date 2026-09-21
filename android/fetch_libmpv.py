import os
import sys

JNILIBS_DIR = os.path.join(os.path.dirname(__file__), "app", "src", "main", "jniLibs")
ARCHITECTURES = ["arm64-v8a", "armeabi-v7a", "x86_64"]

def setup_jni_directories():
    print("Creating jniLibs directory structure...")
    for arch in ARCHITECTURES:
        arch_dir = os.path.join(JNILIBS_DIR, arch)
        os.makedirs(arch_dir, exist_ok=True)
        print(f"   [OK] Created {arch_dir}")

def print_instructions():
    print("\n" + "="*70)
    print("BINGEBOX ANDROID NATIVE LIBMPV SETUP COMPLETE")
    print("="*70)
    print("Directories created at:")
    for arch in ARCHITECTURES:
        print(f"   * app/src/main/jniLibs/{arch}/")
    print("\nPre-built libmpv Android binaries destination:")
    print("   -> https://github.com/mpv-android/mpv-android/releases")
    print("="*70)

if __name__ == "__main__":
    setup_jni_directories()
    print_instructions()

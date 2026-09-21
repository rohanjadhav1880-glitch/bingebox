"""
BingeBox Engine Setup Utility
Detects and guides installation of libmpv and FFmpeg binaries for Windows desktop source development.
"""

import os
import sys
import shutil

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

ENGINE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "engine")

def check_engine():
    os.makedirs(ENGINE_DIR, exist_ok=True)
    
    has_mpv = any(
        os.path.exists(os.path.join(ENGINE_DIR, name))
        for name in ["libmpv-2.dll", "mpv-2.dll", "mpv-1.dll", "libmpv-1.dll"]
    ) or any(
        os.path.exists(os.path.join(os.path.dirname(os.path.abspath(__file__)), name))
        for name in ["libmpv-2.dll", "mpv-2.dll", "mpv-1.dll", "libmpv-1.dll"]
    )
    
    has_ffmpeg = os.path.exists(os.path.join(ENGINE_DIR, "ffmpeg.exe")) or shutil.which("ffmpeg") is not None
    
    return has_mpv, has_ffmpeg

def main():
    print("=" * 60)
    print("BingeBox Engine Dependencies Setup")
    print("=" * 60)
    
    has_mpv, has_ffmpeg = check_engine()
    
    if has_mpv and has_ffmpeg:
        print("\n[OK] All required engine binaries (libmpv + FFmpeg) are present!")
        print(f"Engine folder: {ENGINE_DIR}")
        print("\nYou can start BingeBox by running:\n  python main.py\n")
        return

    print("\n[!] Missing required engine binaries for running from source:\n")
    if not has_mpv:
        print("  [FAIL] libmpv DLL missing (libmpv-2.dll or mpv-1.dll)")
    else:
        print("  [OK]   libmpv DLL found")
        
    if not has_ffmpeg:
        print("  [WARN] ffmpeg.exe missing (needed for thumbnail generation)")
    else:
        print("  [OK]   ffmpeg.exe found")

    print("\n" + "-" * 60)
    print("How to Install libmpv and FFmpeg for Source Development:")
    print("-" * 60)
    print("1. Download libmpv for Windows (64-bit):")
    print("   * SourceForge: https://sourceforge.net/projects/mpv-player-windows/files/libmpv/")
    print("   * Or Shinchiro: https://github.com/shinchiro/mpv-winbuild-cmake/releases")
    print("   Extract 'mpv-2.dll' or 'libmpv-2.dll' and place it into:")
    print(f"   {ENGINE_DIR}\\")
    print("\n2. (Optional) Download FFmpeg for thumbnail extraction:")
    print("   * https://github.com/BtbN/FFmpeg-Builds/releases")
    print("   Extract 'ffmpeg.exe' and 'ffprobe.exe' and place into:")
    print(f"   {ENGINE_DIR}\\")
    print("-" * 60)
    print("\nAfter placing the files into 'engine/', re-run:")
    print("  python setup_engine.py")
    print("=" * 60)

if __name__ == "__main__":
    main()

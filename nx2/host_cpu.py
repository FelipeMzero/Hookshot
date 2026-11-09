"""The x86-64 level this PC's CPU runs (nx2/build.py's -march; issue 363). The game is built on the PC it runs on, so a
CPU without x86-64-v3's features (AVX2, FMA, BMI2, MOVBE) gets x86-64-v2, or the x86-64 baseline. RX_MARCH, read by
build.py, still chooses."""
import os


def host_march():
    want = ("avx2", "fma", "bmi2", "movbe")
    try:
        if os.name == "nt":
            import ctypes
            pf = ctypes.windll.kernel32.IsProcessorFeaturePresent
            # (PF_AVX2_INSTRUCTIONS_AVAILABLE 40; PF_SSE4_2_INSTRUCTIONS_AVAILABLE 38. Windows reports no FMA/BMI2 bit, but
            # every AVX2 CPU has them, as x86-64-v3 counts them together)
            if pf(40):
                ident = os.environ.get("PROCESSOR_IDENTIFIER", "")
                if "AuthenticAMD" in ident:
                    if "Family 23 " in ident:
                        try:
                            model = int(ident.split("Model ")[1].split()[0])
                            return "znver2" if model >= 49 else "znver1"
                        except Exception:
                            return "znver2"
                    if "Family 25 " in ident:
                        return "znver3"
                return "x86-64-v3"
            return "x86-64-v2" if pf(38) else "x86-64"
        cpuinfo = open("/proc/cpuinfo").read()
        flags = cpuinfo.split("flags", 1)[1].split(chr(10), 1)[0].split()
        if all(f in flags for f in want):
            if "AuthenticAMD" in cpuinfo:
                if "cpu family\t: 23" in cpuinfo:
                    return "znver2" if "clwb" in flags or "rdpid" in flags else "znver1"
                if "cpu family\t: 25" in cpuinfo:
                    return "znver3"
            return "x86-64-v3"
        return "x86-64-v2" if all(f in flags for f in ("sse4_2", "popcnt", "ssse3")) else "x86-64"
    except Exception:
        return "x86-64-v3"

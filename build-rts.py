# This script extends bb-runtimes to define the RP2040 targets

import sys
import os
import pathlib

# Add bb-runtimes to the search path so that we can include and extend it
sys.path.append(str(pathlib.Path(__file__).parent / "bb-runtimes"))

import arm.cortexm
import build_rts
from support import add_source_search_path


class RP2040(arm.cortexm.CortexM0P):
    @property
    def name(self):
        return "rp2040"

    @property
    def parent(self):
        # Don't refer to any parent since we need to override certain
        # sources from CortexMArch (e.g. replace src/s-bbsumu__generic.adb)
        return None

    @property
    def loaders(self):
        return ("ROM",)

    @property
    def system_ads(self):
        return {
            "light-tasking": "system-xi-armv6m-sfp.ads",
            "embedded": "system-xi-armv6m-full.ads",
        }

    def __init__(self):
        super(RP2040, self).__init__()

        # Common GNAT sources
        self.add_gnat_sources(
            "rp_src/boot2/generated/boot2-generic_03.S",
            "rp_src/boot2/generated/boot2-generic_qspi.S",
            "rp_src/boot2/generated/boot2-w25qxx.S",
            "rp_src/svd/i-rp2040.ads",
            "rp_src/svd/i-rp2040-clocks.ads",
            "rp_src/svd/i-rp2040-pll_sys.ads",
            "rp_src/svd/i-rp2040-psm.ads",
            "rp_src/svd/i-rp2040-resets.ads",
            "rp_src/svd/i-rp2040-rosc.ads",
            "rp_src/svd/i-rp2040-sio.ads",
            "rp_src/svd/i-rp2040-timer.ads",
            "rp_src/svd/i-rp2040-watchdog.ads",
            "rp_src/svd/i-rp2040-xosc.ads",
            "rp_src/s-bbmcpa.ads",
            "rp_src/start-rom-1.S",
            "rp_src/start-rom-2.S",
            "rp_src/s-bootro.ads",
            "rp_src/s-bootro.adb",
            "rp_src/setup_clocks.adb",
            "rp_src/s-bbbopa.ads",
        )

        # s-maxres__cortexm3.adb is also compatible with Cortex-M0+
        self.add_gnat_sources("src/s-macres__cortexm3.adb")

        # Common GNARL sources
        self.add_gnarl_sources("rp_src/s-bbpara.ads")

        self.add_gnarl_sources(
            "rp_src/a-intnam-1.ads",
            "rp_src/a-intnam-2.ads",
            "rp_src/s-bbbosu.adb",
            "rp_src/s-bbpara.ads",
            "rp_src/s-bbsumu-1.adb",
            "rp_src/s-bbsumu-2.adb",
            "rp_src/s-bcpcst.adb",
            "src/s-bbcppr__armv7m.adb",
            "src/s-bbcppr__old.ads",
            "src/s-bbcpsp__cortexm.ads",
            "src/s-bcpcst__armvXm.ads",
        )

def build_configs(target):
    if target == "rp2040":
        return RP2040()
    else:
        assert False, "unexpected target: %s" % target

def patch_bb_runtimes():
    """Patch some parts of bb-runtimes to use our own targets and data"""
    add_source_search_path(os.path.dirname(__file__))

    build_rts.build_configs = build_configs

if __name__ == "__main__":
    patch_bb_runtimes()
    build_rts.main()
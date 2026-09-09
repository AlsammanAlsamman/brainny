"""The brAInny ASCII banner — derived from assets/assci.txt (an
image-to-ASCII line-art render of assets/icon.png), cropped to content
and downsampled 2:1 vertically (nearest-neighbor row sampling, not
blending — blending smears thin strokes in line art). Shown on bare
`brainny` / `brainny --help`. Color is skipped for non-TTY output or when
NO_COLOR is set, per https://no-color.org.

Regenerating: if assets/assci.txt changes, _GLYPH below must be
regenerated from it by hand (crop to content bbox + pad, then take every
other row) — it is not read from assci.txt at runtime.
"""

from __future__ import annotations

import os
import sys

from brainny import __version__

RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"
GOLD = "\033[93m"
PINK = "\033[38;5;211m"

_GLYPH = """\

                                  &&&&&&            &&&&&&   &&&x
                        &&&&  &&&                   &&&&&            +&&&&
               &&&&&            &&&&    &&&      &&&        &&     &&&&    &&&
            &&&                     &&&&       &&          &&      ;&& &&     &&.
          &&        &&&;  &&&       &&&      &&        &&&     &&&&+    &X      &&
         &&        &&       &&&    &&&      &&       &&         &&   &;  &&&&       &&&&
        &&&&&&&&&&&&&&&        &&&&&&x      &&       &&               $&& &&            &&
    &&&                &&          &&+      &&&      &&+      &&&       &&&&  && : &&    &&
  &&&        &&&&&&  &&&&   &&&     &&             &&&   ;&&&&&  &&&&    &&&&   &       &&x
 &&       &&                :&&             &&&&&               && &&  &&&             &&&&&&
 &&       &&               &&&      &&&&&&&&         &&&         &  &&&       &&            &&
  &&        &&&&$      &&&&&&&&&                   &&x     :&&&&&&&         &&&&    :&&&&    &&
    &&&                  &&x                &&&&&&          &&&&X        ;&&   &&&:    &&&&  &&
       &&&&&           :&&         &&&&&&             &&&               &&&    &&&x&&&      &&
                &&&$   &&       &&$           &&&&;                    &&                &&&
                       &&&             &&&&&&        &&&&&&&$        &&  :&&&&&&&&&&&&&&&
                         &&&                   &&&&& &&&        &&&&     &&&&      &&
                             &&&&&&&&&&&&&&&&&&         &&  &&&&  &&&&&&&  &&&   $&&
                                               &&&       &&&                  X&&&
                                                    &&&  &&      &&&&&&&&&&&&
                                                       &&&&    &&
                                                         &&&    &&
                                                          .&&    &&
                                                           &&                                  \
"""


def _color_enabled() -> bool:
    if os.environ.get("NO_COLOR") is not None:
        return False
    return sys.stdout.isatty()


def render_banner() -> str:
    if _color_enabled():
        glyph = f"{PINK}{_GLYPH}{RESET}"
        wordmark = f"   {BOLD}br{GOLD}AI{RESET}{BOLD}nny{RESET}  v{__version__}"
        tagline = f"   {DIM}remembers how you work with AI{RESET}"
    else:
        glyph = _GLYPH
        wordmark = f"   brAInny  v{__version__}"
        tagline = "   remembers how you work with AI"

    return glyph + "\n\n" + wordmark + "\n" + tagline + "\n"

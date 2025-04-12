from __future__ import annotations

import construct


# Hex for some reason doesn't support compilation for building, despite being trivial to do
# So let's hack it in.
def _hex_emitbuild(self, code):
    return self.subcon._compilebuild(code)


construct.Hex._emitbuild = _hex_emitbuild

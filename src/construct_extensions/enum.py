from __future__ import annotations

import enum
import typing
from typing import Generic, TypeVar

import construct

EnumT = TypeVar("EnumT", bound=enum.Enum)


class StrictEnum(construct.Adapter, Generic[EnumT]):
    def __init__(self, enum_class: type[EnumT], subcon: construct.Construct):
        super().__init__(construct.Enum(subcon, enum_class))
        self.enum_class = enum_class

    def _decode(self, obj: str, context: construct.Container, path: str) -> EnumT:
        return typing.cast("EnumT", self.enum_class[obj])

    def _encode(self, obj: EnumT, context: construct.Container, path: str) -> str:
        return obj.name

    def _emitbuild(self, code: construct.CodeGen):
        i = code.allocateId()

        mapping = ", ".join(f"{repr(enum_entry.name)}: {enum_entry.value}" for enum_entry in self.enum_class)

        code.append(f"""
        _enum_name_to_value_{i} = {{{mapping}}}
        def _encode_enum_{i}(obj, io, this):
            # {self.name}
            try:
                obj = obj.value
            except AttributeError:
                obj = _enum_name_to_value_{i}.get(obj, obj)
            return {self.subcon._compilebuild(code)}
        """)
        return f"_encode_enum_{i}(obj, io, this)"


EnumAdapter = StrictEnum  # alias for compatibility


def StrictEnumL(enum_class: type[EnumT]) -> StrictEnum[EnumT]:
    """StrictEnum for Int32ul"""
    return StrictEnum(enum_class, construct.Int32ul)


def StrictEnumB(enum_class: type[EnumT]) -> StrictEnum[EnumT]:
    """StrictEnum for Int32ub"""
    return StrictEnum(enum_class, construct.Int32ub)


def BitMaskEnum(enum_type: type[enum.IntEnum]):
    flags = {}
    for enumentry in enum_type:
        flags[enumentry.name] = 2**enumentry.value
    return construct.FlagsEnum(construct.Int32ul, **flags)

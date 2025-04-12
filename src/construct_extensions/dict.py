from __future__ import annotations

import construct
from construct import Construct, Container


class DictConstruct(construct.Construct):
    def __init__(
        self,
        key_type: Construct,
        value_type: Construct,
        count_type: Construct = construct.Int32ub,
    ):
        super().__init__()
        self.key_type = key_type
        self.value_type = value_type
        self.count_type = count_type

        assert not self.key_type.flagbuildnone

    def _parse(self, stream, context, path) -> Container:
        field_count = self.count_type._parsereport(stream, context, path)

        result = Container()

        for i in range(field_count):
            field_path = f"{path}.field_{i}"
            key = self.key_type._parsereport(stream, context, field_path)
            value = self.value_type._parsereport(stream, context, field_path)
            result[key] = value

        return result

    def _build(self, obj: Container, stream, context, path):
        self.count_type._build(len(obj), stream, context, path)

        for i, (key, value) in enumerate(obj.items()):
            field_path = f"{path}.field_{i}"
            self.key_type._build(key, stream, context, field_path)
            self.value_type._build(value, stream, context, field_path)

    def _emitparse(self, code):
        return (
            f"Container(({self.key_type._compileparse(code)}, {self.value_type._compileparse(code)}) "
            f"for i in range({self.count_type._compileparse(code)}))"
        )

    def _emitbuild(self, code):
        fname = f"build_dict_{code.allocateId()}"
        block = f"""
            def {fname}(key, value, io, this):
                obj = key
                {self.key_type._compilebuild(code)}

                obj = value
                {self.value_type._compilebuild(code)}
        """
        code.append(block)
        return (
            f"(reuse(len(obj), "
            f"lambda obj: {self.count_type._compilebuild(code)}), "
            f"list({fname}(key, value, io, this) for key, value in obj.items()), obj)[2]"
        )

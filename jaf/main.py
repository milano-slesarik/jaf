import json
import os
import typing
from io import IOBase

from jaf.encoders import JAFJSONEncoder


class JsonArrayFileWriterNotOpenError(Exception):
    pass


class JsonArrayFileWriter:
    MODE__APPEND_OR_CREATE = 'ac'
    MODE__REWRITE_OR_CREATE = 'rc'

    def __init__(self, filepath: str, mode=MODE__REWRITE_OR_CREATE, indent: typing.Optional[int] = None,
                 json_encoder=JAFJSONEncoder):
        self.filepath: str = filepath
        self.mode = mode
        self.indent: int = indent
        self.lines: int = 0
        self.json_encoder = json_encoder
        self.file: typing.Optional[IOBase] = None

    def __enter__(self) -> 'JsonArrayFileWriter':
        self.open()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.close()

    def open(self) -> None:
        if self.mode == self.MODE__REWRITE_OR_CREATE:
            self.file = open(self.filepath, 'w')
            self.file.write('[')
        elif self.mode == self.MODE__APPEND_OR_CREATE:
            if os.path.exists(self.filepath):
                with open(self.filepath) as f:
                    jsn = json.load(f)  # loads whole JSON into the memory
                os.rename(self.filepath, self.filepath + '.bak')
            else:
                jsn = []

            self.file = open(self.filepath, 'w')
            self.file.write('[')
            for entry in jsn:
                self.write(entry)

        elif self.mode == self.MODE__APPEND:
            raise NotImplementedError
        else:
            raise NotImplementedError(f"Unknown write mode \"{self.mode}\"")

    def write(self, dct: dict) -> None:
        if getattr(self, 'file', None) is None:
            raise JsonArrayFileWriterNotOpenError(
                "JsonArrayFileWriter needs to be opened by calling `.open()` or used within a context manager `with JsonArrayFileWriter(<FILEPATH>,**kwargs) as writer:`")
        jsn = json.dumps(dct, indent=self.indent, cls=self.json_encoder)

        if self.lines:
            self.file.write(f',')
        self.write_newline()
        self.file.write(jsn)
        self.lines += 1

    def write_dict(self, dct: dict) -> None:
        self.write(dct)

    def write_newline(self):
        self.file.write(os.linesep)

    def close(self) -> None:
        self.file.write('\n')
        self.file.write(']')
        self.file.close()


with JsonArrayFileWriter('output.json', mode=JsonArrayFileWriter.MODE__APPEND_OR_CREATE, indent=4) as j:
    d = {1: 2, 2: 3, 3: 4, 4: 6}
    for i in range(1000000):
        j.write(d)

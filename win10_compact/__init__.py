import ctypes
from ctypes.wintypes import BOOL, DWORD, HANDLE, LPDWORD, LPVOID, ULONG
from ctypes import windll

WOF_CURRENT_VERSION = 1
WOF_PROVIDER_FILE = 2

FSCTL_SET_EXTERNAL_BACKING = 0x9030C
FSCTL_GET_EXTERNAL_BACKING = 0x90310
FSCTL_DELETE_EXTERNAL_BACKING = 0x90314

FILE_PROVIDER_CURRENT_VERSION = 1

FILE_PROVIDER_COMPRESSION_XPRESS4K = 0
FILE_PROVIDER_COMPRESSION_LZX = 1
FILE_PROVIDER_COMPRESSION_XPRESS8K = 2
FILE_PROVIDER_COMPRESSION_XPRESS16K = 3


class WOF_EXTERNAL_INFO(ctypes.Structure):
    _fields_ = (
        ("Version", ULONG),
        ("Provider", ULONG),
    )


class FILE_PROVIDER_EXTERNAL_INFO_V1(ctypes.Structure):
    _fields_ = (
        ("Version", ULONG),
        ("Algorithm", ULONG),
        ("Flags", ULONG),
    )

DeviceIoControl = windll.kernel32.DeviceIoControl
DeviceIoControl.argtypes = (
    HANDLE,
    DWORD,
    LPVOID,
    DWORD,
    LPVOID,
    DWORD,
    LPDWORD,
    LPVOID,
)
DeviceIoControl.restype = BOOL

# End MS decls

from enum import IntEnum
from typing import Literal, Union
import os

class wof_file_info(ctypes.Structure):
    """Concatenated WOF_EXTERNAL_INFO and FILE_PROVIDER_EXTERNAL_INFO_V1
    """
    _fields_ = (
        ("wof", WOF_EXTERNAL_INFO),
        ("file", FILE_PROVIDER_EXTERNAL_INFO_V1),
    )

class FileProviderCompression(IntEnum):
    XPRESS4K = FILE_PROVIDER_COMPRESSION_XPRESS4K
    LZX = FILE_PROVIDER_COMPRESSION_LZX
    XPRESS8K = FILE_PROVIDER_COMPRESSION_XPRESS8K
    XPRESS16K = FILE_PROVIDER_COMPRESSION_XPRESS16K

def compress(
    file: Union[os.PathLike, int], 
    algorithm: Literal[
        FILE_PROVIDER_COMPRESSION_XPRESS4K,
        FILE_PROVIDER_COMPRESSION_LZX,
        FILE_PROVIDER_COMPRESSION_XPRESS8K,
        FILE_PROVIDER_COMPRESSION_XPRESS16K,
    ]) -> None:
        if not isinstance(file, int):
            with open(file, "r+b") as inner:
                return compress(inner.fileno(), algorithm)

        from msvcrt import get_osfhandle

        fi = wof_file_info()
        fi.wof.Version = WOF_CURRENT_VERSION
        fi.wof.Provider = WOF_PROVIDER_FILE
        fi.file.Version = FILE_PROVIDER_CURRENT_VERSION
        fi.file.Algorithm = algorithm
        fi.file.Flags = 0

        if not DeviceIoControl(get_osfhandle(file), FSCTL_SET_EXTERNAL_BACKING, ctypes.byref(fi), ctypes.sizeof(fi), 0, 0, 0, 0):
            raise ctypes.WinError()


__all__ = []

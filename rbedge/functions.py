import ctypes

from pyrubicon.objc import ObjCInstance  # api
from pyrubicon.objc.runtime import Foundation, Class


def NSStringFromClass(cls: Class) -> ObjCInstance:
  _NSStringFromClass = Foundation.NSStringFromClass
  _NSStringFromClass.restype = ctypes.c_void_p
  _NSStringFromClass.argtypes = [Class]
  return ObjCInstance(_NSStringFromClass(cls))


import ctypes

from pyrubicon.objc import (
  Block,
  ObjCClass,
  ObjCInstance,
  objc_method,
)  # api
from pyrubicon.objc import (
  SEL,
  objc_id,
  send_super,
)  # runtime
# todo: utils ###############################################
from pyrubicon.objc.runtime import Class, Foundation
# todo: lifeCycle ###########################################
import asyncio
import logging
from pyrubicon.objc.eventloop import RubiconEventLoop
# todo: exception ###########################################
import sys
import os
# todo: mainThread ##########################################
import functools
from pyrubicon.objc import objc_block  # runtime
from pyrubicon.objc.runtime import libobjc
from rbedge import pdbr

ObjCClass.auto_rename = True


#############################################################
# --- utils
def NSStringFromClass(cls: Class) -> ObjCInstance:
  _NSStringFromClass = Foundation.NSStringFromClass
  _NSStringFromClass.restype = ctypes.c_void_p
  _NSStringFromClass.argtypes = [Class]
  return ObjCInstance(_NSStringFromClass(cls))


#############################################################
# --- exception
#############################################################
# todo: from objc_util.py of Pythonista3
ExceptionHandlerFuncType = ctypes.CFUNCTYPE(None, ctypes.c_void_p)


def NSSetUncaughtExceptionHandler(_exc: ExceptionHandlerFuncType) -> None:
  _NSSetUncaughtExceptionHandler = Foundation.NSSetUncaughtExceptionHandler
  _NSSetUncaughtExceptionHandler.restype = None
  _NSSetUncaughtExceptionHandler.argtypes = [
    ExceptionHandlerFuncType,
  ]
  _NSSetUncaughtExceptionHandler(_exc)


def _objc_exception_handler(_exc):
  exc = ObjCInstance(_exc)
  _path_str = '~/Documents/_rubicon_objc_exception.txt'
  with open(os.path.expanduser(_path_str), 'w') as f:
    from datetime import datetime
    f.write(
      'The app was terminated due to an Objective-C exception. Details below:\n\n%s\n%s\n'
      % (datetime.now(), exc))


_handler = ExceptionHandlerFuncType(_objc_exception_handler)
NSSetUncaughtExceptionHandler(_handler)

#############################################################
# --- lifeCycle
#############################################################
#logging.basicConfig(level=logging.DEBUG)
loop = RubiconEventLoop()
asyncio.set_event_loop(loop)
#loop.set_debug(True)

#############################################################
# --- mainThread
#############################################################
NSThread = ObjCClass('NSThread')


class struct_dispatch_queue_s(ctypes.Structure):
  pass  # No _fields_, because this is an opaque structure.


_dispatch_main_q = struct_dispatch_queue_s.in_dll(libobjc, '_dispatch_main_q')


def dispatch_get_main_queue():
  return ObjCInstance(ctypes.cast(ctypes.byref(_dispatch_main_q), objc_id))


libobjc.dispatch_sync.restype = None
libobjc.dispatch_sync.argtypes = [
  objc_id,
  objc_block,
]

libobjc.dispatch_async.restype = None
libobjc.dispatch_async.argtypes = [
  objc_id,
  objc_block,
]


def onMainThread(func):

  @functools.wraps(func)
  def wrapper(*args, **kwargs):
    if NSThread.isMainThread:
      func(*args, **kwargs)
    block = Block(functools.partial(func, *args, **kwargs), None)
    libobjc.dispatch_async(dispatch_get_main_queue(), block)

  return wrapper


'''
def onMainThread(func=None, *, sync=True):
  if func is None:
    return functools.partial(onMainThread, sync=sync)

  @functools.wraps(func)
  def wrapper(*args, **kwargs):
    if NSThread.isMainThread:
      return func(*args, **kwargs)

    queue = dispatch_get_main_queue()
    results = []  # 戻り値キャプチャ用

    def task():
      res = func(*args, **kwargs)
      results.append(res)

    block = Block(task, None)

    if sync:
      libobjc.dispatch_sync(queue, block)
      return results[0] if results else None
    else:
      libobjc.dispatch_async(queue, block)
      return None  # asyncは戻り値なし

  return wrapper
'''


#############################################################
# --- UINavigationController
#############################################################
UINavigationController = ObjCClass('UINavigationController')
UINavigationBarAppearance = ObjCClass('UINavigationBarAppearance')
UIBarButtonItem = ObjCClass('UIBarButtonItem')


class RootNavigationController(UINavigationController):

  @objc_method
  def dealloc(self) -> None:
    # xxx: 呼ばない-> `send_super(__class__, self, 'dealloc')`
    print(f'- {NSStringFromClass(__class__)}: dealloc')
    # >>> (5) <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
    loop.stop()
    print('--- stop')

  @objc_method
  def loadView(self) -> None:
    send_super(
      __class__,
      self,
      'loadView',
      restype=None,
    )
    print(f'{NSStringFromClass(__class__)}: loadView')
    navigationBarAppearance = UINavigationBarAppearance.new()
    navigationBarAppearance.configureWithDefaultBackground()
    #navigationBarAppearance.configureWithOpaqueBackground()
    #navigationBarAppearance.configureWithTransparentBackground()
    '''

    navigationBar = self.navigationBar
    navigationBar.standardAppearance = navigationBarAppearance
    navigationBar.scrollEdgeAppearance = navigationBarAppearance
    navigationBar.compactAppearance = navigationBarAppearance
    navigationBar.compactScrollEdgeAppearance = navigationBarAppearance
    '''
    self.navigationBar.standardAppearance = navigationBarAppearance
    self.navigationBar.scrollEdgeAppearance = navigationBarAppearance
    self.navigationBar.compactAppearance = navigationBarAppearance
    self.navigationBar.compactScrollEdgeAppearance = navigationBarAppearance

  @objc_method
  def viewDidLoad(self) -> None:
    send_super(
      __class__,
      self,
      'viewDidLoad',
      restype=None,
    )
    print(f'{NSStringFromClass(__class__)}: viewDidLoad')
    self.delegate = self

  @objc_method
  def viewWillAppear_(self, animated: bool) -> None:
    send_super(
      __class__,
      self,
      'viewWillAppear:',
      animated,
      restype=None,
      argtypes=[
        ctypes.c_bool,
      ],
    )
    print(f'{NSStringFromClass(__class__)}: viewWillAppear_')

  @objc_method
  def viewDidAppear_(self, animated: bool) -> None:
    send_super(
      __class__,
      self,
      'viewDidAppear:',
      animated,
      restype=None,
      argtypes=[
        ctypes.c_bool,
      ],
    )
    print(f'{NSStringFromClass(__class__)}: viewDidAppear_')
    print('↓ ---')

  @objc_method
  def viewWillDisappear_(self, animated: bool) -> None:
    print('↑ ---')
    send_super(
      __class__,
      self,
      'viewWillDisappear:',
      animated,
      restype=None,
      argtypes=[
        ctypes.c_bool,
      ],
    )
    print(f'{NSStringFromClass(__class__)}: viewWillDisappear_')

  @objc_method
  def viewDidDisappear_(self, animated: bool) -> None:
    send_super(
      __class__,
      self,
      'viewDidDisappear:',
      animated,
      restype=None,
      argtypes=[
        ctypes.c_bool,
      ],
    )
    print(f'{NSStringFromClass(__class__)}: viewDidDisappear_')

  @objc_method
  def didReceiveMemoryWarning(self) -> None:
    send_super(
      __class__,
      self,
      'didReceiveMemoryWarning',
      restype=None,
    )
    print(f'{NSStringFromClass(__class__)}: didReceiveMemoryWarning')

  @objc_method
  def closeButtonTapped_(self, sender) -> None:
    print(f'{NSStringFromClass(__class__)}: doneButtonTapped:')
    self.dismissViewControllerAnimated_completion_(True, None)

  @objc_method
  def navigationController_willShowViewController_animated_(
    self,
    navigationController,
    viewController,
    animated: bool,
  ) -> None:
    closeButtonItem = UIBarButtonItem.alloc().initWithBarButtonSystemItem(
      24,
      target=navigationController,
      action=SEL('closeButtonTapped:'),
    )

    visibleViewController = navigationController.visibleViewController
    navigationItem = visibleViewController.navigationItem
    navigationItem.rightBarButtonItem = closeButtonItem


#############################################################
# --- UIViewController
#############################################################
UIViewController = ObjCClass('UIViewController')
UIColor = ObjCClass('UIColor')

class MainViewController(UIViewController):

  @objc_method
  def dealloc(self) -> None:
    # xxx: 呼ばない-> `send_super(__class__, self, 'dealloc')`
    #print(f'\t - {NSStringFromClass(__class__)}: dealloc')
    pass

  @objc_method
  def loadView(self) -> None:
    send_super(
      __class__,
      self,
      'loadView',
      restype=None,
    )
    print(f'\t{NSStringFromClass(__class__)}: loadView')

  @objc_method
  def viewDidLoad(self) -> None:
    send_super(
      __class__,
      self,
      'viewDidLoad',
      restype=None,
    )
    print(f'\t{NSStringFromClass(__class__)}: viewDidLoad')
    self.navigationItem.title = NSStringFromClass(__class__)
    self.view.backgroundColor = UIColor.secondarySystemBackgroundColor()

  @objc_method
  def viewWillAppear_(self, animated: bool) -> None:
    send_super(
      __class__,
      self,
      'viewWillAppear:',
      animated,
      restype=None,
      argtypes=[
        ctypes.c_bool,
      ],
    )
    print(f'\t{NSStringFromClass(__class__)}: viewWillAppear_')

  @objc_method
  def viewDidAppear_(self, animated: bool) -> None:
    send_super(
      __class__,
      self,
      'viewDidAppear:',
      animated,
      restype=None,
      argtypes=[
        ctypes.c_bool,
      ],
    )
    print(f'\t{NSStringFromClass(__class__)}: viewDidAppear_')
    print('\t↓ ---')

  @objc_method
  def viewWillDisappear_(self, animated: bool) -> None:
    print('\t↑ ---')
    send_super(
      __class__,
      self,
      'viewWillDisappear:',
      animated,
      restype=None,
      argtypes=[
        ctypes.c_bool,
      ],
    )
    print(f'\t{NSStringFromClass(__class__)}: viewWillDisappear_')

  @objc_method
  def viewDidDisappear_(self, animated: bool) -> None:
    send_super(
      __class__,
      self,
      'viewDidDisappear:',
      animated,
      restype=None,
      argtypes=[
        ctypes.c_bool,
      ],
    )
    print(f'\t{NSStringFromClass(__class__)}: viewDidDisappear_')

  @objc_method
  def didReceiveMemoryWarning(self) -> None:
    send_super(
      __class__,
      self,
      'didReceiveMemoryWarning',
      restype=None,
    )
    print(f'\t{NSStringFromClass(__class__)}: didReceiveMemoryWarning')


#############################################################
# --- app present
#############################################################
UIApplication = ObjCClass('UIApplication')
'''
class App:

  # >>> (1) <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
  sharedApplication = UIApplication.sharedApplication
  __objectEnumerator = sharedApplication.connectedScenes.objectEnumerator()
  while (__windowScene := __objectEnumerator.nextObject()):
    if __windowScene.activationState == 0:
      break
  rootViewController = __windowScene.keyWindow.rootViewController

  def __init__(self, viewController, modalPresentationStyle=1):
    self.viewController = viewController
    self.modalPresentationStyle = modalPresentationStyle

  def present(self):

    # >>> (2) <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
    @onMainThread
    def present_viewController(viewController: UIViewController, style: int):

      presentViewController = RootNavigationController.alloc(
      ).initWithRootViewController_(viewController)

      presentViewController.setModalPresentationStyle_(style)

      self.rootViewController.presentViewController_animated_completion_(
        presentViewController, True, None)

    # >>> (3) <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
    present_viewController(self.viewController, self.modalPresentationStyle)
    self.main_loop()

  def main_loop(self):
    # >>> (4) <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
    loop.run_forever()
    loop.close()
'''


class App:

  def __init__(
    self,
    viewController: UIViewController,
    modalPresentationStyle=1,
  ):
    self.viewController = viewController
    self.modalPresentationStyle = modalPresentationStyle

    self.set_rootViewController()

  def set_rootViewController(self) -> None:
    # >>> (1) <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
    sharedApplication = UIApplication.sharedApplication
    objectEnumerator = sharedApplication.connectedScenes.objectEnumerator()

    windowScene = next(_scene
                       for _scene in iter(objectEnumerator.nextObject, None)
                       if _scene.activationState == 0)

    rootViewController = windowScene.keyWindow.rootViewController
    self.rootViewController = rootViewController

  def present(
    self,
    NavigationController=RootNavigationController,
  ) -> None:

    # >>> (2) <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
    @onMainThread#(sync=False)
    def present_viewController(
      viewController: UIViewController,
      style: int,
    ) -> None:

      presentViewController = NavigationController.alloc(
      ).initWithRootViewController_(viewController)

      presentViewController.setModalPresentationStyle_(style)

      self.rootViewController.presentViewController_animated_completion_(
        presentViewController,
        True,
        None,
      )

    # >>> (3) <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
    present_viewController(
      self.viewController,
      self.modalPresentationStyle,
    )
    self.main_loop()

  def main_loop(self) -> None:
    # >>> (4) <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
    try:
      print(f'try')
      loop.run_forever()
    except Exception as e:
      print(f'stop: {e}')
      loop.stop()
    finally:
      print(f'finally')
      loop.close()
      


if __name__ == '__main__':
  print('--- run ---')
  main_vc = MainViewController.new()
  presentation_style = 1

  app = App(main_vc, presentation_style)
  app.present()
  print('--- end ---')
  # >>> (6) <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
  del loop


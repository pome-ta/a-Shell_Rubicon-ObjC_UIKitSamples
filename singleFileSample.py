import ctypes

from pyrubicon.objc import (
  Block,
  ObjCClass,
  ObjCInstance,
  ObjCProtocol,
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
from pyrubicon.objc.eventloop import RubiconEventLoop, iOSLifecycle, CFLifecycle
# todo: exception ###########################################
import sys
import os
# todo: mainThread ##########################################
import functools
from pyrubicon.objc import objc_block  # runtime
from pyrubicon.objc.runtime import load_library, libobjc, autoreleasepool
from rbedge import pdbr

ObjCClass.auto_rename = True

UIApplication = ObjCClass("UIApplication")
UIViewController = ObjCClass("UIViewController")
UIColor = ObjCClass("UIColor")
NSObject = ObjCClass("NSObject")
UINavigationController = ObjCClass('UINavigationController')
UINavigationControllerDelegate = ObjCProtocol('UINavigationControllerDelegate')
UIBarButtonItem = ObjCClass('UIBarButtonItem')


def NSStringFromClass(cls: Class) -> ObjCInstance:
  try:
    _func = NSStringFromClass._cfunc
  except AttributeError:
    _func = Foundation.NSStringFromClass
    _func.restype = objc_id
    _func.argtypes = [Class]
    NSStringFromClass._cfunc = _func

  return ObjCInstance(_func(cls))


loop = RubiconEventLoop()

#############################################################
# --- mainThread
#############################################################
libSystem = load_library('System')
NSThread = ObjCClass('NSThread')
'''
print(libobjc)
print(libSystem)
print(libobjc == libSystem)
'''


class struct_dispatch_queue_s(ctypes.Structure):
  pass  # No _fields_, because this is an opaque structure.


#_dispatch_main_q = struct_dispatch_queue_s.in_dll(libobjc, '_dispatch_main_q')
_dispatch_main_q = struct_dispatch_queue_s.in_dll(libSystem,
                                                  '_dispatch_main_q')


def dispatch_get_main_queue():
  return ObjCInstance(ctypes.cast(ctypes.byref(_dispatch_main_q), objc_id))


def dispatch_async(queue, block_obj: objc_block):
  try:
    _func = dispatch_async._cfunc
  except AttributeError:
    #_func = libobjc.dispatch_async
    _func = libSystem.dispatch_async
    _func.restype = None
    _func.argtypes = [
      objc_id,
      objc_block,
    ]
    dispatch_async._cfunc = _func

  _func(queue, block_obj)


def onMainThread(func):

  @functools.wraps(func)
  def wrapper(*args, **kwargs):
    if NSThread.isMainThread:
      #print('NSThread')
      func(*args, **kwargs)
    #print('block')
    block = Block(functools.partial(func, *args, **kwargs), None)
    dispatch_async(dispatch_get_main_queue(), block)

  return wrapper


'''
class NavigationController(UINavigationController,
                           protocols=[UINavigationControllerDelegate]):
'''


class NavigationController(UINavigationController):

  @objc_method
  def dealloc(self) -> None:
    # xxx: 呼ばない-> `send_super(__class__, self, 'dealloc')`
    #print(f'\t - {NSStringFromClass(__class__)}: dealloc')
    pass

  @objc_method
  def viewDidLoad(self) -> None:
    send_super(
      __class__,
      self,
      'viewDidLoad',
      restype=None,
    )
    print(f'\t{NSStringFromClass(__class__)}: viewDidLoad')
    self.delegate = self

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
    if self.isBeingDismissed:
      print('s: stop')
      loop.stop()
      print('e: stop')

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


class MyViewController(UIViewController):

  @objc_method
  def dealloc(self) -> None:
    # xxx: 呼ばない-> `send_super(__class__, self, 'dealloc')`
    print(f'\t - {NSStringFromClass(__class__)}: dealloc')
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
    '''
    if self.isBeingDismissed:
      print('s: stop')
      loop.stop()
      print('e: stop')
    '''

  @objc_method
  def didReceiveMemoryWarning(self) -> None:
    send_super(
      __class__,
      self,
      'didReceiveMemoryWarning',
      restype=None,
    )
    print(f'\t{NSStringFromClass(__class__)}: didReceiveMemoryWarning')


class ModalPresenter(NSObject):

  @objc_method
  def presentVC_(self, vc) -> None:

    sharedApplication = UIApplication.sharedApplication
    objectEnumerator = sharedApplication.connectedScenes.objectEnumerator()

    windowScene = next(_scene
                       for _scene in iter(objectEnumerator.nextObject, None)
                       if _scene.activationState == 0)

    rootViewController = windowScene.keyWindow.rootViewController

    presentViewController = NavigationController.alloc(
    ).initWithRootViewController_(vc)

    #vc.modalPresentationStyle = 1
    presentViewController.modalPresentationStyle = 1

    rootViewController.presentViewController(
      presentViewController,
      animated=True,
      completion=None,
    )
    '''

    app = UIApplication.sharedApplication
    rootVC = app.keyWindow.rootViewController
    while childVC := rootVC.presentedViewController:
      rootVC = childVC
    #mainVC = MyViewController.new().autorelease()

    rootVC.presentViewController_animated_completion_(vc, True, None)
    '''


_keep_alive = []


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

  def present(self) -> None:

    # >>> (2) <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
    @onMainThread  #(sync=False)
    def present_viewController(
      viewController: UIViewController,
      style: int,
    ) -> None:

      presentViewController = NavigationController.alloc(
        #presentViewController = UINavigationController.alloc(
      ).initWithRootViewController_(viewController)  #.autorelease()
      _keep_alive.append(presentViewController)

      #pdbr.state(UINavigationController)

      #viewController.setModalPresentationStyle_(style)
      presentViewController.setModalPresentationStyle_(style)

      self.rootViewController.presentViewController_animated_completion_(
        presentViewController,
        True,
        None,
      )

    # >>> (3) <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
    #with autoreleasepool():
    present_viewController(
      self.viewController,
      self.modalPresentationStyle,
    )
    loop.run_forever()
    #loop.run_forever_cooperatively(lifecycle=iOSLifecycle())
    #self.main_loop()
    #loop.run_forever_cooperatively(lifecycle=iOSLifecycle())


#presentViewController = NavigationController.alloc().initWithRootViewController_(viewController)
'''
if __name__ == '__main__':
  print('--- run ---')
  main_vc = MainViewController.new()
  presentation_style = 0

  app = App(main_vc, presentation_style)
  app.present()
  print('--- end ---')
  # >>> (6) <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
  #loop.close()
'''
'''
if __name__ == '__main__':
  print('--- run ---')
  my_vc = MyViewController.new()
  presenter = ModalPresenter.alloc().init()
  presenter.performSelectorOnMainThread(
    SEL("presentVC:"),
    withObject=my_vc,
    waitUntilDone=False,
  )
  loop.run_forever()
'''
if __name__ == '__main__':
  print('--- run ---')

  main_vc = MyViewController.new()
  presentation_style = 1
  app = App(main_vc, presentation_style)
  app.present()


from pyrubicon.objc import (
  NSObject,
  ObjCClass,
  ObjCInstance,
  objc_method,
  objc_property,
)  # api
from pyrubicon.objc import (
  objc_id,
  send_super,
)  # runtime

from .lifeCycle import loop
from .enumerations import (
  UISceneActivationState,
  UIModalPresentationStyle,
)
from .objcMainThread import onMainThread
from .rootNavigationController import RootNavigationController
from .functions import NSStringFromClass

UIApplication = ObjCClass('UIApplication')


class App(NSObject):

  viewController = objc_property(ObjCInstance)
  navigationClass = objc_property(ObjCClass)

  @objc_method
  def dealloc(self) -> None:
    # xxx: 呼ばない-> `send_super(__class__, self, 'dealloc')`
    #print(f'- {NSStringFromClass(__class__)}: dealloc')
    pass

  @objc_method
  def configureWithViewController_navigationClass_(
    self,
    viewController: ObjCInstance,
    navigationClass: ObjCClass,
  ) -> ObjCInstance:
    self = ObjCInstance(
      send_super(__class__, self, 'init', restype=objc_id, argtypes=[]))
    if self is None:
      return None

    self.viewController = viewController
    self.navigationClass = navigationClass

    return self

  @objc_method
  def initWithViewController_(
    self,
    viewController: ObjCInstance,
  ) -> ObjCInstance:
    return self.configureWithViewController_navigationClass_(
      viewController,
      RootNavigationController,
    )

  @objc_method
  def initWithViewController_navigationClass_(
    self,
    viewController: ObjCInstance,
    navigationClass: ObjCClass,
  ) -> ObjCInstance:
    return self.configureWithViewController_navigationClass_(
      viewController,
      navigationClass,
    )

  @objc_method
  def presentWithStyle_(self, style: int) -> None:

    @onMainThread
    def _main_thread_present() -> None:
      sharedApplication = UIApplication.sharedApplication
      objectEnumerator = sharedApplication.connectedScenes.objectEnumerator()
      windowScene = next(_scene
                         for _scene in iter(objectEnumerator.nextObject, None)
                         if _scene.activationState == 0)
      keyWindowViewController = windowScene.keyWindow.rootViewController

      presentController = self.navigationClass.alloc(
      ).initWithRootViewController_(self.viewController)
      presentController.setModalPresentationStyle_(style)

      keyWindowViewController.presentViewController_animated_completion_(
        presentController,
        True,
        None,
      )

    _main_thread_present()

    #print('s: --- main_loop ---')
    loop.run_forever()


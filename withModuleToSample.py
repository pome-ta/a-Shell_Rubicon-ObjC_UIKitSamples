import ctypes

from pyrubicon.objc import ObjCClass ,objc_method # api
from pyrubicon.objc import send_super # runtime

from rbedge.functions import NSStringFromClass


UIViewController = ObjCClass('UIViewController')


class MainViewController(UIViewController):

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

    @objc_method
    def didReceiveMemoryWarning(self) -> None:
        send_super(
          __class__,
          self,
          'didReceiveMemoryWarning',
          restype=None,
        )
        print(f'\t{NSStringFromClass(__class__)}: didReceiveMemoryWarning')



if __name__ == '__main__':
    from rbedge.app import App
    from rbedge.enumerations import UIModalPresentationStyle

    print('--- run ---')
    main_vc = MainViewController.new()

    #presentation_style = UIModalPresentationStyle.fullScreen
    presentation_style = UIModalPresentationStyle.pageSheet

    app = App.alloc().initWithViewController_(main_vc)
    app.presentWithStyle_(presentation_style)
    print('--- end ---')
    
    try:
      import gc
      gc.collect()
    except Exception as e:
      print('--- collect: error')
      print(f'{e}')
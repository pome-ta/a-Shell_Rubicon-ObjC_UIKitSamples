from pyrubicon.objc import (
  ObjCClass,
  ObjCInstance,
  objc_method,
)  # api
from pyrubicon.objc import send_super  # runtime

from rbedge.enumerations import UITableViewStyle
from rbedge.functions import NSStringFromClass
from rbedge import pdbr

UIViewController = ObjCClass('UIViewController')
UITableView = ObjCClass('UITableView')
UIColor = ObjCClass('UIColor')

NSLayoutConstraint = ObjCClass('NSLayoutConstraint')


class SFSymbolsViewController(UIViewController):

  @objc_method
  def viewDidLoad(self) -> None:
    send_super(
      __class__,
      self,
      'viewDidLoad',
      restype=None,
    )

    # --- Navigation
    self.navigationItem.title = NSStringFromClass(__class__) if (
      title := self.navigationItem.title) is None else title

    # --- Table
    sfTableView = UITableView.alloc().initWithFrame_style_(
      self.view.bounds,
      UITableViewStyle.plain,
    )

    try:
      _bg_color = UIColor.systemCyanColor()
    except TypeError as e:
      _bg_color = UIColor.systemCyanColor
      print(_bg_color, e)
    finally:
      sfTableView.backgroundColor = _bg_color

    self.addSubviewWithLayout_(sfTableView)

  @objc_method
  def didReceiveMemoryWarning(self) -> None:
    send_super(
      __class__,
      self,
      'didReceiveMemoryWarning',
      restype=None,
    )
    print(f'\t{NSStringFromClass(__class__)}: didReceiveMemoryWarning')

  # --- layout
  @objc_method
  def addSubviewWithLayout_(self, subView: ObjCInstance) -> None:
    self.view.addSubview_(subView)
    # `False` にする
    subView.translatesAutoresizingMaskIntoConstraints = False
    # `safeAreaLayoutGuide` を基準に
    safeAreaLayoutGuide = self.view.safeAreaLayoutGuide

    # X軸を中心
    centerXAnchor = subView.centerXAnchor.constraintEqualToAnchor_(
      safeAreaLayoutGuide.centerXAnchor)

    # Y軸を中心
    centerYAnchor = subView.centerYAnchor.constraintEqualToAnchor_(
      safeAreaLayoutGuide.centerYAnchor)

    # 幅を0.5倍(半分)
    widthAnchor = subView.widthAnchor.constraintEqualToAnchor_multiplier_(
      safeAreaLayoutGuide.widthAnchor,
      0.5,
    )

    # 高さを0.5倍(半分)
    heightAnchor = subView.heightAnchor.constraintEqualToAnchor_multiplier_(
      safeAreaLayoutGuide.heightAnchor,
      0.5,
    )

    NSLayoutConstraint.activateConstraints_([
      centerXAnchor,
      centerYAnchor,
      widthAnchor,
      heightAnchor,
    ])


if __name__ == '__main__':
  from rbedge.app import App
  from rbedge.enumerations import UIModalPresentationStyle

  main_vc = SFSymbolsViewController.new()
  _title = NSStringFromClass(SFSymbolsViewController)
  main_vc.navigationItem.title = _title

  presentation_style = UIModalPresentationStyle.fullScreen

  app = App.alloc().initWithViewController_(main_vc)
  app.presentWithStyle_(presentation_style)

  try:
    import gc
    gc.collect()
  except Exception as e:
    print('--- collect: error')
    print(f'{e}')


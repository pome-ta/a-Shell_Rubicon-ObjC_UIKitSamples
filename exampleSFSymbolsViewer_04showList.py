from pyrubicon.objc import (
  ObjCClass,
  ObjCInstance,
  objc_method,
  objc_property,
)  # api
from pyrubicon.objc import send_super  # runtime

from rbedge.enumerations import UITableViewStyle
from rbedge.functions import NSStringFromClass
from rbedge import pdbr

UIViewController = ObjCClass('UIViewController')
UITableView = ObjCClass('UITableView')
UITableViewCell = ObjCClass('UITableViewCell')

UIColor = ObjCClass('UIColor')

NSLayoutConstraint = ObjCClass('NSLayoutConstraint')


class SFSymbolsViewController(UIViewController):

  # 識別子としての文字列を宣言
  cellIdentifier: str = objc_property()
  # 配列要素を宣言
  allItems: list = objc_property()

  @objc_method
  def loadView(self) -> None:
    send_super(
      __class__,
      self,
      'loadView',
      restype=None,
    )

    # 識別子としての文字列を代入
    self.cellIdentifier = 'customCell'
    # 配列要素を代入
    self.allItems = [
      'ほげ',
      'ふが',
      'ぴよ',
    ]

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
    # セルはUITableViewCell, 識別子は文字列`customCell` で登録
    sfTableView.registerClass_forCellReuseIdentifier_(
      UITableViewCell,
      self.cellIdentifier,
    )
    # UITableViewDataSource Protocol を紐付け
    sfTableView.dataSource = self

    sfTableView.backgroundColor = UIColor.systemCyanColor()

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

  # --- UITableViewDataSource
  @objc_method
  def tableView_numberOfRowsInSection_(
    self,
    tableView: ObjCInstance,
    section: int,
  ) -> int:  # Python オブジェクト`int` で返すため型を記載
    # 配列要素の総数を整数で返す
    return len(self.allItems)

  @objc_method
  def tableView_cellForRowAtIndexPath_(
    self,
    tableView: ObjCInstance,
    indexPath: ObjCInstance,
  ) -> ObjCInstance:
    # 文字列の識別子と、index で使用するセルを呼び出す
    cell = tableView.dequeueReusableCellWithIdentifier_forIndexPath_(
      self.cellIdentifier,
      indexPath,
    )
    content = cell.defaultContentConfiguration()
    content.text = self.allItems[indexPath.row]
    cell.contentConfiguration = content

    return cell

  # --- layout
  @objc_method
  def addSubviewWithLayout_(self, subView: ObjCInstance) -> None:
    self.view.addSubview_(subView)
    subView.translatesAutoresizingMaskIntoConstraints = False
    safeAreaLayoutGuide = self.view.safeAreaLayoutGuide

    centerXAnchor = subView.centerXAnchor.constraintEqualToAnchor_(
      safeAreaLayoutGuide.centerXAnchor)

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


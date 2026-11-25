from pathlib import Path
import plistlib

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
UIImage = ObjCClass('UIImage')
UIColor = ObjCClass('UIColor')

NSLayoutConstraint = ObjCClass('NSLayoutConstraint')


def get_order_list() -> list:
  CoreGlyphs_path = '/System/Library/CoreServices/CoreGlyphs.bundle/'

  symbol_order_path = 'symbol_order.plist'
  symbol_order_bundle = Path(CoreGlyphs_path, symbol_order_path)

  order_list = plistlib.loads(symbol_order_bundle.read_bytes())
  return order_list


class SFSymbolsViewController(UIViewController):

  cellIdentifier: str = objc_property()
  allItems: list = objc_property()

  @objc_method
  def loadView(self) -> None:
    send_super(
      __class__,
      self,
      'loadView',
      restype=None,
    )

    self.cellIdentifier = 'customCell'
    self.allItems = get_order_list()

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
    self.view.backgroundColor = UIColor.secondarySystemBackgroundColor()

    # --- Table
    sfTableView = UITableView.alloc().initWithFrame_style_(
      self.view.bounds,
      UITableViewStyle.plain,
    )
    sfTableView.registerClass_forCellReuseIdentifier_(
      UITableViewCell,
      self.cellIdentifier,
    )

    sfTableView.dataSource = self
    sfTableView.delegate = self

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
  ) -> int:
    return len(self.allItems)

  @objc_method
  def tableView_cellForRowAtIndexPath_(
    self,
    tableView: ObjCInstance,
    indexPath: ObjCInstance,
  ) -> ObjCInstance:
    cell = tableView.dequeueReusableCellWithIdentifier_forIndexPath_(
      self.cellIdentifier,
      indexPath,
    )

    symbol_name = self.allItems[indexPath.row]

    content = cell.defaultContentConfiguration()
    content.text = symbol_name
    content.textProperties.numberOfLines = 1
    content.image = UIImage.systemImageNamed_(symbol_name)
    cell.contentConfiguration = content

    return cell

  # --- UITableViewDelegate
  @objc_method
  def tableView_didSelectRowAtIndexPath_(
    self,
    tableView: ObjCInstance,
    indexPath: ObjCInstance,
  ) -> None:
    #tableView.deselectRowAtIndexPath_animated_(indexPath, True)
    select_item = self.allItems[indexPath.row]

    print(f'select:\t{select_item}')

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

    widthAnchor = subView.widthAnchor.constraintEqualToAnchor_multiplier_(
      safeAreaLayoutGuide.widthAnchor,
      1.0,
    )
    heightAnchor = subView.heightAnchor.constraintEqualToAnchor_multiplier_(
      safeAreaLayoutGuide.heightAnchor,
      1.0,
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


# -*- coding: utf-8 -*-

import xbmc
import xbmcgui


ACTION_SELECT_ITEM = getattr(xbmcgui, 'ACTION_SELECT_ITEM', 7)
ACTION_MOUSE_LEFT_CLICK = getattr(xbmcgui, 'ACTION_MOUSE_LEFT_CLICK', 100)
ACTION_NAV_BACK = getattr(xbmcgui, 'ACTION_NAV_BACK', 92)
ACTION_PREVIOUS_MENU = getattr(xbmcgui, 'ACTION_PREVIOUS_MENU', 10)
ACTION_BACKSPACE = getattr(xbmcgui, 'ACTION_BACKSPACE', 110)
ACTION_PARENT_DIR = getattr(xbmcgui, 'ACTION_PARENT_DIR', 9)


class DownloadPickerDialog(xbmcgui.WindowXMLDialog):
  CONTROL_TITLE = 1001
  CONTROL_SUBTITLE = 1002
  CONTROL_STATUS = 1003
  CONTROL_LIST = 1200
  CONTROL_CANCEL = 9000

  def __init__(self, *args, **kwargs):
    self.heading = kwargs.pop('heading', '')
    self.subtitle = kwargs.pop('subtitle', '')
    self.providers = kwargs.pop('providers', '')
    self.listitems = kwargs.pop('listitems', [])
    self.selected_index = -1
    self._list_control = None
    xbmcgui.WindowXMLDialog.__init__(self, *args, **kwargs)

  def onInit(self):
    self._safe_set_label(self.CONTROL_TITLE, self.heading)
    self._safe_set_label(self.CONTROL_SUBTITLE, self.subtitle)
    self._update_status()

    try:
      self._list_control = self.getControl(self.CONTROL_LIST)
      self._list_control.reset()
      for item in self.listitems:
        self._list_control.addItem(item)
      if len(self.listitems) > 0:
        self._list_control.selectItem(0)
      self.setFocusId(self.CONTROL_LIST)
      self._update_status()
    except Exception:
      self._list_control = None

  def onClick(self, controlId):
    if controlId == self.CONTROL_CANCEL:
      self.selected_index = -1
      self.close()
      return

    if controlId == self.CONTROL_LIST and self._list_control is not None:
      try:
        self.selected_index = self._list_control.getSelectedPosition()
      except Exception:
        self.selected_index = -1
      self.close()

  def onAction(self, action):
    action_id = action.getId()
    if action_id in [ACTION_NAV_BACK, ACTION_PREVIOUS_MENU, ACTION_BACKSPACE, ACTION_PARENT_DIR]:
      self.selected_index = -1
      self.close()
      return

    if action_id in [ACTION_SELECT_ITEM, ACTION_MOUSE_LEFT_CLICK] and self.getFocusId() == self.CONTROL_LIST:
      if self._list_control is not None:
        try:
          self.selected_index = self._list_control.getSelectedPosition()
        except Exception:
          self.selected_index = -1
      self.close()
      return

    self._update_status()

  def onFocus(self, controlId):
    self._update_status()

  def _safe_set_label(self, control_id, value):
    try:
      control = self.getControl(control_id)
      control.setLabel(value or '')
    except Exception:
      pass

  def _update_status(self):
    total = len(self.listitems)
    pos = 0
    if self._list_control is not None:
      try:
        pos = int(self._list_control.getSelectedPosition()) + 1
      except Exception:
        pos = 0

    if total <= 0:
      status = '0 items'
    elif pos <= 0:
      status = '%d items' % (total)
    else:
      status = '%d items  -  %d/%d' % (total, pos, total)

    if self.providers:
      status = '%s   |   %s' % (self.providers, status)

    self._safe_set_label(self.CONTROL_STATUS, status)

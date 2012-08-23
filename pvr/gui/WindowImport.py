import pvr.gui.WindowMgr as WinMgr
import pvr.gui.DialogMgr as DiaMgr
from pvr.gui.BaseWindow import BaseWindow, SettingWindow, LivePlateWindow, Action
from pvr.gui.BaseDialog import BaseDialog, SettingDialog
from ElisProperty import ElisPropertyEnum, ElisPropertyInt
from pvr.Util import RunThread, GuiLock, GuiLock2, TimeToString, TimeFormatEnum
from pvr.GuiHelper import *
from pvr.gui.GuiConfig import *
from ElisEventClass import *
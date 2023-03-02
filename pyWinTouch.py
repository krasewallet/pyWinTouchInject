from ctypes import *
from ctypes.wintypes import *
from enum import IntEnum

class POINTER_INPUT_TYPE(IntEnum):
  PT_POINTER = 1
  PT_TOUCH = 2
  PT_PEN = 3
  PT_MOUSE = 4
  PT_TOUCHPAD = 5

class POINTER_FLAGS(IntEnum):
  POINTER_FLAG_NONE = 0x00000000
  POINTER_FLAG_NEW = 0x00000001
  POINTER_FLAG_INRANGE = 0x00000002
  POINTER_FLAG_INCONTACT = 0x00000004
  POINTER_FLAG_FIRSTBUTTON = 0x00000010
  POINTER_FLAG_SECONDBUTTON = 0x00000020
  POINTER_FLAG_THIRDBUTTON = 0x00000040
  POINTER_FLAG_FOURTHBUTTON = 0x00000080
  POINTER_FLAG_FIFTHBUTTON = 0x00000100
  POINTER_FLAG_PRIMARY = 0x00002000
  POINTER_FLAG_CONFIDENCE = 0x00004000
  POINTER_FLAG_CANCELED = 0x00008000
  POINTER_FLAG_DOWN = 0x00010000
  POINTER_FLAG_UPDATE = 0x00020000
  POINTER_FLAG_UP = 0x00040000
  POINTER_FLAG_WHEEL = 0x00080000
  POINTER_FLAG_HWHEEL = 0x00100000
  POINTER_FLAG_CAPTURECHANGED = 0x00200000
  POINTER_FLAG_HASTRANSFORM = 0x00400000

class POINTER_BUTTON_CHANGE_TYPE(IntEnum):
    POINTER_CHANGE_NONE = 0
    POINTER_CHANGE_FIRSTBUTTON_DOWN = 1
    POINTER_CHANGE_FIRSTBUTTON_UP = 2
    POINTER_CHANGE_SECONDBUTTON_DOWN = 3
    POINTER_CHANGE_SECONDBUTTON_UP = 4
    POINTER_CHANGE_THIRDBUTTON_DOWN = 5
    POINTER_CHANGE_THIRDBUTTON_UP = 6
    POINTER_CHANGE_FOURTHBUTTON_DOWN = 7
    POINTER_CHANGE_FOURTHBUTTON_UP = 8 
    POINTER_CHANGE_FIFTHBUTTON_DOWN = 9
    POINTER_CHANGE_FIFTHBUTTON_UP = 10

class POINTER_INFO(Structure):
  _fields_ = [
    ("pointerType", c_int),
    ("pointerId", c_uint32),
    ("frameId", c_uint32),
    ("pointerFlags", c_int),
    ("sourceDevice", HANDLE),
    ("hwndTarget", HWND),
    ("ptPixelLocation", POINT),
    ("ptHimetricLocation", POINT),
    ("ptPixelLocationRaw", POINT),
    ("ptHimetricLocationRaw", POINT),
    ("dwTime", DWORD),
    ("historyCount", c_uint32),
    ("InputData", c_int32),
    ("dwKeyStates", DWORD),
    ("PerformanceCount", c_uint64),
    ("ButtonChangeType", DWORD),
  ]

class POINTER_TOUCH_INFO(Structure):
  _fields_ = [
    ("pointerInfo", POINTER_INFO),
    ("touchFlags", c_uint32),
    ("touchMask", c_uint32),
    ("rcContact", RECT),
    ("rcContactRaw", RECT),
    ("orientation", c_uint32),
    ("pressure", c_uint32),
  ]

class TouchItem :
  def __init__(self, touchId : int) -> None:
    self.touchInfo = POINTER_TOUCH_INFO()
    memset(byref(self.touchInfo), 0, sizeof(POINTER_TOUCH_INFO))
    self.touchInfo.pointerInfo.pointerType = POINTER_INPUT_TYPE.PT_TOUCH
    self.touchInfo.pointerInfo.pointerId = touchId;
    self.touchInfo.pointerInfo.touchFlags = 0x00000000; #TOUCH_FLAG_NONE
    self.touchInfo.pointerInfo.touchMask = 0x00000001 | 0x00000002 | 0x00000004 #TOUCH_MASK_CONTACTAREA | TOUCH_MASK_ORIENTATION | TOUCH_MASK_PRESSURE;
    self.touchInfo.pointerInfo.orientation = 90
    self.touchInfo.pointerInfo.pressure = 32000

    self.lastXPos = 0
    self.lastYPos = 0

    self.isEnable = False
  
  def setTouchPoint(self, xPos : int, yPos : int) -> None :
    self.touchInfo.pointerInfo.ptPixelLocation.x = xPos
    self.touchInfo.pointerInfo.ptPixelLocation.y = yPos
    self.touchInfo.rcContact.top = yPos - 2
    self.touchInfo.rcContact.bottom = yPos + 2
    self.touchInfo.rcContact.left = xPos - 2
    self.touchInfo.rcContact.right = xPos + 2

    self.lastXPos = xPos
    self.lastYPos = yPos

  def updateTouchNextState(self):
    if self.touchInfo.pointerInfo.pointerFlags == (POINTER_FLAGS.POINTER_FLAG_DOWN | POINTER_FLAGS.POINTER_FLAG_INRANGE | POINTER_FLAGS.POINTER_FLAG_INCONTACT):
      self.touchInfo.pointerInfo.pointerFlags = POINTER_FLAGS.POINTER_FLAG_UPDATE | POINTER_FLAGS.POINTER_FLAG_INRANGE | POINTER_FLAGS.POINTER_FLAG_INCONTACT
    elif self.touchInfo.pointerInfo.pointerFlags == POINTER_FLAGS.POINTER_FLAG_UP:
      self.isEnable = False
  
  def touchDown(self, xPos : int, yPos : int) -> None :
    self.setTouchPoint(xPos, yPos)
    self.touchInfo.pointerInfo.pointerFlags = POINTER_FLAGS.POINTER_FLAG_DOWN | POINTER_FLAGS.POINTER_FLAG_INRANGE | POINTER_FLAGS.POINTER_FLAG_INCONTACT
    self.isEnable = True

  def touchMove(self, xPos : int, yPos : int) -> None :
    self.setTouchPoint(xPos, yPos)
    self.touchInfo.pointerInfo.pointerFlags = POINTER_FLAGS.POINTER_FLAG_UPDATE | POINTER_FLAGS.POINTER_FLAG_INRANGE | POINTER_FLAGS.POINTER_FLAG_INCONTACT

  def touchUp(self) -> None :
    self.setTouchPoint(self.lastXPos, self.lastYPos)
    self.touchInfo.pointerInfo.pointerFlags = POINTER_FLAGS.POINTER_FLAG_UP

class TouchMananger:
  def __init__(self, maxCount : int  = 10) -> None:
    windll.user32.InitializeTouchInjection(maxCount, 0x3) #TOUCH_FEEDBACK_NONE

  def initTouches(self, count : int) -> None:
    self.count = count
    self.touches = []
    for i in range(count):
      self.touches.append(TouchItem(i))
  
  def touchDown(self, touchId : int, xPos : int, yPos : int) -> None:
    if touchId > len(self.touches):
      return
    self.touches[touchId].touchDown(xPos, yPos)

  def touchMove(self, touchId : int, xPos : int, yPos : int) -> None:
    if touchId > len(self.touches):
      return
    self.touches[touchId].touchMove(xPos, yPos)

  def touchUp(self, touchId : int) -> None:
    if touchId > len(self.touches):
      return
    self.touches[touchId].touchUp()

  def updateTouches(self) -> None:
    touchesEnabled = [ item.touchInfo for item in self.touches if item.isEnable]
    enabledCnt = len(touchesEnabled)
    if enabledCnt:
      windll.user32.InjectTouchInput(enabledCnt,byref((POINTER_TOUCH_INFO * enabledCnt)(*touchesEnabled)))
    for item in self.touches:
      if item.isEnable:
        item.updateTouchNextState()

if __name__ == "__main__":
  import time
  time.sleep(5)
  manager = TouchMananger()
  manager.initTouches(10)
  manager.touchDown(0, 100, 300)
  manager.updateTouches()
  time.sleep(0.05)

  manager.touchMove(0, 100, 300)
  manager.updateTouches()
  time.sleep(0.05)

  manager.touchMove(0, 200, 300)
  manager.updateTouches()
  time.sleep(0.05)

  manager.touchMove(0, 400, 450)
  manager.updateTouches()
  time.sleep(0.05)

  manager.touchUp(0)
  manager.updateTouches()

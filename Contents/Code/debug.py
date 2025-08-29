# -*- coding: utf-8 -*-
# coding=utf-8


# --------------------------- debug functions ---------------------------
   
def log_timing(func):
  ''' Замер времени выполнения функции, декоратор, миллисекунды'''
  def wrapper(*args, **kwargs):
      # "Действие перед выполнением функции"
      msStart = getMilliseconds(Datetime.Now()) # type: ignore
      func_name = ("%s" % func).split(" ")[1] #- тут имя функции 
      #w(u"%s len(arg)=%i" % (func_name, len(args)))
      if len(args) > 1:
          func_param = args[1]
      else:
          func_param = "-?empty args?-"
      #     func_param = args[1] if len(args)>0 else "-???-"
      # strArgs (<__code__.KinoPoiskUnoficialAgent object at 0x00000000049466d0>, 
      # MediaContainer(art=None, noHistory=False, title1=None, title2=None, replaceParent=False), 
      # <Framework.api.agentkit.TV_Show object at 0x00000000046680d0>, ru)
      strArgs = ', '.join(map(str, list(args)))
      d("<<<<<<< timing start::%s (%s)" % (func_name, func_param))   #strArgs
      func(*args, **kwargs)
      # ("Действие после выполнения функции")
      d(">>>>>>> timing end::%s , duration=%s (%s)"  % (func_name, (getMilliseconds(Datetime.Now()) - msStart), u"s % func_param" )) # type: ignore
  return wrapper


def d(*args):
  '''Включить подробную отладку по Prefs['trace']
  в логе DEBUG
  '''
  if Prefs['trace']: # type: ignore
    args = list(args)
    args[0] = '     #### %s' % args[0]
    strargs = '\n'.join(map(str, args))
    Core.log.debug(strargs)     # type: ignore


def w(*args):
  ''' в логе WARNING
  '''
  args = list(args)
  args[0] = '   ^^^^ %s' % str(args[0])
  strargs = '\n'.join(map(str, args))
  Core.log.warning(strargs)   # type: ignore   
  
  
# inner -------------------------------------
def getMilliseconds(dt):
  ''' Только миллисекунды, в полночь - тыква'''
  # dt waiting as '2025-01-25 12:41:53.921000'
  strDt = "%s" % dt                 # to str
  arrDt = strDt.split(" ")          # ["2025-01-25", "12:41:53.921000"]
  if len(arrDt) != 2:               # err
    return
  strTime = arrDt[1]                # 12:41:53.921000
  arrTime = strTime.split(":")      # ["12", "41", "53.921000"]
  arrTime.reverse()                 # ["53.921000", "41", "12"]
  sec = arrTime[0].split(".")       #  ["53", "921000"]
  arrTime[0] = sec[0]               # ["53", "41", "12"]
  if len(arrTime) != 3:             # err   проверку на 3 - и выйти, если не так.
    return
  seconds = 0
  for i in range(0, 3):
    seconds += int(arrTime[i]) * (60**i)
  seconds = seconds * 1000          # milliseconds
  seconds += int(sec[1])/1000       # 921000 -> 921 
  return int(seconds)               #     milliseconds   

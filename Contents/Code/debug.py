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


# ----UNUSED----------------------- log decoration functions ---------------------------

def pp_json(json, lev=0):
  '''Pretty print json'''
  res = ""
  if not isinstance(json, dict):    # это может быть и list
    return "--%s-- Это не dict JSON !!!" % json
  trail = ""
  for i in range(0, lev):
    trail += "  "
  for key in json:
    val = json[key]
    if isinstance(val, list):
      res += "%s%s:[\n" % (trail, key)
      lev += 1
      for i, el in enumerate(val):
        res += trail
        res += pp_json(val[i], lev)
      res += "%s]\n" % trail
    else:
      res += ("%s%s: %s\n" % (trail, key, json[key]))
  return res



def get_media_data(media, isUpdate=False):
  ''' отображает данные для search media - Movie|TV_Show'''
  m = "\nmedia:\n"
  m += ".media.primary_agent : %s\n" % media.primary_agent
  m += ".media.primary_metadata : %s\n" % media.primary_metadata
  m += ".media.guid : %s\n" % media.guid
  m += ".media.filename : %s\n" % media.filename
  m += ".media.parent_metadata : %s\n" % media.parent_metadata
  # 
  m += ".media.tree : %s\n" % media.tree
  m += ".media.id : %s\n" % media.id
  m += ".media.hash : %s\n" % media.hash
  m += ".media.originally_available_at : %s\n" % media.originally_available_at
  if hasattr(media, 'season'):       # if TV_Show
    m += ".media.parentGUID : %s\n" % media.parentGUID    # Movie has no the attribute
    #m += "TV_Show. : %s\n" % 
    pass
  else:                        # Movie
    m += "Movie.media.name : %s\n" % media.name
    m += "Movie.media.openSubtitlesHash : %s\n" % media.openSubtitlesHash
    m += "Movie.media.year : %s\n" % media.year
    m += "Movie.media.duration : %s\n" % media.duration
    #m += "movie. : %s\n" % 
  return m
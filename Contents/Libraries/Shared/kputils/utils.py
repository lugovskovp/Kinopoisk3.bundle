# -*- coding: utf-8 -*-
# coding=utf-8
        

class ejson():
  ''' Расширенный json, get'''  
  def __init__(self, json):
    self.json = json
  
  def __repr__(self):
    return self.json.__repr__()

  def __iter__(self):
    self.n = 0
    return self
  
  def __next__(self):
    if self.n <= len(self.json):
        res = self.json[self.n]
        self.n += 1
        return res
    else:
        raise StopIteration
  
  def get(self, key):
    ''' get возвращает значение ключа, либо пустой словарь, если ключа нет'''
    res = ''
    try:
      res = self.json[key]
    except:
      Log("ERROR ejson^ json[%s] = %s" % (key, res)) # type: ignore
      return res
    if res is None:
      return ''
    if isinstance(res, list): # если массив
      eres = []
      for item in res:        # каждый item - json
        eres.append(ejson(item))
      res = eres              # тогда вернём массив ejson-ов
    return res  

  def get_int(self, key):
    '''get_int возвращает целое числовое значение или 0'''       
    res = self.get(key)  
    try:
        res = int(res)
    except:
        res = 0
    return res


    
'''
md = ejson(mydata)
jd= {'nameRu': 'Джосс Уидон', 'description': None, 'posterUrl': 'https://st.kp.yandex.net/images/actor_iphone/iphone360_178.jpg', 'professionText': 'Режиссеры', 'staffId': 178, 'nameEn': 'Joss Whedon', 'professionKey': 'DIRECTOR'}
print(len(jd))
ej = ejson(jd)

for item in ej.json:
    print(item)

j0 = ejson(json_test_01)
a1 = j0.get('films')
for m in a1:
  print(m.get('nameRu'))
'''
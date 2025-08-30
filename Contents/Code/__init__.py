# -*- coding: utf-8 -*-
# coding=utf-8

from common_srch import srch_params, srch_and_score, srch_mkres       # общие для поиска в классах
from common_upd import load_distribution, load_episodes, load_gallery, load_metadata, load_reviews, load_staff # общие для апдейта в классах
from config import NAME, VER, LANGUAGES, UPDATE_INTERVAL_MIN, REQUEST_QTY_SEARCH_MIN, APItokenRemains    # константы
from debug import d, w, log_timing
from updater import Updater   

              
##################################################################
def Start():
  Log("\n\n========== START %s %s =============" % (NAME, VER)) # type: ignore 
  HTTP.CacheTime = 0                                  # type: ignore #CACHE_1HOUR
  ValidatePrefs()                 # start autoupdate
    
    
def ValidatePrefs():
  ''' This function is called when the user modifies their preferences.'''
  # update interval must be more than 10 minutes
  UpdateInterval = int(Prefs['update_interval'] or UPDATE_INTERVAL_MIN)*60          # type: ignore
  # starting update check
  Chanel = Prefs['update_channel']                                # type: ignore
  d(u"ValidatePrefs: start: update chanel=%s, interval=%i sec" % (Chanel, UpdateInterval))  # type: ignore
  if Chanel != 'none':                                  
    Thread.CreateTimer(UpdateInterval, Updater.auto_update_thread, core=Core, pref=Prefs)  # type: ignore
  d(u"ValidatePrefs: end.")


@handler(prefix='/applications/KinoPoiskUnoficial', name='KinoPoiskUnoficial ({})'.format(VER)) # type: ignore 
def main():
    """
    Создаёт plug-in ``handler``.
    Единственно для существования в меню настроек иконки плагина.
    Т.к. используется декоратор ``@handler`` , в самой функции достаточно pass.
    """
    pass

##################################################################
class KinoPoiskUnoficialAgent(Agent.Movies): # type: ignore
  '''
  search
  update
  '''
  name              = '%s (%s) Movies' % (NAME, VER) 
  primary_provider  = True  # могут быть выбраны в качестве основного источника метаданных
  fallback_agent    = False # идентификатор другого агента для использования в качестве резервного
  #     contributes_to идентификаторы первичных агентов, которым агент может передавать вторичные данные
  contributes_to    = ['com.plexapp.plugins.kinopoisk3', 'com.plexapp.agents.local']
  # contributes_to    = ['com.plexapp.plugins.kinopoisk3', 'com.plexapp.agents.local', 'com.plexapp.agents.themoviedb', 'com.plexapp.agents.imdb'] 
  # contributes_to    = ['com.plexapp.plugins.kinopoisk3', 'com.plexapp.agents.themoviedb']
  languages         = LANGUAGES  #languages=[['ru', 'en', 'xn']]
  #     accepts_from идентификаторы агентов, которые могут добавлять вторичные данные к первичным данным, предоставляемым этим агентом
  accepts_from      = ['com.plexapp.plugins.kinopoisk3', 'com.plexapp.agents.local'] 
  agent_type        = 'Movies'
  
     
  @log_timing
  def search(self, results, media, lang, manual=False):
    ''' • self – A reference to the instance of the agent class.
        • results (ObjectContainer (page 52)) – An empty container that the developer should populate with potential matches.
        • media (Media (page 36)) – An object containing hints to be used when performing the search.
          В search media - Movie|TV_Show, а вот в update media это MediaTree 
        • lang (str - A string identifying the users currently selected language. This will be one of the constants added to the agents languages attribute.
        • manual (bool - A boolean value identifying whether the search was issued automatically during scanning, or manually by the user (in order to fix an incorrect match)  
    '''   
    #   1 - Подготовка параметров поиска
    srch = srch_params(media, manual)
    Log("\n\n<<<<%s.SEARCH %s, %s, %s %s start\n" % (self.name, srch.str_titles, srch.year, srch.match_type, srch.search_type))# type: ignore
    #   2 - MUST to have a valid token for continue
    HaveToken = APItokenRemains()
    if not HaveToken:
      w(u">>>SEARCH STOPPED: has no valid key or not remains daily attempts")                  # type: ignore
      return
    if HaveToken < REQUEST_QTY_SEARCH_MIN:
      w(u">>>SEARCH STOPPED: Не хватит реквестов в ключе - осталось всего %i" % HaveToken)                  # type: ignore
      return
    #    3 - Поиск и скоринг
    finded = {'films':[]}        # найденные 'films'
    srch_and_score(srch, finded, results)  
    #    4 - Формирование результатов для отображения (если ручной) или (найденные имена) - если автомат.
    srch_mkres(srch, finded, results)
    Log("\n>>>>%s.search %s %s END\n" % (self.name, srch.str_titles, srch.year))# type: ignore

  @log_timing
  def update(self, metadata, media, lang):
    '''
    self      KinoPoiskUnnoficialAgent
    metadata  Framework.models.metadata.com_plexapp_plugins_kinopoisk3.Movie
    media     MediaTree   (search - Movie|TV_Show)
    '''
    HaveToken = APItokenRemains()
    if not HaveToken:
      w(u">>>UPDATE STOPPED: has no valid key or not remains daily attempts")                  # type: ignore
      return    
    Log("\n\n ---------- %s.UPDATE start: m.id=%s tokenQuota=%s" % (self.name, metadata.id, HaveToken))          # type: ignore
    Log("\n metadata-metadata type: %s %s " % (metadata.title, metadata.year)) # type: ignore
    # Log("\n media-MediaTree id: %s, tree: %s, name" % (media.id, media.tree, media.name))

    valid_posters = []
    valid_poster0 = []
    valid_arts = []   
    media.thumb = ""
    @parallelize    # type: ignore # load_gallery posters, duration=3523, load_gallery arts, duration=4383, update, duration=4389
    def parallel_update():
      # постеры и галерею - самыми первыми: они самые долгие
      @task # type: ignore
      def upd_posters(metadata=metadata, valid_posters = valid_posters):
        load_gallery(metadata, valid_posters, IsNeedPosters=True)  # 'POSTER'
      @task # type: ignore
      def upd_arts(metadata=metadata):
        load_gallery(metadata, valid_arts, IsNeedPosters=False)  #  'WALLPAPER'
        pass
      @task # type: ignore
      def upd_staff(metadata=metadata):
        load_staff(metadata)
      @task # type: ignore
      def upd_reviews(metadata=metadata):    
        if Prefs['desc_load_reviews']: # type: ignore  
          load_reviews(metadata)
      @task # type: ignore
      def upd_meta(metadata=metadata):
        load_metadata(metadata, valid_poster0)
        media.title = metadata.title        # в media - надо вернуть наименование выбранного фильма - заменив текущее из поиска
      @task # type: ignore
      def upd_distribution(metadata=metadata):
        load_distribution(metadata)
    # параллельная работа окончена, все задачи завершены
    valid_names = valid_poster0 + valid_posters
    metadata.posters.validate_keys(valid_names)
    metadata.art.validate_keys(valid_arts)
    if len(valid_names) > 0:
      media.thumb = valid_names[0]
    d(" ************* KinoPoiskUnnoficialAgent.UPDATE.end\n")




class KinoPoiskUnoficialAgent(Agent.TV_Shows): # type: ignore
  '''
  search - при ручном поиске в результаты выводит сезоны сериала для выбора верного
    • self – A reference to the instance of the agent class.
    • results (ObjectContainer (page 52)) – An empty container that the developer should populate with potential matches.
    • media (Media (page 36)) – An object containing hints to be used when performing the search.
      В search media - Movie|TV_Show, а вот в update media это MediaTree 
    • lang (str - A string identifying the users currently selected language. This will be one of the constants added to the agents languages attribute.
    • manual (bool - A boolean value identifying whether the search was issued automatically during scanning, or manually by the user (in order to fix an incorrect match)  
  '''   
  name              = '%s (%s) Serials' % (NAME, VER) 
  primary_provider  = True 
  fallback_agent    = False 
  # contributes_to    = ['com.plexapp.plugins.kinopoisk3', 'com.plexapp.agents.local']
  # contributes_to    = ['com.plexapp.plugins.kinopoisk3', 'com.plexapp.agents.local', 'com.plexapp.agents.themoviedb', 'com.plexapp.agents.imdb'] 
  languages         = LANGUAGES  #languages=['ru', 'en', 'xn']
  #accepts_from      = ['com.plexapp.agents.localmedia'] 
  agent_type        = 'TV_Shows'


  @log_timing  
  def search(self, results, media, lang, manual=False):
    '''
    manual = [True|False]
    '''
    #   1 - Подготовка параметров поиска
    srch = srch_params(media, manual)
    Log("\n\n<<<<%s.SEARCH %s, %s, %s %s start\n" % (self.name, srch.str_titles, srch.year, srch.match_type, srch.search_type))# type: ignore
    #   2 - MUST to have a valid token for continue
    HaveToken = APItokenRemains()
    if not HaveToken:
      w(u">>>SEARCH STOPPED: has no valid key or not remains daily attempts")                  # type: ignore
      return
    if HaveToken < REQUEST_QTY_SEARCH_MIN:
      w(u">>>SEARCH STOPPED: Не хватит реквестов в ключе - осталось всего %i" % HaveToken)                  # type: ignore
      return
    #    3 - Поиск и скоринг
    finded = {'films':[]}        # найденные 'films'
    srch_and_score(srch, finded, results)  
    #    4 - Формирование результатов для отображения (если ручной) или (найденные имена) - если автомат.
    srch_mkres(srch, finded, results)
    Log("\n>>>>%s.search %s %s END\n" % (self.name, srch.str_titles, srch.year))# type: ignore


  @log_timing  
  def update(self, metadata, media, lang):
    # В search media - Movie|TV_Show, а вот в update media это Framework.api.agentkit.MediaTree
    '''
    Framework.api.agentkit.MediaTree 
      [] Framework.api.agentkit.MediaPart
    '''
    HaveToken = APItokenRemains()
    if not HaveToken:
      w(u">>>UPDATE STOPPED: has no valid key or not remains daily attempts")                  # type: ignore
      return
    d("\n\n ---------- %s.UPDATE start: m.id=%s tokenQuota=%s" % (self.name, metadata.id, HaveToken))
    d( 'media.all_parts parts: %s' % media.all_parts()[0] )     # MediaPart
    # 'MediaPart' object has no attribute  filename name path     d( 'media.all_parts[0] size: %s' % media.all_parts()[0].size )
    d( 'media.all_parts seasons: %s' % media.seasons ) 
    valid_posters = []
    valid_poster0 = []
    valid_arts = []   
    media.thumb = ""

    @parallelize    # type: ignore # load_gallery posters, duration=3523, load_gallery arts, duration=4383, update, duration=4389
    def parallel_update():
      # постеры и галерею - самыми первыми: они самые долгие
      @task # type: ignore
      def upd_posters(metadata=metadata, valid_posters = valid_posters):
        load_gallery(metadata, valid_posters, IsNeedPosters=True)  # 'POSTER'
      @task # type: ignore
      def upd_arts(metadata=metadata):
        load_gallery(metadata, valid_arts, IsNeedPosters=False)  #  'WALLPAPER'
        pass
      @task # type: ignore
      def upd_staff(metadata=metadata):
        load_staff(metadata)
      @task # type: ignore
      def upd_reviews(metadata=metadata):  
        if Prefs['desc_load_reviews']: # type: ignore  
          load_reviews(metadata)
      @task # type: ignore
      def upd_meta(metadata=metadata):
        load_metadata(metadata, valid_poster0)
        '''if hasattr(media, 'show'):     # в media - надо вернуть наименование выбранного фильма - заменив текущее из поиска
          media.show = metadata.title
        else:
          media.name = metadata.title'''
        media.title = metadata.title        # в media - надо вернуть наименование выбранного фильма - заменив текущее из поиска
      @task # type: ignore
      def upd_episodes(metadata=metadata):
        load_episodes(metadata, media)
    # параллельная работа окончена, все задачи завершены
    valid_names = valid_poster0 + valid_posters
    #metadata.posters.validate_keys(valid_names)
    #metadata.art.validate_keys(valid_arts)
    media.thumb = valid_names[0]
    
  


# ========================================================================


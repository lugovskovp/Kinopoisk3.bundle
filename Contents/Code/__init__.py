# -*- coding: utf-8 -*-
# coding=utf-8

from common_srch import srch_params, srch_and_score, srch_mkres       # общие для поиска в классах
from common_upd import load_distribution, load_episodes, load_gallery, load_metadata, load_reviews, load_staff # общие для апдейта в классах
from config import NAME, VER, LANGUAGES, REQUEST_QTY_SEARCH_MIN, UNKNOWN_YEAR    # константы UPDATE_INTERVAL_MIN, 
from debug import d, w, log_timing  #, inspect_obj
from updater import Updater   
from utils import APItokenRemains, getGUIDs, resurrectMetadataId


#################################################################
def Start():
  Log("\n\n========== START %s %s =============" % (NAME, VER))   # type: ignore 
  HTTP.CacheTime = 0                                              # type: ignore #CACHE_1HOUR
  ValidatePrefs()                                                 # start autoupdate
    
    
def ValidatePrefs():
  ''' This function is called when the user modifies their preferences.'''
  UpdateInterval = int(Prefs['update_interval'] or UPDATE_INTERVAL_MIN)*60          # type: ignore
  # При старте плагина - проверить обновления и обновить. #64
  Chanel = Prefs['update_channel']                                            # type: ignore
  UpdateInterval = int(Prefs['update_interval'] or UPDATE_INTERVAL_MIN)*60          # type: ignore
  if Chanel != 'none':                                  
    d(u"ValidatePrefs: Immediatle update, chanel=%s" % (Chanel))
    Thread.CreateTimer(0, Updater.auto_update_thread, core=Core, pref=Prefs)  # type: ignore
  else:
    d(u"ValidatePrefs: NO update: chanel=%s, interval=%i sec" % (Chanel, UpdateInterval))  # type: ignore
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
    
    Log('Guids:%s' %  media.guid)        # type: ignore
    Guids = getGUIDs(media.guid)
    if not Guids['kpId']:
      media.guid = media.guid + 'kp' + metadata.id

    # AttributeError: 'TV_Show' object has no attribute 'year'
    # Log("metadata-metadata title(year): %s (%s) " % (metadata.title, metadata.year)) # type: ignore
    # Check if 'year' attribute exists
    t = ''
    if hasattr(metadata, 'title'):
      t = metadata.title
    y = UNKNOWN_YEAR
    if hasattr(metadata, 'year'):
      y = metadata.year
    Log("metadata-metadata title(year): %s (%s) " % (t, y)) # type: ignore
    del t
    del y
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
      def upd_meta(metadata=metadata, media=media):
        load_metadata(metadata, media, valid_poster0)
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
    manual = [True|False] p.36: manual – A boolean value identifying whether the search was issued auto
    atically during scanning, or manually by the user (in order to fix an  incorrect match) - БРЕХНЯ
    ВСЕГДА False. 
    Поэтому отлавливать 
    srch.match_type:
    Fix match - либо при автосопоставлении, либо первое предложение при открытии "Сопоставить"
    New match - это вручную, с вкладки "Опции поиска"
    '''
    # media.season = '1'
    # inspect_obj(media)
    
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
  def update(self, metadata, media, lang):    # def update(self, metadata, media, lang, force)
    # В search media - Movie|TV_Show, а вот в update media это Framework.api.agentkit.MediaTree
    '''
    Framework.api.agentkit.MediaTree 
      [] Framework.api.agentkit.MediaPart
    '''
    d("\n\n ---------- %s.UPDATE start: mtd.id: %s, mtd.title: %s" % (self.name, metadata.id, metadata.title))
    
    '''
    inspect_obj(media)
    ('_core', <weakproxy at 0000000003C086B0 to FrameworkCore at 00000000040D9F50>)
    ('_level_name', 'seasons')
    ('addedAt', '1763649916')
    ('added_at', '1763649916')
    ('all_parts', <bound method MediaTree.all_parts of <Framework.api.agentkit.MediaTree object at 0x0000000005ad9f10>>)
    ('children', [<Framework.api.agentkit.MediaTree object at 0x000000000482c110>])
    ('guid', 'com.plexapp.plugins.kinopoisk3://1331649?lang=ru')
    ('id', '580')
    ('index', '1')
    ('instanceRatingKey', '')
    ('items', [])
    ('originallyAvailableAt', '')
    ('originally_available_at', '')
    ('parentTitle', '')
    ('refreshedAt', '1763712646')
    ('refreshed_at', '1763712646')
    ('seasons', {'3': <Framework.api.agentkit.MediaTree object at 0x000000000482c110>})
    ('settings', {'subtitleMode': '-1', 'showOrdering': '', 'subtitleLanguage': '', 'episodeSort': '-1', 'autoDeletionItemPolicyUnwatchedLibrary': '0', 'audioLanguage': '', 'autoDeletionItemPolicyWatchedLibrary': '0', 'flattenSeasons': '-1'})
    ('title', u'\u041c\u0435\u0434\u043b\u0435\u043d\u043d\u044b\u0435 \u043b\u043e\u0448\u0430\u0434\u0438/Slow Horses [\u0412\u0435\u043b\u0438\u043a\u043e\u0431\u0440\u0438\u0442\u0430\u043d\u0438\u044f,..] \u0434\u0435\u0442\u0435\u043a\u0442\u0438\u0432')
    '''
    
    '''
    inspect_obj(media.seasons['3'])
    ('_core', <weakproxy at 00000000034EE6B0 to FrameworkCore at 0000000004149F50>)
    ('_level_name', 'episodes')
    ('addedAt', '1763647483')
    ('added_at', '1763647483')
    ('all_parts', <bound method MediaTree.all_parts of <Framework.api.agentkit.MediaTree object at 0x00000000057d9150>>)
    ('children', [<Framework.api.agentkit.MediaTree object at 0x00000000057d97d0>, <Framework.api.agentkit.MediaTree object at 0x0000000005b2d4d0>, <Framework.api.agentkit.MediaTree object at 0x0000000005b2d7d0>, <Framework.api.agentkit.MediaTree object at 0x0000000005b2da50>, <Framework.api.agentkit.MediaTree object at 0x0000000005b2dcd0>, <Framework.api.agentkit.MediaTree object at 0x0000000005b2df50>])
    ('episodes', {'1': <Framework.api.agentkit.MediaTree object at 0x00000000057d97d0>, '3': <Framework.api.agentkit.MediaTree object at 0x0000000005b2d7d0>, '2': <Framework.api.agentkit.MediaTree object at 0x0000000005b2d4d0>, '5': <Framework.api.agentkit.MediaTree object at 0x0000000005b2dcd0>, '4': <Framework.api.agentkit.MediaTree object at 0x0000000005b2da50>, '6': <Framework.api.agentkit.MediaTree object at 0x0000000005b2df50>})
    ('guid', 'local://581')
    ('id', '581')
    ('index', '3')
    ('instanceRatingKey', '')
    ('items', [])
    ('originallyAvailableAt', '')
    ('originally_available_at', '')
    ('parentTitle', '')
    ('refreshedAt', '-1')
    ('refreshed_at', '-1')
    ('settings', {})
    ('title', '')
    '''

    '''
    inspect_obj(media.seasons['3'].episodes[1])
    ep:<class 'Framework.api.agentkit.MediaTree'>:<Framework.api.agentkit.MediaTree object at 0x00000000058df850>

    ('addedAt', '1763647483')
    ('added_at', '1763647483')
    ('all_parts', <bound method MediaTree.all_parts of <Framework.api.agentkit.MediaTree object at 0x0000000005722790>>)
    ('children', [])
    ('guid', 'local://582')
    ('id', '582')
    ('index', '1')
    ('instanceRatingKey', '')
    ('items', [<Framework.api.agentkit.MediaItem object at 0x0000000005afe190>])
    ('originallyAvailableAt', '2022-12-31')
    ('originally_available_at', '2022-12-31')
    ('parentTitle', '')
    ('refreshedAt', '-1')
    ('refreshed_at', '-1')
    ('settings', {})
    ('title', '')
    '''

    '''
        inspect_obj(media.seasons['3'].episodes[1].items[0].parts)
        it:<class 'Framework.api.agentkit.MediaItem'>
        ('_core', <weakproxy at 0000000003A086B0 to FrameworkCore at 000000000407EF50>)
        ('parts', [<Framework.api.agentkit.MediaPart object at 0x000000000588f110>])

    inspect_obj(media.seasons['3'].episodes[1].items[0].parts[0])
    pt
    ('_core', <weakproxy at 0000000003C286B0 to FrameworkCore at 0000000004035F50>)
    ('_path', u'C:\\Users\\plugo\\AppData\\Local\\Plex Media Server\\Media\\localhost\\4\\7e5ba5fad4e2361d044a5b4be4ba0f09bbb50d2.bundle')
    ('art', <Framework.api.agentkit.MediaContentsDirectory object at 0x0000000005b412d0>)
    ('duration', '2644809')
    ('file', 'c:\\DIY\\Plex\\Media\\Serials\\Slow.Horses.S03.WEB-DLRip.LostF.01\\Slow.Horses.S03E01.WEB-DLRip.RGzsRutracker.avi')
    ('hash', '47e5ba5fad4e2361d044a5b4be4ba0f09bbb50d2')
    ('id', '610')
    ('metadataType', '4')
    ('openSubtitleHash', 'eefa031f3b8651f3')
    ('size', 660490240L)
    ('streams', [<Framework.api.agentkit.MediaStream object at 0x0000000005b41190>, <Framework.api.agentkit.MediaStream object at 0x0000000005b41450>, <Framework.api.agentkit.MediaStream object at 0x0000000005b414d0>])
    ('subtitles', <Framework.api.agentkit.SubtitlesDirectory object at 0x0000000005b41410>)
    ('thumbs', <Framework.api.agentkit.MediaContentsDirectory object at 0x0000000005b411d0>)
    '''
    '''   
    # media.title # Медленные лошади/Slow Horses [Великобритания,..] детектив
    if len(media.seasons) == 1:
      for k in media.seasons:
        pass
      Log("media.seasons.key= %s" % k) # ('seasons', {'3': <Framework.api.agentkit.MediaTree object at 0x000000000482c110>})
    
    SeasonNum = '3'
    SeasonNum2set = '1'
    seaso = media.seasons[SeasonNum]
    
    import os
    import Media , Stack
    
    showTitle = media.title
    episodeTitle = ''
    s_num = SeasonNum2set
    
    
    for ep_num in media.seasons[SeasonNum].episodes:
      # now we create the Media.Episode object representing this episode
      # Media.Episode(showTitle, s_num, ep_num, episodeTitle, year) 
      epFiles = []
      tv_show = Media.Episode(showTitle, s_num, ep_num, episodeTitle, None) 
      tv_show.display_offset = 0  # need to handle mutliple recordings for the same physical show i.e. -0.mpg, -1.mpg, -2.mpg
      ep = media.seasons[SeasonNum].episodes[ep_num]
      # inspect_obj(ep)
      # inspect_obj(ep_num)
      for it in ep.items:
        #inspect_obj(it)

        for pt in it.parts:
          inspect_obj(pt)
          # see inspect_obj(media.seasons['3'].episodes[1].items[0].parts[0])
          tv_show.parts.append(pt.file)
          pass
        pass
      pass
      
      
      
      
    # file = os.path.basename(i)
  
    # tmp = media.seasons.pop(SeasonOld)
    # media.seasons.update({ Season2set : tmp })
    # media.seasons[Season2set].index = Season2set
    
    # ('title', u'\u041c\u0435\u0434\u043b\u0435\u043d\u043d\u044b\u0435 \u043b\u043e\u0448\u0430\u0434\u0438/Slow Horses [\u0412\u0435\u043b\u0438\u043a\u043e\u0431\u0440\u0438\u0442\u0430\u043d\u0438\u044f,..] \u0434\u0435\u0442\u0435\u043a\u0442\u0438\u0432')
    # ('seasons', {'3': <Framework.api.agentkit.MediaTree object at 0x00000000046bb190>})

    # shouldStack = True
    # import Stack, Media
    # #show - наименование, the_season - int сезон, the_episode - int эпизод, None, year - год)
    # tv_show = Media.Episode(show, the_season, the_episode, None, year)
    #   tv_show.parts.append(i)
    #   mediaList.append(tv_show)
              
    # # Stack the results.
    # if shouldStack:
    #   Stack.Scan(path, files, mediaList, subdirs)
    
    # return
    # load_episodes(metadata, media, Season2set)
    # -----------------------------
    
    '''  
    HaveToken = APItokenRemains()
    if not HaveToken:
      w(u">>>UPDATE STOPPED: has no valid key or not remains daily attempts")                  # type: ignore
      return
    d("Start plugin tokenQuota: %s" % (HaveToken))
    
    # # если Prefs["showSerialSeasons"]: восстановить (id, seasonNum)
    # Season2set = ''
    # if Prefs["showSerialSeasons"]:                      # type: ignore
    #   # Восстановить metadata.id
    #   RealId, Season2set = resurrectMetadataId(metadata.id)
    #   media.guid = 'com.plexapp.plugins.kinopoisk3://%s?lang=ru' % RealId
    #   d('Guid: %s' %  media.guid)      # type: ignore
    #   # восстановить metadata.id
    #   metadata.id = RealId

    #   # -----------------------------------------------------
    #
    Guids = getGUIDs(media.guid)
    if not Guids['kpId']:
      media.guid = media.guid + '&kp' + metadata.id
    try:
      y = metadata.year 
    except:
      y = UNKNOWN_YEAR
    Log("metadata-metadata title: %s y:%s" % (metadata.title, y)) # type: ignore
    # 

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
      def upd_meta(metadata=metadata, media=media):
        load_metadata(metadata, media, valid_poster0)
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
    if len(valid_names) > 0:
      media.thumb = valid_names[0]
    d(" ************* KinoPoiskUnnoficialAgent serial.UPDATE.end\n")
  


# ========================================================================


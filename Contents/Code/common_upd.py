# -*- coding: utf-8 -*-
# coding=utf-8
import re, datetime
import requests             # [а к нему еще chardet, urllib3, certifi, idna]      # type: ignore 

from config import API_BASE_URL, FILM_DETAILS, FILM_DISTRIBUTION, FILM_POSTERS, FILM_REVIEW, FILM_STAFF, SERIAL_SEASONS
from debug import d, w, log_timing
from utils import get_json, getGUIDs


@log_timing  
def load_metadata(metadata, media, valid_names):
  #
  d("-------------------update:load_metadata id=%s title=%s" % (metadata.id, metadata.title))
  #msStart = getMilliseconds(Datetime.Now())
  isAgentMovies = False if hasattr(metadata, 'seasons') else True
  
  movie_data = get_json(API_BASE_URL + FILM_DETAILS % metadata.id)
  if not movie_data or not metadata.id:
    return
  
  # добавить   "imdbId": "tt0379786",
  # now media.guid like :kp722886:
  Guids = getGUIDs(media.guid)
  if not Guids['imdbId']:
    if movie_data.get('imdbId'):
        imdbIdguid = movie_data.get('imdbId')
        if imdbIdguid:
          media.guid = media.guid + imdbIdguid
  Log(getGUIDs(media.guid))    # type: ignore
  '''
  "Guid": [{"id": "imdb://tt0499549"},
           {"id": "tmdb://19995"},
           {"id": "tvdb://165"}]
  '''

  #   title                     = Template.String()
  repls = (u' (видео)', u' (ТВ)', u' (мини-сериал)', u' (сериал)')
  title = reduce(lambda a, kv: a.replace(kv, ''), repls, movie_data.get('nameRu')) # type: ignore
  metadata.title = title

  if isAgentMovies:
    #   year                      = Template.Integer()
    if movie_data.get('year'):
      metadata.year = int(movie_data.get('year'))
    else:
      metadata.year = ''
    if metadata.year == 0:
      metadata.year = ''
    
    #   originally_available_at   = Template.Date()   A dateobject specifying the movie’s original release date.
    #   tagline                   = Template.String()
    metadata.tagline = movie_data.get('slogan')
    
  #   summary                   = Template.String()
  summary_add = ''
  # "Описание: отображать слоган фильма"
  if Prefs['desc_show_slogan']: # type: ignore
    val = movie_data.get('shortDescription')
    if val:
      summary_add += "%s\n" % val
      d(u"   Девиз = %s" % summary_add)
  #  "Описание: отображать рейтинг Кинопоиск"
  if Prefs['desc_rating_kp']: # type: ignore
    val = movie_data.get('ratingKinopoisk')
    if val:
      summary_add += u'КиноПоиск: %s' % val
      val1 = movie_data.get('ratingKinopoiskVoteCount')
      if val1:
        summary_add += ' (%s)' % val1
      d(u"   'КиноПоиск: %s(%s) " % (val, val1))
      summary_add += '\n'
  # "Описание: отображать рейтинг IMDB"
  if Prefs['desc_rating_imdb']: # type: ignore
    val = movie_data.get('ratingImdb')
    if val:
      summary_add += u'IMDB: %s' % val
      val1 = movie_data.get('ratingImdbVoteCount')
      if val1:
        summary_add += ' (%s)' % val1
      summary_add += '\n'
  #
  try:
    summary_add += movie_data.get('description')
  except:  pass
  #[Feature request] ссылка на инфо о фильме на кинопоиск #32
  if Prefs['desc_add_links']: # type: ignore
    summary_add += "\n" + movie_data.get('webUrl') + "\n"
    if movie_data.get('imdbId'):
      summary_add += 'https://www.imdb.com/title/' + movie_data.get('imdbId') + '/'
  # Всё, что сложилось - в описание
  metadata.summary = summary_add
  
  ## rating     A float between 0 and 10 specifying the movie’s rating.
  metadata.rating = 0.0
  try:
    metadata.rating = float(movie_data.get('ratingImdb'))
  except:  pass
  if metadata.rating == 0:
    try:
      metadata.rating = float('ratingKinopoisk')
    except:  pass 
  '''
  "Rating": [
          {
            "image": "imdb://image.rating",
            "type": "audience",
            "value": 7.9
          },
          {
            "image": "rottentomatoes://image.rating.ripe",
            "type": "critic",
            "value": 8.1
          },
          {
            "image": "rottentomatoes://image.rating.upright",
            "type": "audience",
            "value": 8.2
          },
          {
            "image": "themoviedb://image.rating",
            "type": "audience",
            "value": 7.582
          }
        ]
  '''


  #   trivia                    = Template.String()   A string containing trivia about the movie.
  #   quotes                    = Template.String()
  #   content_rating            = Template.String()
  val = movie_data.get('ratingMpaa')
  if val:
    metadata.content_rating = val.upper()
  else:
    val = movie_data.get('ratingAgeLimits')
    metadata.content_rating = val
  #   content_rating_age        = Template.Integer()
  try:
    metadata.content_rating_age = int(movie_data.get('ratingAgeLimits').replace('age', '') or 0)
  except:  pass
  #   countries                 = Template.Set(Template.String())
  countries = []
  for country in movie_data.get('countries'):
    countries.append(country.get('country'))
  metadata.countries = countries
  
  #   chapters                  = Template.Set(Chapter()) 
  ##  original_title       A string specifying the movie’s original title.
  val = movie_data.get('nameOriginal') 
  metadata.original_title = val if val else movie_data.get('nameEn')
  
  ## genres        A set of strings specifying the movie’s genre  
  genres = []
  for genre in movie_data.get('genres'):
      genres.append(genre.get('genre'))
  metadata.genres = genres       
  
  ## posters     A container of proxy objects representing the movie’s posters. See below for information about proxy objects.
  
  try:
    d("   === load meta start posterUrlPreview %s" % movie_data.get('posterUrlPreview'))
    #c "c:\Users\plugo\AppData\Local\Plex Media Server\Plug-ins\MoviePosterDB.bundle\Contents\Code\__init__.py" 
    image_url = movie_data.get('posterUrl')
    thumb_url = movie_data.get('posterUrlPreview')
    #metadata.posters[image_url] = Proxy.Preview(HTTP.Request(thumb_url), sort_order=0)
    metadata.posters[image_url] = Proxy.Preview(requests.get(thumb_url).content, sort_order=0) # type: ignore
    valid_names.append(image_url)
    #metadata.posters.validate_keys(valid_names)  #только после ВСЕХ posters
  except:    pass
  # d("===================update:load_meta end, Duration=%s\n"  % (getMilliseconds(Datetime.Now()) - msStart))
  ## themes    A container of proxy objects representing the movie’s theme music. 


@log_timing
def load_episodes(metadata, media):
  seasons_json = get_json(API_BASE_URL + SERIAL_SEASONS % metadata.id)
  #seasons_json = get_json(API_BASE_URL + SERIAL_SEASONS % 464963)   # 464963 - Игра престолов
  if not seasons_json:
    return
  if 'message' in seasons_json:
    d(u"\nsrch_and_score: Попытка поиска без ключа. %s" % seasons_json["message"])
    return
  #seasons_qty = seasons_json.get('total')
  for season_num, season_data in enumerate(seasons_json.get('items'), 1):    # 1,2...
    if season_num not in media.seasons:      
      continue
    # отлично, есть локальные файлы из сезонов из найденного сезона
    for episode_num, episode_data in enumerate(season_data.get('episodes'), 1):
      # по каждой серии
      s_num = episode_data.get('seasonNumber')
      e_num = episode_data.get('episodeNumber')
      episode = metadata.seasons[s_num].episodes[e_num]
      episode.title = ''
      episode.originally_available_at = None
      episode.summary = ''
      #
      title = episode_data.get('nameRu') 
      if not title:
        title = ''
      titleE = episode_data.get('nameEn')
      if not titleE:
        titleE = ''
      else:
        if title:
          title = title + ' / '
      episode.title = title + titleE
      dat = episode_data.get('releaseDate')
      if dat:
        episode.originally_available_at = datetime.datetime.strptime(dat, "%Y-%m-%d").date()
      episode.summary = episode_data.get('synopsis')
      d("%s:%s %s  %s" % (season_num, episode_num, dat, episode.title))

    
@log_timing  
def load_distribution(metadata):
  #https://www.kinopoisk.ru/film/5405057/studio/
  # d("-------------------update:load_distribution - start")
  ## msStart = getMilliseconds(Datetime.Now())
  movie_data = get_json(API_BASE_URL + FILM_DISTRIBUTION % metadata.id).get('items')
  if not movie_data:
    return
  #[ LOCAL, COUNTRY_SPECIFIC, PREMIERE, ALL, WORLD_PREMIER ], subType : [ CINEMA, DVD, DIGITAL, BLURAY ] 
  for data in movie_data:
    if data.get('type') == 'ALL':
      metadata.originally_available_at = Datetime.ParseDate((data.get('date')).replace('00.', '01.'), '%Y-%m-%d').date()  # type: ignore
      #   studio                    = Template.String() A string specifying the movie’s studio.
      for comp in data.get('companies'):
        metadata.studio = comp.get('name')  # so, only last like highlander  1981-12-02  Studio updated
  # d("===================update:load_distribution end, Duration=%s\n"  % (getMilliseconds(Datetime.Now()) - msStart))
    
  
#@log_timing  
def load_staff(metadata):
  ''' - штат - актеры, сценаристы, режиссер '''
  #d("-------------------update:load_staff - start")
  #msStart = getMilliseconds(Datetime.Now())  # '2025-01-25 12:41:53.921000' 
  isAgentMovies = False if hasattr(metadata, 'seasons') else True
  staff_data = get_json(API_BASE_URL + FILM_STAFF % metadata.id)
  if not staff_data:
    return
  # d("%s" % staff_data) # там сразу массив, без ключа
  # professionKey = [ WRITER, OPERATOR, EDITOR, COMPOSER, PRODUCER_USSR, HIMSELF, HERSELF, 
  # HRONO_TITR_MALE, HRONO_TITR_FEMALE, TRANSLATOR, DIRECTOR, DESIGN, PRODUCER, ACTOR, VOICE_DIRECTOR, UNKNOWN ]
  #   writers                   = Template.Set(Person())
  #   directors                 = Template.Set(Person())
  #   producers                 = Template.Set(Person())
  #   roles                     = Template.Set(Person())    TV_Show - only role
  
  @parallelize  # type: ignore
  def upd_staff():
    if isAgentMovies:
      metadata.directors.clear()
      metadata.producers.clear()
      metadata.writers.clear()
    metadata.roles.clear()
    for member in staff_data:
      #
      @task # type: ignore
      def upd_member(metadata = metadata,
                     member = member):
        prof = member.get('professionKey')
        name = member.get('nameRu') if member.get('nameRu') else member.get('nameEn')
        url = member.get('posterUrl')
        role_description = member.get('description')
        if prof == 'DIRECTOR' and isAgentMovies:
          if name:
            director = metadata.directors.new()
            director.name = name
            if url:
              director.photo = url
        if prof == 'PRODUCER' and isAgentMovies:
          if name:
            producer = metadata.producers.new()
            producer.name = name
            if url:
              producer.photo = url
        if prof == 'WRITER' and isAgentMovies:
          if name:
            writer = metadata.writers.new()
            writer.name = name
            if url:
              writer.photo = url
        if prof == 'ACTOR':
          if name and role_description:
            role = metadata.roles.new()
            role.name = name
            role.role = role_description
            if url:
              role.photo = url  
        #d("   staff %s = %s (%s)" % (prof, name, role_description))
  # d("===================update:load_staff end, Duration=%s\n"  % (getMilliseconds(Datetime.Now()) - msStart))
   
    
@log_timing   
def load_reviews(metadata):
  ''' обзоры с кинопоиска '''
  #d("-------------------update:load_reviews - start")
  #msStart = getMilliseconds(Datetime.Now())  # '2025-01-25 12:41:53.921000' 
  
  # Описание: загружать отзывы
  if not Prefs['desc_load_reviews']: # type: ignore
    d(u"Обзоры не загружать (настройка Описание: загружать отзывы = false)")
    metadata.reviews.clear()
    return

  reviews_dict = get_json(API_BASE_URL + FILM_REVIEW % metadata.id)
  if not reviews_dict:
    return            # нечего время терять
  @parallelize  # type: ignore
  def upd_reviews():
    metadata.reviews.clear()
    for item in reviews_dict.get('items'):
      @task # type: ignore
      def add_review(item = item,
                     metadata = metadata):
        author = u"%s +%s|-%s" % (item.get('author'), int(item.get('positiveRating')), int(item.get('negativeRating')))
        #author = u"%s +%s|-%s" % (item.get('author'), item.get_int('positiveRating'), item.get_int('negativeRating'))
        source = item.get('title') if item.get('title') else 'Кинопоиск'   # везде "Кинопоиск" - скучно, "title": "Королевский шпион, Часть 18.",
        text = re.sub(r'<("[^"]*"|\'[^\']*\'|[^\'">])*>', '', item.get('description'))   # вырезать теги
        text = re.sub(r'[\x00-\x08\x0b\x0c\x0e]', '', text)
        if author and source and text:
          review = metadata.reviews.new()
          review.author = author
          review.source = source
          review.image = 'rottentomatoes://image.review.rotten' if item.get('type') == "POSITIVE" else 'rottentomatoes://image.review.fresh'
          review.text = text
    ''' not used:
    "kinopoiskId": 1814200,
    "date": "2013-06-21T14:27:26",
  
  '''
  #d("===================update:load_reviews end, Duration=%s\n"  % (getMilliseconds(Datetime.Now()) - msStart))

  
@log_timing  
def load_gallery(metadata, valid_names, IsNeedPosters = True):
  ''' IsNeedPoster - постеры (false - artworks)
  metadata
  valid_names - массив проксимедиа с изображениями
  IsNeedPosters загружать постеры (иначе - обои)
  '''
  ## art       A container of proxy objects representing the movie’s background art. 
  def load_dict(type_artwork):
    '''   STILL - кадры
          SHOOTING - изображения со съемок
          POSTER - постеры
          FAN_ART - фан-арты
          PROMO - промо
          CONCEPT - концепт-арты
          WALLPAPER - обои
          COVER - обложки
          SCREENSHOT - скриншоты
    ''' 
    res = get_json(API_BASE_URL + FILM_POSTERS % (metadata.id, type_artwork))
    d("load_gallery:load_dict %s, finded [%s] results" % (type_artwork, res.get('total')))
    if not 'total' in res:
      res['total'] = 0
    return res
    
  if IsNeedPosters:    # posters - картинка на странице о фильме и в библиотеке
    art_dict = load_dict('POSTER') 
    if art_dict['total'] == 0:
      #тут нет постеров, ну вообще нет
      d("load_gallery: nothing %s finded")
      return
  else:               # грузим картинки для заднего фона страницы       
    art_dict = load_dict('WALLPAPER') 
    if art_dict['total'] == 0:
      art_dict = load_dict('COVER') 
      if art_dict['total'] == 0:
        art_dict = load_dict('PROMO')
        if art_dict['total'] == 0:
          art_dict = load_dict('STILL')
          if art_dict['total'] == 0:
            #тут рыбы нет, ну вообще нет
            d("load_gallery: nothing %s finded")
            return

  d("film='%s' id = %s, find total: %s" % (metadata.title, metadata.id, art_dict['total']))  
  #valid_names = []
  @parallelize   # type: ignore
  def upd_posters():
    pref_max = int(Prefs['poster_limit'])         # type: ignore
    max_posters = pref_max if pref_max else 30    # ну вот захардкодил 30 как 'очень много'
    for i, mov in enumerate(art_dict.get('items')):
      image_url = mov.get('imageUrl')
      thumb_url = mov.get('previewUrl')
      @task  # type: ignore # Create a task for updating poster
      def upd_poster( i=i, 
                      image_url=image_url, 
                      thumb_url=thumb_url, 
                      metadata=metadata,
                      valid_names=valid_names,
                      max_posters = max_posters):
        if i >= max_posters:
          #d("max posters = %s" % max_posters)
          return
        # d(" << @task:%02i:load_gallery:start %s  %s" % (i,('poster' if IsNeedPosters else 'art'), thumb_url))
        #metadata.posters[image_url] = Proxy.Preview(requests.get(thumb_url).content, sort_order = i+1)
        if IsNeedPosters:
          # sort_order=i+1 т.к. № 0 - в upd_metadata
          metadata.posters[image_url] = Proxy.Preview(requests.get(thumb_url).content, sort_order=i+1) # type: ignore
        else:
          # art or banners
          metadata.art[image_url] = Proxy.Preview(requests.get(thumb_url).content, sort_order=i) # type: ignore
        valid_names.append(image_url)
        # d(" ** @task:%02i:load_gallery:e  %s=%s" % (i,('poster' if IsNeedPosters else 'art'), thumb_url))
  '''
  # валидейт - все картинки привязывает в метадату. Надо за раз - и постеры и обои, при пересечении печаль
  if IsNeedPosters:
    metadata.posters.validate_keys(valid_names)
  else:
    metadata.art.validate_keys(valid_names)'''
  # d("\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! \n %s" % valid_names)


# coding=utf-8
from os.path import split as split_path
import shutil, time
from config import UPDATER_REPO, UPDATER_STABLE_URL, UPDATER_BETA_URL, UPDATER_ARCHIVE_URL, UPDATE_INTERVAL_MIN


class Updater(object):
  def __init__(self, core, channel, repo=UPDATER_REPO):
    Log("Updaterr:_init_ repo: %s" % repo)    # type: ignore
    self.core = core
    self.channel = channel
    self.repo = repo
    self.identifier = self.core.identifier
    self.stage = self.core.storage.data_item_path('Stage')
    self.stage_path = self.core.storage.join_path(self.stage, self.identifier)
    self.plugins_path = self.core.storage.join_path(self.core.app_support_path, 'Plug-ins')
    self.bundle_name = self.splitall(self.core.bundle_path)[-1]     #
    self.inactive = self.core.storage.data_item_path('Deactivated')
    self.inactive_path = self.core.storage.join_path(self.inactive, self.identifier)
    self.version_path = self.core.storage.join_path(self.core.bundle_path, 'Contents', 'VERSION')
    self.update_version = None
    self.stable_url = UPDATER_STABLE_URL % self.repo
    self.beta_url = UPDATER_BETA_URL % self.repo
    self.archive_url = UPDATER_ARCHIVE_URL % self.repo    
    Log("Updaterr:_init_ end, core: %s " % self.core)    # type: ignore
    
      
  @classmethod
  def auto_update_thread(cls, core, pref):
    Log("Updaterr:auto_update_thread:: chanel: %s." % pref['update_channel'])     # type: ignore
    # "c:\Program Files\Plex\Plex Media Server\Resources\Plug-ins-46083195d\Framework.bundle\Contents\Resources\Versions\2\Python\Framework\components\runtime.py" 
    try:
      core.log.debug("Updaterr:auto_update_thread:try")
      cls(core, pref['update_channel'], UPDATER_REPO).checker()
      core.storage.remove_data_item('error_update')
      #c:\Users\plugo\AppData\Local\Plex Media Server\Plug-in Support\Data\com.plexapp.plugins.kinopoisk3\DataItems\
    except Exception as e:
      core.storage.save_data_item('error_update', str(e))
      core.log.error("Updaterr:auto_update_thread::err %s." % str(e))     # type: ignore
    UpdateInterval = int(Prefs['update_interval'])      # type: ignore
    if UPDATE_INTERVAL_MIN > UpdateInterval:
      UpdateInterval = UPDATE_INTERVAL_MIN
    UpdateInterval = UpdateInterval * 60
    UpdateInterval = int(Prefs['update_interval'] or 1)*60       # type: ignore
    core.runtime.create_timer(UpdateInterval, Updater.auto_update_thread, True, core.sandbox, True, core=core, pref=pref)
        
  
  def checker(self):
    ''' Проверка необходимости обновления
      - self.channel = [ none, stable, beta], none - никаких действий
      - stable - ver from GH последний стабильный релиз получить тег: "name": "v1.6.0"
          https://api.github.com/repos/lugovskovp/Kinopoisk3.bundle/releases/latest
      - beta - ver from GH - самый-самый последний тег релиза из в т.ч. и prereleases "name": "v1.6.1-beta.5"
          https://api.github.com/repos/lugovskovp/Kinopoisk3.bundle/tags?per_page=1
      
    '''
    self.core.log.debug('Updater:checker')  
    if self.channel != 'none': 
      Log('Updater:checker: Check for %s channel updates' % self.channel)   # type: ignore
      url = getattr(self, '%s_url' % self.channel)
      req = self.core.networking.http_request(url)
      if req:
        git_data = self.core.data.json.from_string(req.content)
        try:
          if self.channel == 'beta':                                #stable - obj, beta - [obj]
            self.update_version = reduce(dict.get, {'name'}, git_data[0])     # type: ignore
          else:
            self.update_version = reduce(dict.get, {'name'}, git_data)     # type: ignore
          if not self.update_version:
            self.core.log.debug('Updater checker: Unsuccessful trying get tag info for channel %s' % self.channel)
            return
          elif self.channel == 'stable':
            self.core.log.debug(u'Updater:checker: Github version for channel %s = %s' % (self.channel, self.update_version))     # type: ignore
            current_version = ''
            if self.core.storage.file_exists(self.version_path):
              current_version = self.core.storage.load(self.version_path)
              current_version = str.split(current_version)[0]
              self.core.log.debug(u'Updater:checker: Current actual version "%s" vs "%s"' % (current_version, self.update_version))
            if current_version == self.update_version:
                self.core.log.debug('Updater:checker: Current version is actual')
                return
            self.install_zip_from_url(self.archive_url + self.update_version + ".zip")  
            return
          else: pass
        except Exception as e:
          self.core.log.error('Updater:checker: Something goes wrong with updater: %s', e, exc_info=True)
          raise
  
  
  @property
  def setup_stage(self):
    self.core.log.debug(u"Updater:setup_stage Setting up staging area for {} at \n{}".format(self.identifier, self.stage_path))
    #C:\Users\plugo\AppData\Local\Plex Media Server\Plug-in Support\Data\com.plexapp.plugins.kinopoisk3\DataItems\Stage\com.plexapp.plugins.kinopoisk3
    self.core.storage.remove_tree(self.stage_path)
    self.core.storage.make_dirs(self.stage_path)
    return self.stage_path
  
  
  def cleanup(self):
    if self.core.storage.dir_exists(self.inactive_path):
      self.core.log.debug(u"Updater:cleanup Cleaning up after {} (removing {})".format(self.identifier, self.inactive_path))
      self.core.storage.remove_tree(self.inactive_path)
            
  
  def unstage(self):
    self.core.log.debug(u"Updater: Unstaging files for {} (removing {})".format(self.identifier, self.stage_path))
    self.core.storage.remove_tree(self.stage_path)


  def splitall(self, path):
    allparts = list()
    while True:
      parts = split_path(path)
      if parts[0] == path:  # sentinel for absolute paths
        allparts.insert(0, parts[0])
        break
      elif parts[1] == path: # sentinel for relative paths
        allparts.insert(0, parts[1])
        break
      else:
        path = parts[0]
        allparts.insert(0, parts[1])
    return allparts
     
      
  def install_zip_from_url(self, url):
    stage_path = self.setup_stage 
    self.core.log.debug(u"Updater:install_zip_from_url Path=\n%s\n%s" % (stage_path, url))
    try:
      archive = self.core.data.archiving.zip_archive(self.core.networking.http_request(url).content)
    except:
      self.core.log.debug(u"Updater:install_zip_from_url Unable to download archive for {}".format(self.identifier))
      self.unstage()
      return False
    if archive.Test() != None:
      self.core.log.debug(u"Updater:install_zip_from_url The archive of {} is invalid - unable to continue".format(self.identifier))
      self.unstage()
      return False
    try:
      for archive_name in archive:
        parts = archive_name.split('/')[1:]

        if parts[0] == '' and len(parts) > 1:
          parts = parts[1:]

        if len(parts) > 1 and parts[0] == 'Contents' and len(parts[-1]) > 0 and parts[-1][0] != '.':
          file_path = self.core.storage.join_path(stage_path, *parts)
          dir_path = self.core.storage.join_path(stage_path, *parts[:-1])

          if not self.core.storage.dir_exists(dir_path):
            self.core.storage.make_dirs(dir_path)
          self.core.storage.save(file_path, archive[archive_name])
          self.core.log.debug(u"install_zip_from_url: Extracted {} to {} for {}".format(parts[-1], dir_path, self.identifier))
        else:
          self.core.log.debug(U"install_zip_from_url: Not extracting {}".format(archive_name))

      version_file_path = self.core.storage.join_path(stage_path, 'Contents', 'VERSION')
      if not self.core.storage.file_exists(version_file_path):
        self.core.storage.save(version_file_path, self.update_version)
    except:
      self.core.log.error(u"install_zip_from_url: Error extracting archive of {}".format(self.identifier), exc_info=True)
      self.unstage()
      return False

    finally:
      archive.Close()
      
    plist_path = self.core.storage.join_path(stage_path, 'Contents', 'Info.plist')
    plist_data = self.core.storage.load(plist_path, binary=False)
    plist_data = plist_data.replace('{{version}}', self.update_version)
    Logs_path = self.core.storage.join_path(self.core.app_support_path, 'Logs', 'PMS Plugin Logs')
    plist_data = plist_data.replace('{{logs}}', Logs_path)
    self.core.log.debug(plist_data)
    self.core.storage.save(plist_path, plist_data, binary=False)
    
    self.deactivate()
    if not self.activate():
      self.core.log.error(u"Updater:install_zip_from_url Unable to activate {}".format(self.identifier), exc_info=True)
      self.reactivate()
      self.unstage()
      return False

    try:
      self.core.storage.utime(self.core.plist_path, None)
    except:
      self.core.log.error(u"Updater:install_zip_from_url Error with utime function", exc_info=True)

    self.unstage()
    self.cleanup()
    self.core.log.log(u"!!!\nUpdater: update to version %s successful ended" % self.update_version)
    
    return True
    
    
    
  def reactivate(self):
    try:
      self.core.log.debug(u"Updater:reactivate Reactivating the old installation of %s (moving from %s)" % (self.identifier, self.inactive_path))
      self.core.storage.rename(self.inactive_path, self.core.storage.join_path(self.plugins_path, self.bundle_name))
    except:
      self.core.log.exception(u"Updater:reactivate Unable to reactivate the old installation of %s", self.identifier)


  def deactivate(self):
    self.core.log.debug(u"Updater:deactivate Deactivating an old installation of %s (moving to %s)" % (self.identifier, self.inactive_path))
    self.cleanup()
    self.core.storage.make_dirs(self.inactive_path)
    self.core.storage.rename(self.core.storage.join_path(self.plugins_path, self.bundle_name), self.inactive_path)


  def activate(self, fail_count=0):
    final_path = self.core.storage.join_path(self.plugins_path, self.bundle_name)

    if not self.core.storage.dir_exists(self.stage_path):
        self.core.log.debug(u"Updater:activate Unable to find stage for {}".format(self.identifier))
        return False

    self.core.log.debug(u"Updater:activate Activating a new installation of {}".format(self.identifier))
    try:
        if not self.core.storage.dir_exists(final_path):
            self.core.storage.rename(self.stage_path, final_path)
        else:
            self.copytree(self.stage_path, final_path)
    except:
        self.core.log.exception(u"Updater:activate Unable to activate {} at {}".format(self.identifier, final_path))
        if fail_count < 5:
            self.core.log.info(u"Updater:activate Waiting 2s and trying again")
            time.sleep(2)                               # type: ignore
            return self.activate(fail_count + 1)
        else:
            self.core.log.info(u"Updater:activate Too many failures - returning")
            return False
    return True
  
  
  def copytree(self, src, dst):
    if not self.core.storage.file_exists(dst):
      self.core.log.debug(u"Updater:copytree reating dir at '{}'".format(dst))
      self.core.storage.make_dirs(dst)
    self.core.log.debug(u"Updater:copytree copying contents of '{}' into '{}'".format(src, dst))
    for item in self.core.storage.list_dir(src):
      s = self.core.storage.join_path(src, item)
      d = self.core.storage.join_path(dst, item)
      if self.core.storage.dir_exists(s):
        self.core.log.debug(u"Updater:copytree Copying '{}' into '{}'".format(s, d))
        self.copytree(s, d)
      else:
        self.core.log.debug(u"Updater:copytree Copying with copy2 '{}' into '{}'".format(s, d))
        try:
          shutil.copy2(s, d)
        except IOError as err:
          self.core.log.error(u'Updater:copytree Something wrong while file copy %s', err, exc_info=True)
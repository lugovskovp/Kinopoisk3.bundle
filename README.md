# Кинопоиск3 - плагин для Plex
<!-- https://shields.io/badges/git-hub-release -->
![CI][release-image]
[![][version-image]][changelog-url]
[![Release date][release-date-image]][release-url]
[![][version-beta-image]][changelog-url]
[![][license-image]][license-url]


# Зачем.
Искренняя благодарность Artem Mirotin aka @amirotin, Aleksey Ganuta aka @ziemenz и @Jenstel и Vladimir Sharapov aka @EvelRus, которые являются авторами плагина для Plex Media Server (PMS) [Kinopoisk.bundle](https://github.com/Jenstel/Kinopoisk.bundle)
Увы, последнее обновление которого - март 2021, и изменения в API сделали этот плагин малопригодным для использования.
В данной реализации, архитектурно значительно более простой, и рассчитанной только на работу с Кинопоиском, удалось добавить некоторые фишки, отсутствующие в оригинальном Kinopoisk.bundle. При этом, очень многое взято из оригинального.

# Установка
Исходим из того, что [Plex Media Server|https://www.plex.tv/media-server-downloads/?cat=computer&plat=windows] для вашей операционной системы уже установлен.
Иначе зачем мог понадобиться плагин к нему.

## Latest версия
Скачать актуальную версию [Kinopoisk3.bundle|https://github.com/lugovskovp/Kinopoisk3.bundle/releases/latest].
Плагин в активной доработке, подэтому в настройках (см.ниже) рекомендую включить автообновление.

## Распаковка в папку плагинов
Расположение папки плагинов Plex (папки Plug-ins) в разных операционных системах:
* '%LOCALAPPDATA%\Plex Media Server\'                                        # Windows Vista/7/8
* '%USERPROFILE%\Local Settings\Application Data\Plex Media Server\'         # Windows XP, 2003, Home Server
* '$HOME/Library/Application Support/Plex Media Server/'                     # Mac OS
* '$PLEX_HOME/Library/Application Support/Plex Media Server/',               # Linux
* '/var/lib/plexmediaserver/Library/Application Support/Plex Media Server/', # Debian,Fedora,CentOS,Ubuntu
* '/usr/local/plexdata/Plex Media Server/',                                  # FreeBSD
* '/usr/pbi/plexmediaserver-amd64/plexdata/Plex Media Server/',              # FreeNAS
* '${JAIL_ROOT}/var/db/plexdata/Plex Media Server/',                         # FreeNAS
* '/c/.plex/Library/Application Support/Plex Media Server/',                 # ReadyNAS
* '/share/MD0_DATA/.qpkg/PlexMediaServer/Library/Plex Media Server/',        # QNAP
* '/volume1/Plex/Library/Application Support/Plex Media Server/',            # Synology, Asustor
* '/raid0/data/module/Plex/sys/Plex Media Server/',                          # Thecus
* '/raid0/data/PLEX_CONFIG/Plex Media Server/'                               # Thecus Plex community
* '/Volume1/Plex/Library/Application Support/Plex Media Server'              # TOS 5.0 | TOS 6.0


# Использование
## Преимущества

## Настройки

## Пожелания к доработке
Если есть пожелания к доработке какой-то функции, или необходимо сообщить о проблеме - достаточно завести тикет на странице проекта:

## Changelog
See [CHANGELOG][changelog-url].

## License
This project is released under the [MIT License][license-url].

<!-- Links: -->
[release-url]: https://github.com/lugovskovp/Kinopoisk3.bundle
[changelog-url]: https://github.com/lugovskovp/Kinopoisk3.bundle/blob/master/CHANGELOG.md

[release-image]: https://github.com/lugovskovp/Kinopoisk3.bundle/actions/workflows/release.yml/badge.svg?branch=master
[release-url]: https://github.com/lugovskovp/Kinopoisk3.bundle/actions/workflows/release.yml

[version-image]: https://img.shields.io/github/v/release/lugovskovp/Kinopoisk3.bundle
[version-beta-image]: https://img.shields.io/github/v/release/lugovskovp/Kinopoisk3.bundle?include_prereleases
[release-date-image]: https://img.shields.io/github/release-date/lugovskovp/Kinopoisk3.bundle

[license-url]: https://github.com/lugovskovp/Kinopoisk3.bundle/blob/main/LICENSE
[license-image]: https://img.shields.io/github/license/lugovskovp/Kinopoisk3.bundle



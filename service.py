# -*- coding: utf-8 -*-

import os
import re
import sys
import xbmc
import xbmcaddon
import xbmcgui,xbmcplugin
import xbmcvfs
import shutil

import uuid

if sys.version_info[0] == 2:
    p2 = True
else:
    unicode = str
    p2 = False

from resources.lib.dualsubs import mergesubs

__addon__ = xbmcaddon.Addon()
__author__     = __addon__.getAddonInfo('author')
__scriptid__   = __addon__.getAddonInfo('id')
__scriptname__ = __addon__.getAddonInfo('name')
__version__    = __addon__.getAddonInfo('version')
__language__   = __addon__.getLocalizedString

LANGUAGE_CODE_REGEX = re.compile(r'\(([a-z]{2})\)\s*$', re.IGNORECASE)

try:
    translatePath = xbmcvfs.translatePath
except AttributeError:
    translatePath = xbmc.translatePath

__cwd__        = translatePath( __addon__.getAddonInfo('path') )
if p2:
    __cwd__ = __cwd__.decode("utf-8")

__resource__   = translatePath( os.path.join( __cwd__, 'resources', 'lib' ) )
if p2:
    __resource__ = __resource__.decode("utf-8")

__profile__    = translatePath( __addon__.getAddonInfo('profile') )
if p2:
    __profile__ = __profile__.decode("utf-8")

__temp__       = translatePath( os.path.join( __profile__, 'temp', '') )
if p2:
    __temp__ = __temp__.decode("utf-8")

if xbmcvfs.exists(__temp__):
  shutil.rmtree(__temp__)
xbmcvfs.mkdirs(__temp__)

__msg_box__       = xbmcgui.Dialog()

__subtitlepath__  = translatePath("special://subtitles")

if __subtitlepath__ is None:
  __subtitlepath__ = ""

sys.path.append (__resource__)

# Make sure the manual search button is disabled
try:
  if xbmc.getCondVisibility("Window.IsActive(subtitlesearch)"):
      window = xbmcgui.Window(10153)
      window.getControl(160).setEnableCondition('!String.IsEqual(Control.GetLabel(100),"{}")'.format(__scriptname__))
except:
  #ignore
  window = ''

def AddItem(name, url):
  listitem = xbmcgui.ListItem(label          = "",
                              label2         = name
                             )

  listitem.setProperty( "sync", "false" )
  listitem.setProperty( "hearing_imp", "false" )

  xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=url,listitem=listitem,isFolder=False)


def Search():
  AddItem(__language__(33004), "plugin://%s/?action=browsedual" % (__scriptid__))
  AddItem(__language__(33008), "plugin://%s/?action=settings" % (__scriptid__))

def get_params(string=""):
  param={}
  if string == "":
    if len(sys.argv) > 2:
      paramstring=sys.argv[2]
    else:
      paramstring=""
  else:
    paramstring=string
  if len(paramstring)>=2:
    params=paramstring
    cleanedparams=params.replace('?','')
    if (params[len(params)-1]=='/'):
      params=params[0:len(params)-2]
    pairsofparams=cleanedparams.split('&')
    param={}
    for i in range(len(pairsofparams)):
      splitparams={}
      splitparams=pairsofparams[i].split('=')
      if (len(splitparams))==2:
        param[splitparams[0]]=splitparams[1]

  return param

params = get_params()

def unzip(zip, exts):
  filename = None
  for file in xbmcvfs.listdir(zip)[1]:
    file = os.path.join(__temp__, file)
    if (os.path.splitext( file )[1] in exts):
      filename = file
      break

  if filename != None:
    xbmc.executebuiltin('Extract("%s","%s")' % (zip,__temp__,), True)
  else:
    xbmc.executebuiltin((u'Notification(%s,%s)' % (__scriptname__ , __language__(33007))))
  return filename

def Download(filename):
  listitem = xbmcgui.ListItem(label=filename)
  xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=filename,listitem=listitem,isFolder=False)

def _is_disallowed_browse_path(path):
  if not path:
    return True

  lower = path.lower()
  return lower.startswith('plugin://') or lower.startswith('pvr://')

def _exists_dir(path):
  try:
    if xbmcvfs.exists(path):
      return True
  except:
    pass

  if path and not path.endswith('/'):
    try:
      if xbmcvfs.exists(path + '/'):
        return True
    except:
      pass

  return False

def _is_usable_browse_dir(path):
  if not path:
    return False

  if _is_disallowed_browse_path(path):
    return False

  return _exists_dir(path)

def _current_video_context():
  try:
    video_file = xbmc.Player().getPlayingFile()
  except:
    video_file = ''

  if not video_file:
    return '', ''

  if _is_disallowed_browse_path(video_file):
    return '', ''

  video_dir = os.path.dirname(video_file)
  if not _is_usable_browse_dir(video_dir):
    return '', ''

  video_name = os.path.splitext(os.path.basename(video_file))[0]
  return video_dir, video_name

def _resolve_start_dir(video_dir):
  if _is_usable_browse_dir(video_dir):
    return video_dir

  last_used = __addon__.getSetting('last_used_subtitle_dir')
  if _is_usable_browse_dir(last_used):
    return last_used

  if _is_usable_browse_dir(__subtitlepath__):
    return __subtitlepath__

  return ''

def _parse_language_code(setting_id):
  language_value = __addon__.getSetting(setting_id)
  if not language_value or language_value == 'Disabled':
    return None

  match = LANGUAGE_CODE_REGEX.search(language_value)
  if match is not None:
    return match.group(1).lower()

  language_value = language_value.strip().lower()
  if re.match(r'^[a-z]{2}$', language_value):
    return language_value

  return None

def _language_label(setting_id):
  language_value = __addon__.getSetting(setting_id)
  if not language_value or language_value == 'Disabled':
    return __language__(33018)
  return language_value

def _find_exact_subtitle_matches(video_dir, video_basename, language_code):
  if not video_dir or not video_basename or not language_code:
    return []

  try:
    files = xbmcvfs.listdir(video_dir)[1]
  except:
    return []

  expected = [
      ("%s.%s.srt" % (video_basename, language_code)).lower(),
      ("%s-%s.srt" % (video_basename, language_code)).lower(),
      ("%s_%s.srt" % (video_basename, language_code)).lower(),
  ]

  matches = []
  for subtitle_name in files:
    subtitle_name_lower = subtitle_name.lower()
    if subtitle_name_lower in expected:
      matches.append(os.path.join(video_dir, subtitle_name))

  return matches

def _auto_match_subtitles(video_dir, video_basename):
  result = {
      'mode': 'none',
      'subtitle1': None,
      'subtitle2': None,
      'found_label': '',
      'missing_label': '',
      'missing': '',
  }

  language1 = _parse_language_code('preferred_language_1')
  language2 = _parse_language_code('preferred_language_2')
  if not video_dir or not video_basename or not language1 or not language2 or language1 == language2:
    return result

  matches1 = _find_exact_subtitle_matches(video_dir, video_basename, language1)
  matches2 = _find_exact_subtitle_matches(video_dir, video_basename, language2)

  if len(matches1) == 1 and len(matches2) == 1 and matches1[0] != matches2[0]:
    result['mode'] = 'full'
    result['subtitle1'] = matches1[0]
    result['subtitle2'] = matches2[0]
    return result

  if len(matches1) == 1 and len(matches2) == 0:
    result['mode'] = 'partial'
    result['subtitle1'] = matches1[0]
    result['found_label'] = _language_label('preferred_language_1')
    result['missing_label'] = _language_label('preferred_language_2')
    result['missing'] = 'subtitle2'
    return result

  if len(matches1) == 0 and len(matches2) == 1:
    result['mode'] = 'partial'
    result['subtitle2'] = matches2[0]
    result['found_label'] = _language_label('preferred_language_2')
    result['missing_label'] = _language_label('preferred_language_1')
    result['missing'] = 'subtitle1'
    return result

  return result

def _browse_for_subtitle(title, browse_dir):
  if not _is_usable_browse_dir(browse_dir):
    browse_dir = ''

  while True:
    subtitlefile = __msg_box__.browse(1, title, "video", ".zip|.srt", False, False, browse_dir, False)
    if subtitlefile is None or subtitlefile == '' or subtitlefile == browse_dir:
      return None, browse_dir

    selected_dir = os.path.dirname(subtitlefile)
    if subtitlefile.lower().endswith('.zip'):
      extracted_file = unzip(subtitlefile, [ ".srt" ])
      if extracted_file is None:
        browse_dir = selected_dir
        continue
      return extracted_file, selected_dir

    return subtitlefile, selected_dir

def _remember_last_used_dir(path):
  if not _is_usable_browse_dir(path):
    return

  try:
    __addon__.setSetting('last_used_subtitle_dir', path)
  except:
    pass

def _prepare_and_merge_subtitles(subs):
  substemp=[]
  for sub in subs:
    # Python can fail to read subtitles from special Kodi locations (for example smb://).
    # Copy each selected subtitle to a local temporary file first.
    subtemp = os.path.join(__temp__, "%s" %(str(uuid.uuid4())))
    xbmcvfs.copy(sub, subtemp)
    substemp.append(subtemp)

  finalfile = mergesubs(substemp)

  for subtemp in substemp:
    xbmcvfs.delete(subtemp)

  return finalfile

def _run_dual_subtitle_flow():
  video_dir, video_basename = _current_video_context()
  start_dir = _resolve_start_dir(video_dir)

  subtitle1 = None
  subtitle2 = None
  subtitle1_dir = ''

  automatch = _auto_match_subtitles(video_dir, video_basename)
  if automatch['mode'] == 'full':
    subtitle1 = automatch['subtitle1']
    subtitle2 = automatch['subtitle2']
    subtitle1_dir = os.path.dirname(subtitle1)

  elif automatch['mode'] == 'partial':
    message = __language__(33014) % (automatch['found_label'], automatch['missing_label'])
    if __msg_box__.yesno(__scriptname__, message):
      if automatch['missing'] == 'subtitle2':
        subtitle1 = automatch['subtitle1']
        subtitle1_dir = os.path.dirname(subtitle1)
        title2 = __language__(33006) + ' ' + __language__(33009)
        subtitle2, _ = _browse_for_subtitle(title2, subtitle1_dir)
      else:
        subtitle2 = automatch['subtitle2']
        browse_dir = os.path.dirname(subtitle2)
        subtitle1, subtitle1_dir = _browse_for_subtitle(__language__(33005), browse_dir)

  if subtitle1 is None and subtitle2 is None:
    subtitle1, subtitle1_dir = _browse_for_subtitle(__language__(33005), start_dir)
    if subtitle1 is None:
      return

    title2 = __language__(33006) + ' ' + __language__(33009)
    subtitle2, _ = _browse_for_subtitle(title2, subtitle1_dir)

  if subtitle1 is None:
    return

  if not subtitle1_dir:
    subtitle1_dir = os.path.dirname(subtitle1)
  _remember_last_used_dir(subtitle1_dir)

  subs = [subtitle1]
  if subtitle2 is not None:
    subs.append(subtitle2)

  finalfile = _prepare_and_merge_subtitles(subs)
  Download(finalfile)

action = params.get('action', 'search')

if action == 'manualsearch':
  Search()

elif action == 'search':
  Search()

elif action == 'browsedual':
  _run_dual_subtitle_flow()

elif action == 'settings':
  __addon__.openSettings()
  __msg_box__.ok(__scriptname__, __language__(32530))

else:
  Search()

xbmcplugin.endOfDirectory(int(sys.argv[1]))

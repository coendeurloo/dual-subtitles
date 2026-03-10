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
NOTIFY_INFO = getattr(xbmcgui, 'NOTIFICATION_INFO', '')
NOTIFY_WARNING = getattr(xbmcgui, 'NOTIFICATION_WARNING', '')
NOTIFY_ERROR = getattr(xbmcgui, 'NOTIFICATION_ERROR', '')
LOG_DEBUG = getattr(xbmc, 'LOGDEBUG', 0)
LOG_INFO = getattr(xbmc, 'LOGINFO', getattr(xbmc, 'LOGNOTICE', 1))
LOG_WARNING = getattr(xbmc, 'LOGWARNING', 2)
LOG_ERROR = getattr(xbmc, 'LOGERROR', 4)

try:
    translatePath = xbmcvfs.translatePath
except AttributeError:
    translatePath = xbmc.translatePath

__cwd__        = translatePath(__addon__.getAddonInfo('path'))
if p2:
    __cwd__ = __cwd__.decode("utf-8")

__resource__   = translatePath(os.path.join(__cwd__, 'resources', 'lib'))
if p2:
    __resource__ = __resource__.decode("utf-8")

__profile__    = translatePath(__addon__.getAddonInfo('profile'))
if p2:
    __profile__ = __profile__.decode("utf-8")

__temp__       = translatePath(os.path.join(__profile__, 'temp', ''))
if p2:
    __temp__ = __temp__.decode("utf-8")

if xbmcvfs.exists(__temp__):
  shutil.rmtree(__temp__)
xbmcvfs.mkdirs(__temp__)

__msg_box__       = xbmcgui.Dialog()

__subtitlepath__  = translatePath("special://subtitles")
if __subtitlepath__ is None:
  __subtitlepath__ = ""

sys.path.append(__resource__)

# Make sure the manual search button is disabled
try:
  if xbmc.getCondVisibility("Window.IsActive(subtitlesearch)"):
      window = xbmcgui.Window(10153)
      window.getControl(160).setEnableCondition('!String.IsEqual(Control.GetLabel(100),"{}")'.format(__scriptname__))
except:
  window = ''

def AddItem(name, url):
  listitem = xbmcgui.ListItem(label="", label2=name)
  listitem.setProperty("sync", "false")
  listitem.setProperty("hearing_imp", "false")
  xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=url, listitem=listitem, isFolder=False)

def Search():
  AddItem(__language__(33004), "plugin://%s/?action=browsedual" % (__scriptid__))
  AddItem(__language__(33008), "plugin://%s/?action=settings" % (__scriptid__))

def get_params(string=""):
  param = {}
  if string == "":
    if len(sys.argv) > 2:
      paramstring = sys.argv[2]
    else:
      paramstring = ""
  else:
    paramstring = string
  if len(paramstring) >= 2:
    params = paramstring
    cleanedparams = params.replace('?', '')
    if params[len(params) - 1] == '/':
      params = params[0:len(params) - 2]
    pairsofparams = cleanedparams.split('&')
    param = {}
    for i in range(len(pairsofparams)):
      splitparams = {}
      splitparams = pairsofparams[i].split('=')
      if len(splitparams) == 2:
        param[splitparams[0]] = splitparams[1]

  return param

params = get_params()

def unzip(zip_path, exts):
  filename = None
  for file_name in xbmcvfs.listdir(zip_path)[1]:
    target = os.path.join(__temp__, file_name)
    if os.path.splitext(target)[1].lower() in exts:
      filename = target
      break

  if filename is not None:
    xbmc.executebuiltin('Extract("%s","%s")' % (zip_path, __temp__), True)
  else:
    _notify(__language__(33007), NOTIFY_WARNING)
  return filename

def Download(filename):
  listitem = xbmcgui.ListItem(label=filename)
  xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=filename, listitem=listitem, isFolder=False)

def _equal_text(setting_value, message_id):
  return setting_value == str(message_id) or setting_value == __language__(message_id)

def _notify(message, icon=NOTIFY_INFO, timeout=4000):
  try:
    __msg_box__.notification(__scriptname__, message, icon, timeout)
  except:
    try:
      xbmc.executebuiltin(u'Notification(%s,%s)' % (__scriptname__, message))
    except:
      pass

def _log(message, level=LOG_INFO):
  try:
    xbmc.log('[%s] %s' % (__scriptid__, message), level)
  except:
    pass

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

def _get_start_folder_priority():
  setting = __addon__.getSetting('start_folder_priority')
  if _equal_text(setting, 33034):
    return 'last_used_first'
  return 'video_first'

def _get_no_match_behavior():
  setting = __addon__.getSetting('no_match_behavior')
  if _equal_text(setting, 33023):
    return 'first_only'
  if _equal_text(setting, 33024):
    return 'stop'
  return 'manual_both'

def _get_partial_match_behavior():
  setting = __addon__.getSetting('partial_match_behavior')
  if _equal_text(setting, 33026):
    return 'auto_use'
  if _equal_text(setting, 33027):
    return 'manual_both'
  return 'ask'

def _get_match_strictness():
  setting = __addon__.getSetting('match_strictness')
  if _equal_text(setting, 33031):
    return 'relaxed'
  return 'strict'

def _is_second_subtitle_required():
  return __addon__.getSetting('second_subtitle_required') == 'true'

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
  last_used = __addon__.getSetting('last_used_subtitle_dir')
  if _get_start_folder_priority() == 'last_used_first':
    candidates = [last_used, video_dir, __subtitlepath__]
  else:
    candidates = [video_dir, last_used, __subtitlepath__]

  for candidate in candidates:
    if _is_usable_browse_dir(candidate):
      return candidate
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

def _match_subtitle_name(subtitle_name, video_basename, language_code, strict):
  name_lower = subtitle_name.lower()
  base_lower = video_basename.lower()
  lang_lower = language_code.lower()

  if not name_lower.endswith('.srt'):
    return False
  if not name_lower.startswith(base_lower):
    return False

  name_without_ext = subtitle_name[:-4]
  if len(name_without_ext) <= len(video_basename):
    return False

  tail = name_without_ext[len(video_basename):]
  if not tail:
    return False
  if tail[0] not in ['.', '-', '_']:
    return False

  tail_lower = tail.lower()
  suffixes = ['.%s' % (lang_lower), '-%s' % (lang_lower), '_%s' % (lang_lower)]
  if strict:
    return tail_lower in suffixes

  for suffix in suffixes:
    if tail_lower.endswith(suffix):
      return True
  return False

def _find_subtitle_matches(video_dir, video_basename, language_code, strict):
  if not video_dir or not video_basename or not language_code:
    return []

  try:
    files = xbmcvfs.listdir(video_dir)[1]
  except:
    return []

  matches = []
  seen = {}
  for subtitle_name in files:
    if _match_subtitle_name(subtitle_name, video_basename, language_code, strict):
      full_path = os.path.join(video_dir, subtitle_name)
      lower_key = full_path.lower()
      if lower_key not in seen:
        seen[lower_key] = True
        matches.append(full_path)

  return matches

def _auto_match_subtitles(video_dir, video_basename):
  result = {
      'mode': 'disabled',
      'subtitle1': None,
      'subtitle2': None,
      'found_label': '',
      'missing_label': '',
      'missing': '',
      'language1_label': _language_label('preferred_language_1'),
      'language2_label': _language_label('preferred_language_2'),
  }

  language1 = _parse_language_code('preferred_language_1')
  language2 = _parse_language_code('preferred_language_2')
  if not video_dir or not video_basename or not language1 or not language2 or language1 == language2:
    _log('auto-match disabled: video_dir=%s base=%s lang1=%s lang2=%s' % (video_dir, video_basename, language1, language2), LOG_DEBUG)
    return result

  strict = _get_match_strictness() == 'strict'
  matches1 = _find_subtitle_matches(video_dir, video_basename, language1, strict)
  matches2 = _find_subtitle_matches(video_dir, video_basename, language2, strict)
  _log('auto-match candidates: strict=%s lang1=%s count1=%d lang2=%s count2=%d' % (strict, language1, len(matches1), language2, len(matches2)), LOG_DEBUG)

  if len(matches1) == 1 and len(matches2) == 1 and matches1[0] != matches2[0]:
    result['mode'] = 'full'
    result['subtitle1'] = matches1[0]
    result['subtitle2'] = matches2[0]
    _log('auto-match full: %s | %s' % (result['subtitle1'], result['subtitle2']), LOG_INFO)
    return result

  if len(matches1) == 1 and len(matches2) == 0:
    result['mode'] = 'partial'
    result['subtitle1'] = matches1[0]
    result['found_label'] = _language_label('preferred_language_1')
    result['missing_label'] = _language_label('preferred_language_2')
    result['missing'] = 'subtitle2'
    _log('auto-match partial: found subtitle1=%s missing subtitle2' % (result['subtitle1']), LOG_INFO)
    return result

  if len(matches1) == 0 and len(matches2) == 1:
    result['mode'] = 'partial'
    result['subtitle2'] = matches2[0]
    result['found_label'] = _language_label('preferred_language_2')
    result['missing_label'] = _language_label('preferred_language_1')
    result['missing'] = 'subtitle1'
    _log('auto-match partial: found subtitle2=%s missing subtitle1' % (result['subtitle2']), LOG_INFO)
    return result

  if len(matches1) > 1 or len(matches2) > 1 or (len(matches1) == 1 and len(matches2) == 1 and matches1[0] == matches2[0]):
    result['mode'] = 'ambiguous'
    _log('auto-match ambiguous: count1=%d count2=%d' % (len(matches1), len(matches2)), LOG_WARNING)
    return result

  result['mode'] = 'none'
  _log('auto-match none: no usable subtitle match', LOG_INFO)
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
  substemp = []
  try:
    for sub in subs:
      # Python can fail to read subtitles from special Kodi locations (for example smb://).
      # Copy each selected subtitle to a local temporary file first.
      subtemp = os.path.join(__temp__, "%s" % (str(uuid.uuid4())))
      if not xbmcvfs.copy(sub, subtemp):
        raise RuntimeError(__language__(33043))
      substemp.append(subtemp)
    merged = mergesubs(substemp)
    _log('merged subtitles: count=%d output=%s' % (len(subs), merged), LOG_INFO)
    return merged
  finally:
    for subtemp in substemp:
      xbmcvfs.delete(subtemp)

def _pick_subtitles_with_settings(start_dir, apply_no_match_behavior=False, force_manual_both=False):
  second_required = _is_second_subtitle_required()
  behavior = 'manual_both'
  if apply_no_match_behavior:
    behavior = _get_no_match_behavior()
  if force_manual_both:
    behavior = 'manual_both'

  if behavior == 'stop':
    _log('no-match behavior=stop; aborting manual picker', LOG_INFO)
    _notify(__language__(33039), NOTIFY_WARNING)
    return None, None, ''

  _log('manual picker behavior=%s second_required=%s start_dir=%s' % (behavior, second_required, start_dir), LOG_DEBUG)
  subtitle1, subtitle1_dir = _browse_for_subtitle(__language__(33005), start_dir)
  if subtitle1 is None:
    _log('manual picker cancelled on first subtitle', LOG_DEBUG)
    return None, None, ''

  if behavior == 'first_only' and not second_required:
    _log('manual picker using first subtitle only: %s' % (subtitle1), LOG_INFO)
    return subtitle1, None, subtitle1_dir

  title2 = __language__(33006) + ' ' + __language__(33009)
  subtitle2, _ = _browse_for_subtitle(title2, subtitle1_dir)
  if subtitle2 is None and second_required:
    _log('manual picker cancelled second subtitle while required', LOG_WARNING)
    _notify(__language__(33040), NOTIFY_WARNING)
    return None, None, ''

  _log('manual picker selected subtitle1=%s subtitle2=%s' % (subtitle1, subtitle2), LOG_INFO)
  return subtitle1, subtitle2, subtitle1_dir

def _run_dual_subtitle_flow():
  video_dir, video_basename = _current_video_context()
  start_dir = _resolve_start_dir(video_dir)

  subtitle1 = None
  subtitle2 = None
  subtitle1_dir = ''
  force_manual_both = False

  automatch = _auto_match_subtitles(video_dir, video_basename)
  _log('dual flow start: video_dir=%s video_basename=%s start_dir=%s automatch_mode=%s' % (video_dir, video_basename, start_dir, automatch['mode']), LOG_DEBUG)
  if automatch['mode'] == 'full':
    subtitle1 = automatch['subtitle1']
    subtitle2 = automatch['subtitle2']
    subtitle1_dir = os.path.dirname(subtitle1)
    _notify(__language__(33035) % (automatch['language1_label'], automatch['language2_label']), NOTIFY_INFO)

  elif automatch['mode'] == 'partial':
    _notify(__language__(33036) % (automatch['found_label'], automatch['missing_label']), NOTIFY_WARNING)
    partial_behavior = _get_partial_match_behavior()

    if partial_behavior == 'manual_both':
      _notify(__language__(33044), NOTIFY_INFO)
      force_manual_both = True

    elif partial_behavior == 'auto_use':
      if automatch['missing'] == 'subtitle2':
        subtitle1 = automatch['subtitle1']
        subtitle1_dir = os.path.dirname(subtitle1)
        title2 = __language__(33006) + ' ' + __language__(33009)
        subtitle2, _ = _browse_for_subtitle(title2, subtitle1_dir)
        if subtitle2 is None and _is_second_subtitle_required():
          _notify(__language__(33040), NOTIFY_WARNING)
          return
      else:
        subtitle2 = automatch['subtitle2']
        browse_dir = os.path.dirname(subtitle2)
        subtitle1, subtitle1_dir = _browse_for_subtitle(__language__(33005), browse_dir)
        if subtitle1 is None:
          return

    else:
      message = __language__(33014) % (automatch['found_label'], automatch['missing_label'])
      if __msg_box__.yesno(__scriptname__, message):
        if automatch['missing'] == 'subtitle2':
          subtitle1 = automatch['subtitle1']
          subtitle1_dir = os.path.dirname(subtitle1)
          title2 = __language__(33006) + ' ' + __language__(33009)
          subtitle2, _ = _browse_for_subtitle(title2, subtitle1_dir)
          if subtitle2 is None and _is_second_subtitle_required():
            _notify(__language__(33040), NOTIFY_WARNING)
            return
        else:
          subtitle2 = automatch['subtitle2']
          browse_dir = os.path.dirname(subtitle2)
          subtitle1, subtitle1_dir = _browse_for_subtitle(__language__(33005), browse_dir)
          if subtitle1 is None:
            return
      else:
        _notify(__language__(33044), NOTIFY_INFO)
        force_manual_both = True

  elif automatch['mode'] == 'ambiguous':
    _notify(__language__(33038), NOTIFY_WARNING)

  elif automatch['mode'] == 'none':
    _notify(__language__(33037), NOTIFY_WARNING)

  apply_no_match_behavior = automatch['mode'] == 'none'
  if subtitle1 is None and subtitle2 is None:
    subtitle1, subtitle2, subtitle1_dir = _pick_subtitles_with_settings(
      start_dir,
      apply_no_match_behavior=apply_no_match_behavior,
      force_manual_both=force_manual_both
    )
    if subtitle1 is None:
      _log('dual flow ended without subtitle selection', LOG_INFO)
      return

  if subtitle1 is None:
    return

  if not subtitle1_dir:
    subtitle1_dir = os.path.dirname(subtitle1)
  _remember_last_used_dir(subtitle1_dir)
  _log('selected subtitles before merge: subtitle1=%s subtitle2=%s' % (subtitle1, subtitle2), LOG_INFO)

  subs = [subtitle1]
  if subtitle2 is not None:
    subs.append(subtitle2)

  try:
    finalfile = _prepare_and_merge_subtitles(subs)
  except Exception as exc:
    _log('subtitle merge failed: %s' % (exc), LOG_ERROR)
    _notify(__language__(33042), NOTIFY_ERROR)
    __msg_box__.ok(__language__(32531), str(exc))
    return

  Download(finalfile)
  if len(subs) > 1:
    _notify(__language__(33041), NOTIFY_INFO)
  else:
    _notify(__language__(33045), NOTIFY_INFO)

action = params.get('action', 'search')

if action == 'manualsearch':
  Search()

elif action == 'search':
  Search()

elif action == 'browsedual':
  _run_dual_subtitle_flow()

elif action == 'settings':
  __addon__.openSettings()
  _log('settings opened', LOG_DEBUG)

else:
  Search()

xbmcplugin.endOfDirectory(int(sys.argv[1]))

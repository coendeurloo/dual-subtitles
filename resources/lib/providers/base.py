# -*- coding: utf-8 -*-


class SubtitleProviderError(Exception):
  pass


class ProviderAuthError(SubtitleProviderError):
  pass


class ProviderRequestError(SubtitleProviderError):
  pass


class SubtitleProviderBase(object):
  name = 'provider'

  def is_enabled(self):
    return False

  def validate_config(self):
    return True

  def search(self, context, language_code, max_results):
    raise NotImplementedError

  def download(self, result):
    raise NotImplementedError


# -*- coding: utf-8 -*-

from .base import ProviderAuthError, ProviderRequestError, SubtitleProviderError
from .opensubtitles import OpenSubtitlesProvider
from .podnadpisi import PodnadpisiProvider
from .subdl import SubDLProvider
from .bsplayer import BSPlayerProvider


def get_enabled_subtitle_providers(provider_config, logger=None):
  providers = [
    OpenSubtitlesProvider(provider_config.get('opensubtitles', {}), logger=logger),
    PodnadpisiProvider(provider_config.get('podnadpisi', {}), logger=logger),
    SubDLProvider(provider_config.get('subdl', {}), logger=logger),
    BSPlayerProvider(provider_config.get('bsplayer', {}), logger=logger),
  ]
  return [provider for provider in providers if provider.is_enabled()]


__all__ = [
  'get_enabled_subtitle_providers',
  'ProviderAuthError',
  'ProviderRequestError',
  'SubtitleProviderError',
]

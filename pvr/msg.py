#
# Msg translation constants
#

#Languagesetting
LANGUAGE = 103

#test
LOCALIZE_TEST = 2001

import xbmcaddon
"""
from pvr.util import NativeTranslator
import pvr.platform
self.platform = pvr.platform.getPlatform()
self.translator = NativeTranslator(self.platform.getScriptDir())
"""
def strings(id, replacements = None):
    string = xbmcaddon.Addon(id = 'script.mbox').getLocalizedString(id)
    if replacements is not None:
        return string % replacements
    else:
        return string

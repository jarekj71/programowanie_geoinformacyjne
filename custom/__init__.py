# -*- coding: utf-8 -*-
def classFactory(iface):
    from .custom import TestPlugin
    return TestPlugin(iface)

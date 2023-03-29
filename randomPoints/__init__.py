# -*- coding: utf-8 -*-
def classFactory(iface):
    from .randomPoints import randomPoints
    return randomPoints(iface)


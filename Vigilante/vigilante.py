#!/usr/bin/python3
# -*- coding: utf-8 -*-

import gi
from gi.repository import GLib
from gi.repository import GObject


class Camara(GObject.Object):
    def __init__(self):
        GObject.Object.__init__(self)

        self.__loop = GLib.MainLoop()
        self.__loop.run()


if __name__=="__main__":
    camara = Camara()

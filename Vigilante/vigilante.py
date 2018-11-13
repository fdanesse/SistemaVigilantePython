#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os

import gi
gi.require_version("Gst", "1.0")
gi.require_version("GstVideo", "1.0")

from gi.repository import GLib
from gi.repository import GObject
from gi.repository import Gst
from gi.repository import GstVideo

GObject.threads_init()
Gst.init("--opengl-hwdec-interop=vaapi-glx")


class Camara(Gst.Pipeline):
    def __init__(self):
        Gst.Pipeline.__init__(self)

        camara = Gst.ElementFactory.make('v4l2src', 'v4l2src')
        videoconvert = Gst.ElementFactory.make('videoconvert', 'videoconvert')
        fakesink = Gst.ElementFactory.make('fakesink', 'fakesink')

        self.add(camara)
        self.add(videoconvert)
        self.add(fakesink)

        camara.link(videoconvert)
        videoconvert.link(fakesink)

        self.__bus = self.get_bus()
        self.__bus.add_signal_watch()
        self.__bus.connect("message", self.__sync_message)

        self.set_state(Gst.State.PLAYING)

        print ("Proceso Camara:", os.getpid())

        self.__loop = GLib.MainLoop()
        self.__loop.run()

    def __sync_message(self, bus, mensaje):
        pass


if __name__=="__main__":
    camara = Camara()

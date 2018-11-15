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

VIGILANTE = os.path.join(os.environ["HOME"], "VIGILANTE")
if not os.path.exists(VIGILANTE):
    os.mkdir(VIGILANTE)


class Camara(Gst.Pipeline):

    __gsignals__ = {"estado": (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE, (GObject.TYPE_STRING,))}

    def __init__(self, device="/dev/video0", gtksink=None):

        Gst.Pipeline.__init__(self)

        cameraPath = os.path.join(VIGILANTE, device.replace("/", "_"))
        if not os.path.exists(cameraPath):
            os.mkdir(cameraPath)
        self.__videoPath = os.path.join(cameraPath, "Video")
        if not os.path.exists(self.__videoPath):
            os.mkdir(self.__videoPath)
        self.__imagenPath = os.path.join(cameraPath, "Imagen")
        if not os.path.exists(self.__imagenPath):
            os.mkdir(self.__imagenPath)

        self.__gtksink = gtksink
        self.__device = device

        camara = Gst.ElementFactory.make('v4l2src', 'v4l2src')
        camera.set_property("device", self.__device)
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

        print ("Proceso Camara:", os.getpid())

        self.__loop = GLib.MainLoop()
        

    def __sync_message(self, bus, mensaje):
        #self.emit(str(mensaje))
        pass

    def play_Independiente(self):
        self.set_state(Gst.State.PLAYING)
        self.__loop.run()


def Test(self, camara, info):
    print(camara, info)

if __name__=="__main__":
    camara = Camara()
    camara.connect("estado", Test)
    camara.play_Independiente()

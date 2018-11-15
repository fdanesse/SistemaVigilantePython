#!/usr/bin/python3
# -*- coding: utf-8 -*-

# 1 hora de video = 303.6 Mb

import os
import datetime

import gi
gi.require_version("Gst", "1.0")
gi.require_version("GstVideo", "1.0")

from gi.repository import GLib
from gi.repository import GObject
from gi.repository import Gst
from gi.repository import GstVideo

from libs.timelib import *

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
        VIDEOPATH = os.path.join(cameraPath, "Video")
        if not os.path.exists(VIDEOPATH):
            os.mkdir(VIDEOPATH)
        #self.__imagenPath = os.path.join(cameraPath, "Imagen")
        #if not os.path.exists(self.__imagenPath):
        #    os.mkdir(self.__imagenPath)

        self.__gtksink = gtksink
        self.__device = device
        self.__controller = None

        self.__inicial_datetime = get_datetime_now()

        self.__string_date = get_date_as_string(self.__inicial_datetime)
        self.__video_file_name = get_time_as_string(self.__inicial_datetime)

        path = os.path.join(VIDEOPATH, self.__string_date)
        if not os.path.exists(path):
            os.mkdir(path)
        self.__video_location = os.path.join(path, self.__video_file_name + ".avi")

        camara = Gst.ElementFactory.make('v4l2src', 'v4l2src')
        camara.set_property("device", self.__device)
        videoconvert = Gst.ElementFactory.make('videoconvert', 'videoconvert')
        caps = Gst.Caps.from_string('video/x-raw,pixel-aspect-ratio=1/1,framerate=30/1')  # Corrige un BUG: http://gstreamer-devel.966125.n4.nabble.com/master-vs-1-5-1-changing-video-size-on-compositor-input-td4673354.html
        capsfilter = Gst.ElementFactory.make("capsfilter", "capsfilter")
        capsfilter.set_property("caps", caps)
        x264enc = Gst.ElementFactory.make("x264enc", "x264enc")

        avimux = Gst.ElementFactory.make("avimux", "avimux")
        filesink = Gst.ElementFactory.make('filesink', 'filesink')
        filesink.set_property("location", self.__video_location)

        self.add(camara)
        self.add(videoconvert)
        self.add(capsfilter)
        self.add(x264enc)
        self.add(avimux)
        self.add(filesink)

        camara.link(videoconvert)
        videoconvert.link(capsfilter)
        capsfilter.link(x264enc)
        x264enc.link(avimux)
        avimux.link(filesink)

        self.__bus = self.get_bus()
        self.__bus.add_signal_watch()
        self.__bus.connect("message", self.__sync_message)
        
        print ("Proceso Camara:", os.getpid())

        self.__new_handle(True)

        self.__loop = GLib.MainLoop()
        
    def __sync_message(self, bus, mensaje):
        #self.emit("estado", str(mensaje))
        print(mensaje.type)

    def __new_handle(self, reset):
        if self.__controller:
            GLib.source_remove(self.__controller)
            self.__controller = False
        if reset:
            self.__controller = GLib.timeout_add(200, self.__handle)

    def __handle(self):
        dif = get_datetime_now() - self.__inicial_datetime  # datetime.timedelta()
        minutos = dif.seconds/60
        print(minutos)
        if minutos > 5:
            self.set_state(Gst.State.NULL)
            self.__loop.quit()
            return False
        return True


    def play_Independiente(self):
        self.set_state(Gst.State.PLAYING)
        self.__loop.run()

GObject.type_register(Camara)


def Test(camara, info):
    print(camara, info)

if __name__=="__main__":
    camara = Camara()
    camara.connect("estado", Test)
    camara.play_Independiente()

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
        self.__controller = False
        self.__status = Gst.State.NULL

        self.__inicial_datetime = get_datetime_now()

        self.__string_date = get_date_as_string(self.__inicial_datetime)
        self.__video_file_name = get_time_as_string(self.__inicial_datetime)

        path = os.path.join(VIDEOPATH, self.__string_date)
        if not os.path.exists(path):
            os.mkdir(path)
        self.__video_location = os.path.join(path, self.__video_file_name + ".avi")

        self.__createPipe()
        
        self.__bus = self.get_bus()
        self.__bus.add_signal_watch()
        self.__bus.connect("message", self.__sync_message)
        
        print ("Proceso Camara:", os.getpid())

        self.__new_handle(True)

        self.__loop = GLib.MainLoop()
    
    def __createPipe(self):
        # VIDEO
        camara = Gst.ElementFactory.make('v4l2src', 'v4l2src')
        camara.set_property("device", self.__device)
        queue = Gst.ElementFactory.make('queue', 'queue')
        videoconvert = Gst.ElementFactory.make('videoconvert', 'videoconvert')
        videoscale = Gst.ElementFactory.make('videoscale', 'videoscale')
        caps = Gst.Caps.from_string('video/x-raw,pixel-aspect-ratio=1/1,framerate=30/1,width=640, height=480')  # Corrige un BUG: http://gstreamer-devel.966125.n4.nabble.com/master-vs-1-5-1-changing-video-size-on-compositor-input-td4673354.html
        capsfilter = Gst.ElementFactory.make("capsfilter", "capsfilter")
        capsfilter.set_property("caps", caps)
        videorate = Gst.ElementFactory.make('videorate', 'videorate')
        videorate.set_property("max-rate", 30)
        clockoverlay = Gst.ElementFactory.make('clockoverlay', 'clockoverlay')
        timeoverlay = Gst.ElementFactory.make('timeoverlay', 'timeoverlay')
        timeoverlay.set_property("halignment", 2)
        x264enc = Gst.ElementFactory.make("x264enc", "x264enc")

        self.add(camara)
        self.add(queue)
        self.add(videoconvert)
        self.add(videoscale)
        self.add(capsfilter)
        self.add(videorate)
        self.add(clockoverlay)
        self.add(timeoverlay)
        self.add(x264enc)

        avimux = Gst.ElementFactory.make("avimux", "avimux")
        filesink = Gst.ElementFactory.make('filesink', 'filesink')
        filesink.set_property("location", self.__video_location)

        self.add(avimux)
        self.add(filesink)

        camara.link(queue)
        queue.link(videoconvert)
        videoconvert.link(videoscale)
        videoscale.link(capsfilter)
        capsfilter.link(videorate)
        videorate.link(clockoverlay)
        clockoverlay.link(timeoverlay)
        timeoverlay.link(x264enc)
        x264enc.link(avimux)
        avimux.link(filesink)

    def __sync_message(self, bus, mensaje):
        if mensaje.type == Gst.MessageType.STATE_CHANGED:
            old, new, pending = mensaje.parse_state_changed()
            if old == Gst.State.PAUSED and new == Gst.State.PLAYING:
                if self.__status != new:
                    self.__status = new
                    self.emit("estado", "playing")
                    self.__new_handle(True)

            elif old == Gst.State.READY and new == Gst.State.PAUSED:
                if self.__status != new:
                    self.__status = new
                    self.emit("estado", "paused")
                    self.__new_handle(False)

            elif old == Gst.State.READY and new == Gst.State.NULL:
                if self.__status != new:
                    self.__status = new
                    self.emit("estado", "None")
                    self.__new_handle(False)

            elif old == Gst.State.PLAYING and new == Gst.State.PAUSED:
                if self.__status != new:
                    self.__status = new
                    self.emit("estado", "paused")
                    self.__new_handle(False)
        elif mensaje.type == Gst.MessageType.LATENCY:
            self.recalculate_latency()
        elif mensaje.type == Gst.MessageType.ERROR:
            self.__new_handle(False)

    def __new_handle(self, reset):
        if self.__controller:
            GLib.source_remove(self.__controller)
            self.__controller = False
        if reset:
            self.__inicial_datetime = get_datetime_now()  # El tiempo inicial se reestablece cuando el pipe se pone en play
            self.__controller = GLib.timeout_add(200, self.__handle)

    def __handle(self):
        dif = get_datetime_now() - self.__inicial_datetime  # datetime.timedelta()
        minutos = dif.seconds/60
        if minutos > 5:
            self.set_state(Gst.State.NULL)
            self.__loop.quit()
            return False
        return True


    def play_Independiente(self):
        self.set_state(Gst.State.PLAYING)
        self.__loop.run()
        '''
        self.mainloop = GLib.MainLoop()        
        self.thread = threading.Thread(target=self.mainloop.run)
        self.thread.start() 
        '''

GObject.type_register(Camara)


def Test(camara, info):
    print(camara, info)

if __name__=="__main__":
    camara = Camara()
    camara.connect("estado", Test)
    camara.play_Independiente()

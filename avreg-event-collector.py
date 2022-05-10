#!/usr/bin/env python3
import sys
sys.path.append(".")
sys.dont_write_bytecode = True
import config
import os
import time
import telebot
import mysql.connector as mysql
import multiprocessing as mp
from datetime import datetime
from config import *

#########################################################################
# зависимости требуемые скрипту и как их ставить:
# sudo pip3 install pyTelegramBotAPI
# sudo pip3 install mysql-connector

#отправка простого сообщения
def send_message(msg):
    print("{} {}".format(datetime.now(),msg))
    try:
        bot.send_message(tg_chat, msg)
    except Exception as err:
        print("{} Telegram bot error: {}".format(datetime.now(),err))

#отправка видео(если видео больше 48 мегабайт(tg_max_size) то отправляем как файл 
def send_video(msg,video):
    tg_max_size = 48
    print("{} {}".format(datetime.now(),msg))
    try:
        size=os.stat(video).st_size/(1024*1024)
        vfile = open(video, "rb")
        if size <= tg_max_size:
            bot.send_video(tg_chat, vfile, caption = msg)
        else:
            bot.send_document(tg_chat, vfile, caption = msg)
    except Exception as err:
        print("{} error: {}".format(datetime.now(),err))

#обработка события VERSION
def evt_version(*array):
    if array[1] == "SET": send_message("AVREG event collector запущен, AVREG версии {}.{}".format(array[2],array[3]))
    else: print("VERSION: unknown event",array);

#обработка события EVENT
def evt_event(array, cams_rows):
    dt1      = array[1]
    dt2      = array[2]
    cam_nr   = int(array[3])
    evt_id   = int(array[4])
    ser_nr   = int(array[5])
    evt_cont = array[10]
    cam_name = "no name"
    for row in cams_rows:
         if row[0] == cam_nr: cam_name = row[1]
    if evt_id == 1: #события демона avreg
         if ser_nr == 0: send_message("AVREG демон запущен в",dt2)
         if ser_nr == 1: send_message("AVREG демон остановлен в",dt1)
         if ser_nr == 2: send_message("AVREG демон перезапуск в",dt1)
    if evt_id == 3: #cбой захвата
         if ser_nr == 0: send_message("Камера: {} название: {} error: {}".format(cam_nr,cam_name,evt_cont))
         if ser_nr == 3: send_message("Камера: {} название: {} error: {}".format(cam_nr,cam_name,evt_cont))
    if evt_id == 22: #изменение качества видеокадра
         if ser_nr == 0: send_message("Камера: {} название: {} засветка окончена".format(cam_nr,cam_name))
         if ser_nr == 1: send_message("Камера: {} название: {} засветка началась".format(cam_nr,cam_name))
         if ser_nr == 2: send_message("Камера: {} название: {} затемнение закончено".format(cam_nr,cam_name))
         if ser_nr == 3: send_message("Камера: {} название: {} затемнение началось".format(cam_nr,cam_name))
    if evt_id == 23: #recorded video file
         if str(cam_nr) in str(motion_cams):
             video = "{}/{}".format(storage_dir,evt_cont)
             msg   = "Замечено движение на {} в {}".format(cam_name,dt2)
             send_video(msg, video)

if __name__ == '__main__':
    bot = telebot.TeleBot(tg_token)
    try:
        db = mysql.connect(
           host     = mysql_host,
           user     = mysql_user, 
           passwd   = mysql_pass,
           database = mysql_avregdb
        )
        cursor = db.cursor()
        cursor.execute("SELECT CAM_NR,PARVAL FROM CAMERAS WHERE PARNAME='text_left'")
        cams_rows = cursor.fetchall()
        db.close()
    except mysql.Error as err:
        send_message("Error in MySQL: {}".format(err))
        time.sleep(1)
        exit(1)
    print("{} avreg event collector started".format(datetime.now()))
    while True:
        msgArray = input()
        print(msgArray)
        msgArray = msgArray.split("\t")
        if msgArray[0] == "VERSION":
           p = mp.Process(target = evt_version, args = (msgArray))
           p.start()
        elif msgArray[0] == "EVENT":
           p = mp.Process(target = evt_event, args = (msgArray,cams_rows))
           p.start()
        elif msgArray[0] == "QUIT":
            print("Avreg event-collector closed by command")
            exit(0)
        else:
            print("unknown event",msgArray)
exit(0)
######################## config ##########################################
tg_token      = "tg_token" #токен телеграм бота
tg_chat       = "tg_chat_id"                                    #chat_id в который постим сообщения
mysql_host    = "localhost"                                     #хост с mysql
mysql_user    = "avreg-event-collector"                         #имя пользователя имеющего права на select БД avreg%
mysql_pass    = "password"                                      #пароль
mysql_avregdb = "avreg6_db"                                     #БД avreg
motion_cams   = 1,2,3,4                                         #камеры на которых реагируем на срабатывание детектора двиежения (перечисляем через запятую)
storage_dir   = "/var/spool/avreg"                              #каталог где хранятся файлы с видео записанные avreg
##########################################################################

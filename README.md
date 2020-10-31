SKABEN over MQTT\
\
command protocol for dungeon devices\
\
`<channel_id>` - на примере устройства типа `lock`:\
- в сторону клиента `lock`
- в сторону сервера `lockask`

`<device_id>` - MAC-адрес устройства.\
`<task_id>` - уникальная последовательность символов (alphanumeric).\
`<data_dictionary>` - полезная нагрузка в виде словаря.\

##### пинг-пакеты

`PING` - запрос клиенту\

- заголовок: `<channel_id>/<device_id>/PING`
- содержимое: `b'{"timestamp": 123456789}`

при получении пакета клиент записывает значение timestamp в локальный файл.\
\
`PONG` - ответ от клиента\

- заголовок: `<channel_id>/<device_id>/PONG`
- содержимое: `b'{"timestamp": 123456789}`

идентичен предыдущему, таймстемп берется из локального файла.\
\
PINGLegacy - легаси-пинг для люстр. сломан.\

##### пакеты управления передачей

`ACK` - успех операции\
`NACK` - неуспех операции

- заголовок: `<channel_id>/<device_id>/<ACK|NACK>`
- содержимое: `b'{"timestamp": 123456789, "task_id": <task_id>}`

`WAIT` - не используется.

##### пакеты с полезной нагрузкой

`INFO` - сообщение без обновления конфигурации\
`SUP` - server update - обновление записи о клиенте в базе сервера\
`CUP` - client update - обновление локального конфига клиента\

- заголовок: `<channel_id>/<device_id>/<INFO|CUP|SUP>`
- содержимое: `b'{"timestamp": 123456789, "task_id": <task_id>, "datahold": <data_dictionary>}`

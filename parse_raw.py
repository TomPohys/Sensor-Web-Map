# -*- coding: utf-8 -*-

import psycopg2

db = psycopg2.connect(
    "dbname='db' user='postgres' host='localhost' password='postgres'")

cn = db.cursor()
cn1 = db.cursor()

cn.execute('SELECT raw, timestamp, id FROM "sensorData" ORDER BY id ASC;')
cn1.execute("CREATE TABLE IF NOT EXISTS test4 (id serial NOT NULL PRIMARY KEY, idsensor integer NOT NULL, idmeasure integer NOT NULL, timestamp timestamp  NOT NULL, measuretype varchar(3), measurevalue varchar);")
while 1:
    record = cn.fetchone()
    if not(record):
        break
    else:
        raw, timestamp, id_sensor = record[0], record[1], record[2]
        if id_sensor == 309161:
            continue
        if "\n" not in raw[-2:]:
            raw += cn.fetchone()[0]

        for i in raw.split('\r\n'):
            if i and i[:5] != 'Hello':
                tmp = i.split('#')
                for x in tmp[2:]:
                    if x.startswith('TS'):
                        break
                    jmeno, hodnota = x.split(':')
                    cn1.execute("insert into test4 (idsensor, idmeasure, timestamp, measuretype, measurevalue) values (%s, %s, '%s', '%s', '%s');" % (
                        tmp[0].split(':')[1], tmp[1].split(':')[1], timestamp, jmeno, hodnota.strip()))
db.commit()
db.close()

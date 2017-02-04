# -*- coding: utf-8 -*-

import sqlite3


db_path = 'biblioteczka.db'
conn = sqlite3.connect(db_path)

c = conn.cursor()
#
# Tabele
#
c.execute('''
          CREATE TABLE Biblioteka_kategorie
          ( id_kat INTEGER PRIMARY KEY,
            nazwa_kategorii VARCHAR(50) NOT NULL,
            ilosc_pozycji INTEGER NOT NULL
          )
          ''')
c.execute('''
          CREATE TABLE Ksiazki
          (tytul VARCHAR(100) NOT NULL,
            autor VARCHAR(100) NOT NULL,
            id_kat integer not null,
           FOREIGN KEY(id_kat) REFERENCES Biblioteka_kategorie(id_kat),
           PRIMARY KEY (tytul, autor))
          ''')

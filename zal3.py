# -*- coding: utf-8 -*-

import zal2
import sqlite3
import unittest

db_path = 'biblioteczka.db'

class RepositoryTest(unittest.TestCase):

    def setUp(self):
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute('DELETE FROM Ksiazki')
        c.execute('DELETE FROM Biblioteka_kategorie')
        c.execute('INSERT INTO Biblioteka_kategorie VALUES (1, "Powiesc", 1)')
        c.execute('INSERT INTO Ksiazki VALUES ("Hobit", "Tolkien", 1)')
        conn.commit()
        conn.close()

    def tearDown(self):
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute('DELETE FROM Ksiazki')
        c.execute('DELETE FROM Biblioteka_kategorie')
        conn.commit()
        conn.close()


    def testGetByIdNotFound(self):
        self.assertEqual(zal2.Biblioteka_kategorieRepository().getById(22),
                None, "Powinno wyjsc None")

    def testGetByIdInvitemsLen(self):
        self.assertEqual(len(zal2.Biblioteka_kategorieRepository().getById(1).Ksiazki), 1, "Powinno wyjsc 1")

    def testDeleteNotFound(self):
        self.assertRaises(zal2.RepositoryException,
                zal2.Biblioteka_kategorieRepository().delete, 22)


if __name__ == "__main__":
        unittest.main()

# -*- coding: utf-8 -*-

import sqlite3
from datetime import datetime

# Ścieżka połączenia z bazą danych

db_path = 'biblioteczka.db'

# Wyjątek używany w repozytorium

class RepositoryException(Exception):
    def __init__(self, message, *errors):
        Exception.__init__(self, message)
        self.errors = errors

# Model danych

class Biblioteka_kategorie():
    """Model kategorii
    """
    def __init__(self, id_kat, nazwa_kategorii = "Inne", Ksiazki=[]):
        self.id_kat = id_kat
        self.nazwa_kategorii = nazwa_kategorii
        self.Ksiazki = Ksiazki
        self.ilosc_pozycji = len(self.Ksiazki)

    def __repr__(self):
        return "<Biblioteka_kategorie(id_kat='%s', nazwa_kategorii='%s', ilosc_pozycji='%s', Ksiazki='%s')>" % (
                    self.id_kat, self.nazwa_kategorii, str(self.ilosc_pozycji), str(self.Ksiazki)
                )


class Ksiazki():
    """Model ksiazek w kategoriach. Występuje tylko wewnątrz obiektu Biblioteka_kategorie.
    """
    def __init__(self, tytul, autor):
        self.tytul = tytul
        self.autor = autor

    def __repr__(self):
        return "<Ksiazki(tytul='%s', autor='%s')>" % (
                    self.tytul, self.autor)

# Klasa bazowa repozytorium

class Repository():
    def __init__(self):
        try:
            self.conn = self.get_connection()
        except Exception as e:
            raise RepositoryException('GET CONNECTION:', *e.args)
        self._complete = False

    # wejście do with ... as ...
    def __enter__(self):
        return self

    # wyjście z with ... as ...
    def __exit__(self, type_, value, traceback):
        self.close()

    def complete(self):
        self._complete = True

    def get_connection(self):
        return sqlite3.connect(db_path)

    def close(self):
        if self.conn:
            try:
                if self._complete:
                    self.conn.commit()
                else:
                    self.conn.rollback()
            except Exception as e:
                raise RepositoryException(*e.args)
            finally:
                try:
                    self.conn.close()
                except Exception as e:
                    raise RepositoryException(*e.args)

# repozytorium obiektow typu Biblioteka_kategorie

class Biblioteka_kategorieRepository(Repository):

    def add(self, Biblioteka_kategorie):
        """Metoda dodaje pojedynczą kategorie do bazy danych,
        wraz ze wszystkimi jej tytulami.
        """
        try:
            c = self.conn.cursor()
            c.execute('INSERT INTO Biblioteka_kategorie (id_kat, nazwa_kategorii, ilosc_pozycji) VALUES(?, ?, ?)',
                        (Biblioteka_kategorie.id_kat, Biblioteka_kategorie.nazwa_kategorii, Biblioteka_kategorie.ilosc_pozycji)
                    )
            # zapisz pozycje kategorii
            if Biblioteka_kategorie.Ksiazki:
                for Ksiazki in Biblioteka_kategorie.Ksiazki:
                    try:
                        c.execute('INSERT INTO Ksiazki (tytul, autor, id_kat) VALUES(?,?,?)',
                                        (Ksiazki.tytul, Ksiazki.autor, Biblioteka_kategorie.id_kat)
                                )
                    except Exception as e:
                        #print "item add error:", e
                        raise RepositoryException('error adding Biblioteka_kategorie item: %s, to Biblioteka_kategorie: %s' %
                                                    (str(Ksiazki), str(Biblioteka_kategorie.id_kat))
                                                )
        except Exception as e:
            #print "Biblioteka_kategorie add error:", e
            raise RepositoryException('error adding Biblioteka_kategorie %s' % str(Biblioteka_kategorie))

    def addBook(self, Ksiazki, id):
        """Metoda dodaje pojedynczą ksiazke do bazy danych,
        wraz z przypisaniem jej z gory kategorii.
        """
        try:
            c = self.conn.cursor()
            c.execute('INSERT INTO Ksiazki (tytul, autor, id_kat) VALUES(?,?,?)',
                                        (Ksiazki.tytul, Ksiazki.autor, id))
        except Exception as e:
                        #print "item add error:", e
            raise RepositoryException('2 error adding Biblioteka_kategorie item: %s, to Biblioteka_kategorie: %s' %
                                                    (str(Ksiazki), str(Biblioteka_kategorie.id_kat))
                                                )



    def delete(self, Biblioteka_kategorie):
        """Metoda usuwa pojedynczą kategorie z bazy danych,
        wraz ze wszystkimi jej pozycjami (ksiakami).
        """
        try:
            c = self.conn.cursor()
            # usuń ksiazki
            c.execute('DELETE FROM Ksiazki WHERE id_kat=?', (Biblioteka_kategorie.id_kat,))
            # usuń kategorie
            c.execute('DELETE FROM Biblioteka_kategorie WHERE id_kat=?', (Biblioteka_kategorie.id_kat,))

        except Exception as e:
            #print "Biblioteka_kategorie delete error:", e
            raise RepositoryException('error deleting Biblioteka_kategorie %s' % str(Biblioteka_kategorie))

    def getById(self, id):
        """Get Biblioteka_kategorie by id_kat
        """
        try:
            c = self.conn.cursor()
            c.execute("SELECT * FROM Biblioteka_kategorie WHERE id_kat=?", (id,))
            kat_row = c.fetchone()
            biblioteka_kategorie = Biblioteka_kategorie(id_kat=id)
            if kat_row == None:
                biblioteka_kategorie=None
            else:
                biblioteka_kategorie.nazwa_kategorii = kat_row[1]
                biblioteka_kategorie.ilosc_pozycji = kat_row[2]
                c.execute("SELECT * FROM Ksiazki WHERE id_kat=? order by id_kat", (id,))
                ksiazki_row = c.fetchall()
                items_list = []
                for item_row in ksiazki_row:
                    item = Ksiazki(tytul=item_row[0], autor=item_row[1])
                    items_list.append(item)
                biblioteka_kategorie.Ksiazki=items_list
        except Exception as e:
            #print "Biblioteka_kategorie getById error:", e
            raise RepositoryException('error getting by id Biblioteka_kategorie_id: %s' % str(id))
        return biblioteka_kategorie

if __name__ == '__main__':
    try:
        with Biblioteka_kategorieRepository() as Biblioteka_kategorie_repository:
            Biblioteka_kategorie_repository.add(
                Biblioteka_kategorie(id_kat = 1, nazwa_kategorii = "Powiesc",
                        Ksiazki = [
                            Ksiazki(tytul = "Hobbit",   autor = "Tolkien John Ronald Reuel"),
                            Ksiazki(tytul = "Harry Potter i Kamien Filozoficzny",   autor = "Rowling J. K."),
                            Ksiazki(tytul = "Harry Potter i komnata Tajemnic",   autor = "Rowling J. K."),
                        ]
                    )
                )
            Biblioteka_kategorie_repository.complete()
    except RepositoryException as e:
        print(e)

    try:
        with Biblioteka_kategorieRepository() as Biblioteka_kategorie_repository:
            Biblioteka_kategorie_repository.add(
                Biblioteka_kategorie(id_kat = 2, nazwa_kategorii = "Poradniki",
                    )
                )
            Biblioteka_kategorie_repository.complete()
    except RepositoryException as e:
        print(e)

    try:
        with Biblioteka_kategorieRepository() as Biblioteka_kategorie_repository:
            Biblioteka_kategorie_repository.addBook(Ksiazki(tytul = "7 nawykow skutecznego dzialania", autor = "Covey Stephen R."), 2)
            Biblioteka_kategorie_repository.complete()
    except RepositoryException as e:
        print(e)


    try:
        with Biblioteka_kategorieRepository() as Biblioteka_kategorie_repository:
            Biblioteka_kategorie_repository.delete(Biblioteka_kategorie(id_kat = 2))
            Biblioteka_kategorie_repository.complete()
    except RepositoryException as e:
        print(e)

    print (Biblioteka_kategorieRepository().getById(1))

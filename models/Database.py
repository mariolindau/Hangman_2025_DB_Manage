import sqlite3           # SQLite andmebaasiga töötamiseks
import os                # Failisüsteemi kontrollimiseks (kas kataloog olemas jne)
import sys               # Programmi sulgemiseks (vajadusel)
from tkinter import messagebox            # Kasutajateavitused (veateated, küsimused)
from tkinter.filedialog import askopenfilename   # Faili valimine graafiliselt


class Database:
    def __init__(self, db_path='databases/hangman_2025.db'):
        """
        Konstruktor. Seob andmebaasi failitee ja loob ühenduse.
        Kui tabelit pole, loob selle.
        """
        self.db_path = db_path
        self.conn = None
        self.connect()
        self.create_words_table()

    # ... muud meetodid jäävad samaks ...

    def get_all_categories(self):
        """
        Tagastab unikaalsed kategooriad andmebaasist.
        :return: list kategooriatest (sorteeritult)
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute('select DISTINCT category * from words ORDER BY category')
            rows = cursor.fetchall()
            return [row[0] for row in rows]
        except sqlite3.Error as e:
            print(f"Viga kategooriate küsimisel: {e}")
            return []

    def connect(self):
        """
        Ühendub andmebaasiga. Kui kaust (näiteks 'databases') puudub, loob selle.
        """
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self.conn = sqlite3.connect(self.db_path)

    def close(self):
        """
        Katkestab ühenduse andmebaasiga.
        """
        if self.conn:
            self.conn.close()

    def create_words_table(self):
        """
        Loob 'words' tabeli, kui see ei ole veel olemas.
        Tabelis on kolm veergu: id, word, category.
        """
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS words (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                word TEXT NOT NULL,
                category TEXT NOT NULL
            )
        ''')
        self.conn.commit()

    def check_valid_structure(self):
        """
        Kontrollib, kas andmebaasis on olemas 'words' tabel ja vajalikud veerud:
        id, word, category.
        :return: True kui sobib, False kui mitte
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute("PRAGMA table_info(words)")  # küsime tabeli struktuuri
            columns = cursor.fetchall()
            expected_columns = {'id', 'word', 'category'}
            current_columns = {col[1] for col in columns}
            return expected_columns.issubset(current_columns)
        except:
            return False

    def recreate_database(self, new_path='databases/hangman_2025.db'):
        """
        Loob uue andmebaasi, kui vana on vigane. Kuvab kasutajale teavituse.
        """
        self.close()
        self.db_path = new_path
        self.connect()
        self.create_words_table()
        messagebox.showinfo("Info", f"Loodi uus andmebaas: {new_path}")

    def insert_word(self, word, category):
        """
        Lisab ühe uue kirje 'words' tabelisse.
        :param word: sisestatud sõna
        :param category: kategooria
        :return: True kui õnnestus, False kui tekkis viga
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute('INSERT INTO words (word, category) VALUES (?, ?)', (word, category))
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Viga lisamisel: {e}")
            return False

    def fetch_all_words(self):
        """
        Toob kõik kirjed andmebaasist.
        :return: List tuplena (id, word, category)
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute('SELECT id, word, category FROM words')
            return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Viga andmete küsimisel: {e}")
            return []

    def update_word(self, word_id, new_word, new_category):
        """
        Uuendab konkreetse kirje (ID järgi) sõna ja kategooria.
        :param word_id: Kirje ID
        :param new_word: uus sõna
        :param new_category: uus kategooria
        :return: True kui edukas, False kui mitte
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute('UPDATE words SET word = ?, category = ? WHERE id = ?', (new_word, new_category, word_id))
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Viga muutmisel: {e}")
            return False

    def delete_word(self, word_id):
        """
        Kustutab kirje ID järgi.
        :param word_id: Kirje ID
        :return: True kui edukas, False kui mitte
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute('DELETE FROM words WHERE id = ?', (word_id,))
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Viga kustutamisel: {e}")
            return False

    def open_database_via_dialog(self):
        """
        Avab failivalija, laseb kasutajal valida olemasoleva andmebaasi.
        Kui andmebaas ei sobi (vale struktuur), siis:
        - Kas loob uue
        - Või annab hoiatuse ja ei ava
        :return: True kui kõik ok, False kui katkestati
        """
        file_path = askopenfilename(
            defaultextension=".db",
            filetypes=[("SQLite andmebaasid", "*.db"), ("Kõik failid", "*.*")]
        )
        if not file_path:
            return False  # Kasutaja katkestas

        self.close()
        self.db_path = file_path
        self.connect()

        if not self.check_valid_structure():
            # Küsi kasutajalt, kas soovib luua uue
            result = messagebox.askyesno(
                "Vigane andmebaas",
                "Valitud andmebaasis puudub sobiv tabel või veerud.\nKas soovid luua uue andmebaasi?"
            )
            if result:
                self.recreate_database(file_path)
            else:
                messagebox.showwarning("Hoiatus", "Andmebaasi ei avatud.")
                return False

            # Alternatiiv – sulge rakendus täielikult (soovi korral)
            # messagebox.showerror("Viga", "Vale andmebaasi struktuur. Rakendus suletakse.")
            # sys.exit()

        return True

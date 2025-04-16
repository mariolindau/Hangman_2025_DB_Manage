from models.Database import Database

class Model:
    def __init__(self):
        # Luuakse andmebaasi objekt vaikimise asukohaga
        self.db = Database()

    def add_word(self, word, category):
        """Lisab sõna ja kategooria andmebaasi.
        :return: True kui õnnestus, False kui ei
        """
        return self.db.insert_word(word, category)

    def get_all_words(self):
        """
        Tagastab kõik kirjed andmebaasist.
        :return: List (id, word, category)
        """
        return self.db.fetch_all_words()

    def update_word(self, word_id, new_word, new_category):
        """
        Uuendab süna ja kategooriat vastavalt ID-le
        """
        return self.db.update_word(word_id, new_word, new_category)

    def delete_word(self, word_id):
        """
        Kustutab kirje ID järgi
        """
        return self.db.delete_word(word_id)

    def open_database_via_file_dialog(self):
        """
        Avab uue andmebaasi faili kasutaja valiku alusel.
        :return: True kui õnnestus, False kui mitte
        """
        return self.db.open_database_via_dialog()

    def get_all_categories(self):
        return self.db.get_all_categories()
from tkinter import END, messagebox
from tkinter import filedialog


class Controller:
    def __init__(self, model, view):
        """
        Kontrolleri konstruktor
        :param model: main-is loodud mudel
        :param view:  main-is loodud view
        """
        self.model = model
        self.view = view

        # Rippmenüü funktsionaalsus
        self.view.get_combo_categories.bind("<<ComboboxSelected>>", self.combobox_change)

        # Seome nupud funktsioonidega
        self.view.get_btn_open.config(command=self.open_database)
        self.view.get_btn_add.config(command=self.add_word)
        self.view.get_btn_edit.config(command=self.edit_word)
        self.view.get_btn_delete.config(command=self.delete_word)

        # Võimalus lisada hiljem "Ava" nupp
        # self.view.get_btn_open.config(command=self.open_database)

        # Seome tabeli kliki/topeltkliki, et täita vormi
        self.view.get_my_table.bind("<<TreeviewSelect>>", self.fill_form_from_table)

        # Esmalt uuendame tabeli sisu
        self.refresh_table()
        self.update_categories_in_combobox()

    def combobox_change(self, event=None):
        """
        Kui valitakse rippmenüüst tegevus, saadakse kätte tekst kui ka index (print lause). Näide kuidas võiks
        rippmenüü antud rakenduses töötada :)
        :param event: vaikimisi pole
        :return: None
        """
        # print(self.view.get_combo_categories.get(), end=" => ") # Tekst rippmenüüst => Hooned
        # print(self.view.get_combo_categories.current()) # Rippmenüü index => 1
        if self.view.get_combo_categories.current() > 0:  # Vali kategooria on 0
            self.view.get_txt_category.delete(0, END) # Tühjenda uue kategooria sisestuskast
            self.view.get_txt_category.config(state='disabled')  # Ei saa sisestada uut kategooriat
            self.view.get_txt_word.focus()
        else:
            self.view.get_txt_category.config(state='normal')  # Saab sisestada uue kategooria
            self.view.get_txt_category.focus()

    def refresh_table(self):
        """
        Kustutab tabeli sisu ja lisab uuesti kõik andmebaasis olevad kirjed.
        """
        table = self.view.get_my_table
        table.delete(*table.get_children())
        data = self.model.get_all_words()
        for idx, (id_, word, category) in enumerate(data, start=1):
            table.insert('', 'end', values=(idx, id_, word, category))

    def update_categories_in_combobox(self):
        """Värskendab rippmenüü andmed andmebaasist saadud anikaalsete kategooriatega"""
        categories = self.model.get_all_categories()
        values = ['Vali kategooria'] + categories
        self.view.get_combo_categories["values"] = values
        self.view.get_combo_categories.current(0)

    def add_word(self):
        word = self.view.get_txt_word.get().strip()
        if self.view.get_combo_categories.current() > 0:
            category = self.view.get_combo_categories.get()
        else:
            category = self.view.get_txt_category.get().strip()

        if not word or not category:
            messagebox.showerror("Viga", "sõna ja kategooria peavad olema täidetud.")
            return

        if self.model.add_word(word, category):
            self.view.get_txt_word.delete(0, END)

            # Tühjendame ainult siis, kui kasutati käsitsi sisestust
        if self.view.get_combo_categories.current() == 0:
            self.view.get_txt_category.delete(0, END)

            # Rippmenüü tagasi "Vali kategooria"
            self.view.get_combo_categories.set("Vali kategooria")
            self.view.get_txt_category.config(state='normal')

            self.refresh_table()
        else:
            messagebox.showerror("Viga", "Sõna lisamine ebaõnnestus.")

    def fill_form_from_table(self, event=None):
        """
        Täidab vormi tabelist valitud andmete põhjal.
        """
        selected = self.view.get_my_table.selection()
        if not selected:
            return

        values = self.view.get_my_table.item(selected[0], 'values')
        if not values:
            return

        word = values[2]
        category = values[3]

        self.view.get_txt_word.delete(0, END)
        self.view.get_txt_word.insert(0, word)

        self.view.get_txt_category.config(state='normal')
        self.view.get_txt_category.delete(0, END)
        self.view.get_txt_category.insert(0, category)

        self.view.get_combo_categories.set("Vali kategoria")

    def edit_word(self):
        """Muudab valitud kirje andmebaasis ja tabelis."""
        selected = self.view.get_my_table.selection()
        if not selected:
            messagebox.showwarning("Hoiatus", "Palun vali tabelist kirje mida muuta.")
            return

        values = self.view.get_my_table.item(selected[0], 'values')
        word_id = values[1]
        new_word = self.view.get_txt_word.get().strip()
        new_category = self.view.get_txt_category.get().strip()

        if not new_word or not new_category:
            messagebox.showerror("Viga", "Sõna ja kategooria ei tohi olla tühjad.")
            return

        if self.model.update_word(word_id, new_word, new_category):
            self.refresh_table()
            self.update_categories_in_combobox()
        else:
            messagebox.showerror("Viga", "Muutmine ebaõnnestus.")

    def delete_word(self):
        """Kustutab valitud kirje andmebaasist ja tabelist."""
        selected = self.view.get_my_table.selection()
        if not selected:
            messagebox.showwarning("Hoiatus", "Palun vali tabelist kirje mida kustutada.")
            return

        values = self.view.get_my_table.item(selected[0], 'values')
        word_id = values[1]

        confirm = messagebox.askyesno("Kustutamine", "Kas oled kindel, et soovid selle kustutada?")
        if confirm:
            if self.model.delete_word(word_id):
                self.refresh_table()
                self.update_categories_in_combobox()
            else:
                messagebox.showerror("Viga", "Kustutamine ebaõnnestus.")

    def open_database(self):
        """Avab andmebaasi failivalijaga ja kontrollib selle sobivust. Kui sobib, siis uuendab tabelit"""
        if self.model.open_database_via_file_dialog():
            self.refresh_table()
            self.update_categories_in_combobox()
        else:
            messagebox.showwarning("Hoiatus", "Andmebaasi ei avatud")
import pandas as pd
from tkinter import *
from tkinter import filedialog
from tkinter import messagebox as msg
from pandastable import Table
from csv_diff import load_csv, compare


class CsvTable:

    def __init__(self, root):

        self.root = root
        self.file_name = ''
        self.f = Frame(self.root,
                       height=800,
                       width=850)
        self.f.pack()
        self.message_label = Label(self.f,
                                   text='Редактор CSV документов',
                                   font=('Arial', 20, 'bold'),
                                   fg='Black')
        self.display_csv_button = Button(self.f,
                                         text='Открыть CSV',
                                         font=('Arial', 14),
                                         bg='Green',
                                         fg='Black',
                                         command=self.display_csv_file)
        self.message_label.grid(row=0, column=0)
        self.display_csv_button.grid(row=2, column=0)

    def save_df(self):
        self.temp_df.loc[self.temp_df['Базовая цена'] == 0, 'Базовая цена'] = ''
        with open('import_data.csv', 'w', encoding='utf-8-sig', newline='') as f:
            self.temp_df.to_csv(f, index=False)
        msg.showinfo('Файл сохранен', 'CSV файл сохранен')

        diff = compare(
            load_csv(open('original_data.csv', encoding='utf-8-sig'), key='Артикул'),
            load_csv(open('import_data.csv', encoding='utf-8-sig'), key='Артикул')
        )

        def elem_printer(total_text, data_list):
            for i_elem in data_list:
                new_line = f'Артикул: {i_elem.get("Артикул")}; Имя: {i_elem.get("Имя")}; ' \
                           f'В наличии?: {i_elem.get("В наличии?")} Запасы: {i_elem.get("Запасы")}; ' \
                           f'Базовая цена: {i_elem.get("Базовая цена")}'
                total_text = '\n'.join([total_text, new_line])

        add_counter = diff.get('added', [])
        total_text = f'Добавлено: {len(add_counter)}'
        if len(add_counter) > 0:
            total_add_info = diff.get('added')
            elem_printer(total_text, total_add_info)

        remove_counter = diff.get('removed', [])
        total_text = '\n'.join([total_text, f'Удалено: {len(remove_counter)}'])
        if len(remove_counter) > 0:
            total_remove_info = diff.get('removed')
            elem_printer(total_text, total_remove_info)

        change_counter = diff.get('changed', [])
        total_text = '\n'.join([total_text, f'Изменено: {len(change_counter)}'])
        if len(change_counter) > 0:
            for i_elem in change_counter:
                total_changes = ''
                for key, value in i_elem.get('changes').items():
                    data_line = f'{key}: {value[0]} -> {value[1]}'
                    total_changes = '\n'.join([total_changes, data_line])

                new_line = f'Артикул: {i_elem.get("key")}, Изменения: {total_changes}\n'
                total_text = '\n'.join([total_text, new_line])

        text_editor = Text()
        text_editor.pack()
        text_editor.delete('1.0', END)
        text_editor.insert('1.0', total_text)

    def display_csv_file(self):
        try:
            self.file_name = filedialog.askopenfilename(initialdir='/Desktop',
                                                        title='Выберите загруженный csv-файл',
                                                        filetypes=(('CSV file', '*.csv'),))
            self.temp_df = pd.read_csv(self.file_name)

            if len(self.temp_df) == 0:
                msg.showinfo('Ошибка!', 'Записи отсутствуют')

            self.temp_df['Базовая цена'] = self.temp_df['Базовая цена'].fillna(0).astype(int)

            root.geometry('850x800')

            f2 = Frame(self.root, height=300, width=800)
            f2.pack(fill=BOTH, expand=True)
            table = Table(f2, dataframe=self.temp_df, read_only=False, decimal=False)
            table.show()
            save_button = Button(self.f,
                                 text='Сохранить',
                                 font=('Arial', 14),
                                 bg='Green',
                                 fg='Black',
                                 command=self.save_df)
            self.display_csv_button.grid_remove()
            save_button.grid(row=4, column=0)

        except FileNotFoundError as e:
            print(e)
            msg.showerror('FileNotFoundError', str(e))


root = Tk()
root.title('Редактор CSV документов')

obj = CsvTable(root)
root.geometry('400x100')
root.mainloop()

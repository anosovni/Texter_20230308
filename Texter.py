from tkinter import ttk
from tkinter import *
import sqlite3, os
from tkinter import font
import tkinter.filedialog as fd
import tkinter
from PIL import Image, ImageTk

def create_connection(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(e)

    return conn

def create_table(conn, create_table_sql):
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except Error as e:
        print(e)

def main():
    database = r"texter.db"
    # описание столбцов словаря - id номер, слово и значение
    sql_create_texter_table = """ CREATE TABLE IF NOT EXISTS texter (
                                        id integer PRIMARY KEY AUTOINCREMENT,
                                        word text,
                                        style_bold integer,
                                        style_italic integer,
                                        style_underline integer,
                                        size integer,
                                        picture blob
                                    ); """


    # подключение к базе
    conn = create_connection(database)

    # создание таблицы texter
    if conn is not None:
        create_table(conn, sql_create_texter_table)
        print('ok')
    else:
        print("Ошибка: не удалось подключиться к базе.")

class Texter:
    db_name = 'texter.db'
       
    def __init__(self, window):

        self.wind = window
        self.wind.title('Texter')
                      
        # создание элементов для ввода слов и значений
        frame = LabelFrame(self.wind, text = 'Введите новую заметку')
        frame.grid(row = 0, column = 0, columnspan = 5)
        self.word = Text(frame)
        self.word.focus()
        self.word.insert('1.0','Введите заметку')
        self.word.grid(row = 0, column = 0)
        self.numb = Label(frame, text = '')
        self.numb.grid(row = 1, column = 0, sticky = W)
        self.message = Label(text = '', fg = 'green')
        self.message.grid(row = 2, column = 0, columnspan = 1, sticky = W + E)
        self.canvas = tkinter.Canvas(frame, height=400, width=400, bg='white')
        self.canvas.grid(row=0,column=1)
        
        # таблица заметок
        self.tree = ttk.Treeview(height = 10, columns = 2)#(1,2,3,4,5,6,7))
        self.tree.grid(row = 3, column = 0, columnspan = 5, sticky = W + E)
        self.tree.heading('#0', text = 'Номер', anchor = CENTER)
        self.tree.column('#0', anchor= CENTER, width = 50, stretch = NO)
        self.tree.heading('#1', text = 'Заметки', anchor = CENTER)
        #self.tree.heading('#2', text = 'Жирный', anchor = CENTER)
        #self.tree.heading('#3', text = 'Курсив', anchor = CENTER)
        #self.tree.heading('#4', text = 'Подчеркнутый', anchor = CENTER)
        #self.tree.heading('#5', text = 'Размер', anchor = CENTER)
        #self.tree.heading('#6', text = 'Картинка', anchor = CENTER)
                
        # создание меню редактирования        
        ttk.Button(text = 'Жирный', command = self.bold_word).grid(row = 1, column = 0, sticky = W + E)
        ttk.Button(text = 'Курсив', command = self.italic_word).grid(row = 1, column = 1, sticky = W + E)
        ttk.Button(text = 'Подчеркнутый', command = self.underline_word).grid(row = 1, column = 2, sticky = W + E)
        self.arr_style = [0,0,0]
        
        self.size = StringVar()
        self.spinbox = Spinbox(self.wind, from_=8, to=18, textvariable=self.size)
        self.size.trace("w", self.set_font)
        self.size.set("10")
        self.spinbox.grid(row = 1, column = 3, sticky = W + E)
        
        ttk.Button(text = 'Добавить изображение', command = self.choose_file).grid(row = 1, column = 4, sticky = W + E)
        self.filename = ''
        
        # кнопки редактирования записей
        ttk.Button(text = 'Удалить', command = self.delete_word).grid(row = 4, column = 0, sticky = W + E)
        ttk.Button(text = 'Изменить', command = self.edit_word).grid(row = 4, column = 1, sticky = W + E)
        ttk.Button(text = 'Сохранить', command = self.add_word).grid(row = 4, column = 2, sticky = W + E)
                
        # заполнение таблицы
        self.get_words()
                      
    # подключение и запрос к базе
    def run_query(self, query, parameters = ()):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            result = cursor.execute(query, parameters)
            conn.commit()
        return result

    # изменение шрифта
    def set_font(self, *args): 
        size = self.size.get()       
        self.word.config(font=('', size))
        
    def bold_word(self):
        self.arr_style[1], self.arr_style[2] = 0, 0
        if self.arr_style[0] == 1:
            self.word.config(font=('', self.size.get()))
            self.arr_style[0] = 0
        else:
            self.word.config(font=('', self.size.get(), "bold"))
            self.arr_style[0] = 1
    def italic_word(self):
        self.arr_style[0], self.arr_style[2] = 0, 0
        if self.arr_style[1] == 1:
            self.word.config(font=('', self.size.get()))
            self.arr_style[1] = 0
        else:
            self.word.config(font=('', self.size.get(), "italic"))
            self.arr_style[1] = 1
    def underline_word(self):
        self.arr_style[0], self.arr_style[1] = 0, 0
        if self.arr_style[2] == 1:
            self.word.config(font=('', self.size.get()))
            self.arr_style[2] = 0
        else:
            self.word.config(font=('', self.size.get(), "underline"))
            self.arr_style[2] = 1

    # добавление картинки
    def choose_file(self):
        filetypes = (("Изображение", "*.jpg *.gif *.png"),
                     ("Любой", "*"))
        self.filename = fd.askopenfilename(title="Открыть файл", initialdir="/", filetypes=filetypes)

        if self.filename:
            image = Image.open(self.filename)
            photo = ImageTk.PhotoImage(image)
            self.canvas.image = photo
            image = self.canvas.create_image(0, 0, anchor='nw', image = photo)
        
    def to_binary_picture(self):
        if len(self.filename) != 0:
            with open(self.filename, 'rb') as file:
                blob_picture = file.read()
            return blob_picture
        else:
            return
           
    # заполнение таблицы заметками
    def get_words(self):
        records = self.tree.get_children()
        for element in records:
            self.tree.delete(element)
        query = 'SELECT * FROM texter ORDER BY id ASC'
        db_rows = self.run_query(query)
        for row in db_rows:
            self.tree.insert('', 0, text = row[0], values = (row[1], row[2], row[3], row[4], row[5], row[6]))

    # валидация ввода
    def validation(self):
        return len(self.word.get('1.0', END).strip()) != 0
    # добавление нового слова
    def add_word(self):
        if self.validation():
            if len(str(self.numb['text'])) == 0:                
                query = 'INSERT INTO texter VALUES(NULL, ?, ?, ?, ?, ?, ?)'
                parameters = (self.word.get('1.0', END), self.arr_style[0], self.arr_style[1], self.arr_style[2], self.size.get(), self.to_binary_picture())
                self.run_query(query, parameters)
                self.message['text'] = 'Заметка сохранена'.format(self.word.get('1.0', END))
                self.word.delete('1.0', END)
                self.arr_style[0], self.arr_style[1], self.arr_style[2] = 0, 0, 0
                self.word.config(font=('', '10'))
                self.filename = ''
                self.canvas.image = None
            else:
                query = 'UPDATE texter SET word = ?, style_bold = ?, style_italic = ?, style_underline = ?, size  = ?, picture = ? WHERE id = ?'
                parameters = (self.word.get('1.0', END), self.arr_style[0], self.arr_style[1], self.arr_style[2], self.size.get(), self.to_binary_picture(), self.numb['text'])
                self.run_query(query, parameters)
                self.message['text'] = 'Заметка изменена'.format(self.word.get('1.0', END))
                self.word.delete('1.0', END)
                self.numb['text'] = ''
                self.arr_style[0], self.arr_style[1], self.arr_style[2] = 0, 0, 0
                self.word.config(font=('', '10'))
                self.filename = ''
                self.canvas.image = None
        else:
            self.message['text'] = 'Введите заметку'
        self.get_words()
        
    # удаление заметки 
    def delete_word(self):
        self.message['text'] = ''
        try:
            self.tree.item(self.tree.selection())
        except IndexError as e:
            self.message['text'] = 'Выберите заметку'
            return
        self.message['text'] = ''
        word = self.tree.item(self.tree.selection())['text']
        query = 'DELETE FROM texter WHERE id = ?'
        self.run_query(query, (word, ))
        self.message['text'] = 'Заметка удалена'.format(word)
        self.get_words()
        
    # рeдактирование заметки
    def edit_word(self):
        self.message['text'] = ''
        try:
            self.word.delete('1.0', END)
            self.word.insert('1.0', self.tree.item(self.tree.selection())['values'][0])
            self.numb['text'] = self.tree.item(self.tree.selection())['text']
            self.arr_style[0] = self.tree.item(self.tree.selection())['values'][1]
            self.arr_style[1] = self.tree.item(self.tree.selection())['values'][2]
            self.arr_style[2] = self.tree.item(self.tree.selection())['values'][3]
            self.size.set(self.tree.item(self.tree.selection())['values'][4])            
            if self.tree.item(self.tree.selection())['values'][1] == 1:
                self.word.config(font=('', self.tree.item(self.tree.selection())['values'][4], "bold"))
            if self.tree.item(self.tree.selection())['values'][2] == 1:
                self.word.config(font=('', self.tree.item(self.tree.selection())['values'][4], "italic"))
            if self.tree.item(self.tree.selection())['values'][3] == 1:
                self.word.config(font=('', self.tree.item(self.tree.selection())['values'][4], "underline"))
            self.canvas.image = None
           
        except IndexError as e:
            self.message['text'] = 'Выберите заметку для изменения'
            return      

if __name__ == '__main__':
    main()
    window = Tk()
    application = Texter(window)
    window.mainloop()

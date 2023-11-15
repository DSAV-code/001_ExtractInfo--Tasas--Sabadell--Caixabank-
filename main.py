from datetime import datetime
from tkinter import Tk, Button, messagebox, filedialog, StringVar, \
    DISABLED, ACTIVE, PhotoImage, ttk, IntVar, Frame, LEFT, \
    RIGHT, Radiobutton, Label

from pandas import DataFrame
from pathlib import Path
from os import system

import modules

class Aplicacion():
    def __init__(self):
        self.root = Tk()
        self.root.geometry("600x250")
        self.root.title("TF-001_ExtractInfo Tasas")
        self.root.resizable(width=False,height=False)

        self.pdf_list = []

        # ---------------------- Body ----------------------
        self.color = 'white'
        self.body = Frame(self.root, bg=self.color)
        self.body.pack(side=RIGHT, fill='both', expand=1)

        # Info Label
        self.info_label = Label(self.body, text='', bg=self.color)
        self.info_label.pack(side='top', fill='x', expand=1, pady=10)

        # Search Bar
        folder_img = PhotoImage(file='src\\folder.png')
        self.search_bar = Frame(self.body, bg=self.color)
        self.search_bar.pack(fill='none', expand=1)

        self.folder_value = StringVar()
        self.folder_textbox = ttk.Entry(self.search_bar, width=65, textvariable=self.folder_value, state=DISABLED, justify='left')
        self.folder_textbox.pack(side=LEFT, padx=10, pady=5)
      
        self.button_search_path = Button(self.search_bar,
                                        image=folder_img,
                                        bg=self.color,
                                        command=self.select_path,
                                        cursor='hand2',
                                        relief='flat')
        self.button_search_path.pack(side=RIGHT, padx=10, pady=5)

        # Action Buttons
        self.footer = Frame(self.body, bg=self.color)
        self.footer.pack(fill='none', expand=1)
        self.button_extinfo = ttk.Button(self.footer, text='Analizar tasas', command=self.get_fees_info, width=20, padding=10, state=DISABLED, cursor='arrow')       
        self.button_extinfo.pack(side=LEFT, padx=10, pady=50)
        self.button_openfolder = ttk.Button(self.footer, text='Abrir Ruta', command=self.open_folder, width=20, padding=10, state=DISABLED, cursor='arrow')       
        self.button_openfolder.pack(side=RIGHT, padx=10, pady=50)

        

        # ---------------------- Left-bar ----------------------
        self.left_bar = Frame(self.root, relief='sunken')
        self.left_bar.pack(side=LEFT, fill='y')
        axactor_color_logo = PhotoImage(file='src\\axactor-color.png')
        sabadell_color_logo = PhotoImage(file='src\\sabadell-color.png')
        caixabank_color_logo = PhotoImage(file='src\\caixa-color.png')
        axactor_grey_logo = PhotoImage(file='src\\axactor-grey.png')
        sabadell_grey_logo = PhotoImage(file='src\\sabadell-grey.png')
        caixabank_grey_logo = PhotoImage(file='src\\caixa-grey.png')
        

        # RadioButtons
        self.client_value = IntVar()
        self.axactor_option = Radiobutton(self.left_bar, 
                                          value=1, 
                                          image=axactor_grey_logo,
                                          selectcolor=self.color,
                                          selectimage=axactor_color_logo,
                                          indicatoron=0,
                                          relief='flat',
                                          variable=self.client_value)
        
        self.caixabank_option = Radiobutton(self.left_bar, 
                                          value=2, 
                                          image=caixabank_grey_logo,
                                          selectcolor=self.color, 
                                          selectimage=caixabank_color_logo,
                                          indicatoron=0,
                                          relief='ridge',
                                          variable=self.client_value)
        
        self.sabadell_option = Radiobutton(self.left_bar, 
                                          value=3, 
                                          image=sabadell_grey_logo, 
                                          selectcolor=self.color,
                                          selectimage=sabadell_color_logo,
                                          indicatoron=0,
                                          relief='ridge',
                                          variable=self.client_value)
        
        self.client_value.set(1)

        self.axactor_option.pack(fill="y", expand=True)
        self.caixabank_option.pack(fill="y", expand=True)
        self.sabadell_option.pack(fill="y", expand=True)

        self.root.mainloop()

    #-------------------------- Funtions --------------------------
    def open_folder(self) -> None:
        """Open the select folder in a new window"""
        folder = Path(self.folder_value.get())
        system(f'explorer "{folder}"')

    def reset_values(self) -> None:
        """If any field is empty or an error occurs, change the state and values of interface."""
        self.folder_value.set('')
        self.pdf_list: list = self.pdf_list.clear()
        self.info_label.config(text='')
        self.button_extinfo.config(state=DISABLED)
        self.button_openfolder.config(state=DISABLED)

    def select_path(self):
        """Define the folder path wit the fees."""
        try:
            path_files =  (filedialog.askdirectory(title="Selecciona la ruta con los documentos"))

            # If any path select
            if not path_files or not Path(path_files).exists():
                self.reset_values()
                return None
            
            # Search pdfs
            path_files = Path(path_files).absolute()
            self.pdf_list = [Path(file) for file in list(path_files.glob('*.*')) if file.is_file() and file.suffix.casefold() == '.pdf']
            if (count_pdfs := len(self.pdf_list)) == 0:
                self.reset_values()
                return messagebox.showerror("ERROR", "La ruta no contiene archivos pdf.")
            
            text_label = f'{count_pdfs} tasa encontrada.' if count_pdfs == 1 else f'{count_pdfs} tasas encontradas.'
            # Update fields
            self.folder_value.set(path_files)
            self.info_label.config(text=text_label)
            self.button_extinfo.config(state=ACTIVE)
            self.button_openfolder.config(state=ACTIVE)
            return None
        except Exception as error:
            return messagebox.showerror("ERROR", f"{error}")

    def get_fees_info(self) -> None:
        """Read the fees and return an excel file with the data."""
        try:
            match self.client_value.get():
                case 1: type_fee = modules.AxactorFee
                case 2: type_fee = modules.CaixaBankFee
                case 3: type_fee = modules.SabadellFee
                case _: raise TypeError("El tipo escogido no está definido.")
            
            data_dict = {}
            pdf_fee: Path
            for pdf_fee in self.pdf_list:
                fee = type_fee(pdf_fee)
                data_dict[pdf_fee.stem] = fee.get_data(fee.date, fee.amount, fee.nrc)
            
            # Create dataframe with data
            df = DataFrame(data_dict)
            df = df.transpose()
            df.reset_index(inplace=True)
            df.columns = ['Nombre Archivo Original','Fecha', 'Importe', 'Referencia']

            # Save the excel file
            today = datetime.today()
            out_path = Path(self.folder_value.get()) / f'InfoTasas_{today.day}-{today.month}-{today.year}_{today.hour}-{today.minute}.csv'
            df.to_csv(out_path, index=False, sep=';')
            return messagebox.showinfo('¡COMPLETADO!', 'Ha finalizado el proceso de extraer información de las tasas. \
                                    \n Se ha generado el informe en la ruta seleccionada.')
        except Exception as error:
            return messagebox.showerror("ERROR", f"{error}")
        

def main() -> None:
    Aplicacion()
    pass

if __name__ == "__main__":
    main()
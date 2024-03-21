#*****LIBRERIAS*****
import pandas as pd
import numpy as np
import tkinter as tk
import math
import scipy 
import csv
from scipy.stats import norm
from tkinter import *
from tkinter import messagebox
from tkinter import ttk
from tkinter import Tk
from tkinter import font
from pandastable import Table
from tkinter.filedialog import askopenfile
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

#*****DATAFRAMES*****
#Nuestros Dataframes
df=pd.DataFrame()
dfmuestreo=pd.DataFrame()

#*****INTERFAZ GRÁFICA*****
#Ventana principal del programa  
window = Tk()
window.title("Proyecto de Ciencia de Datos")
window.geometry("500x250")

#*****VARIABLES*****
tPoblacion = IntVar()
tNivelConfianza = DoubleVar()
tPrecision= DoubleVar()
tProporcion= DoubleVar()
tVarianza= DoubleVar()
tZ= DoubleVar()
tMuestraCorregida= IntVar()
tColumna = StringVar()
tEstrato = StringVar()

#*****FUNCIONES*****
#1) Función que permite salir del programa
def exit():
    window.destroy()

#2) Función que permite cargar un archivo con el método ASKOPENFILE
def file_upload():
    file = askopenfile()
    # Verificar si se seleccionó un archivo
    if file is not None:
        print("Archivo seleccionado.")
        global df
        df=pd.read_csv(file)
    else:
        print("No se seleccionó ningún archivo.")

#3) Función que crea una caja de diálogo para ingresar los argumentos.
def dialog_argumentos():
    #Definiendo tamaño de la población
    tPoblacion=len(df)
    
    #Ventana de diálogo para ingresar los argumentos
    dialog = tk.Toplevel(window)
    dialog.title("Argumentos")
    dialog.geometry("500x550")
    
    #Creando etiquetas, labels, cajas de texto, botones:
    bold_font = font.Font(weight="bold")
    labelTitle = tk.Label(dialog, text="Tamaño de Muestra", font=bold_font)
    labelTitle.grid(row=0, column=0,sticky="nsew",columnspan=4)

    label1 = tk.Label(dialog, text="Tamaño Poblacional:")
    label1.grid(row=2, column=0, sticky="w", padx=10, pady=10)
    e1=Entry(dialog, textvariable=tPoblacion)
    e1.grid(row=2, column=1)
    e1.delete(0, tk.END)
    e1.insert(0, tPoblacion)
    e1.configure(state='readonly')
    
    label2 = tk.Label(dialog, text="Nivel de Confianza:")
    label2.grid(row=3, column=0, sticky="w", padx=10, pady=10)
    e2=Entry(dialog, textvariable=tNivelConfianza)
    e2.grid(row=3, column=1)
    
    label3 = tk.Label(dialog, text="Precisión (proporción 0 a 1):")
    label3.grid(row=4, column=0, sticky="w", padx=10, pady=10)
    e3=Entry(dialog, textvariable=tPrecision)
    e3.grid(row=4, column=1)
    
    label4 = tk.Label(dialog, text="Proporción Poblacional:")
    label4.grid(row=5, column=0, sticky="w", padx=10, pady=10)
    e4=Entry(dialog, textvariable=tProporcion)
    e4.grid(row=5, column=1)
    
    label5 = tk.Label(dialog, text="Varianza:")
    label5.grid(row=7, column=0, sticky="w", padx=10, pady=10)
    e5=Entry(dialog, textvariable=tVarianza)
    e5.grid(row=7, column=1)

    label8 = tk.Label(dialog, text="Nombre de la columna :")
    label8.grid(row=6, column=0, sticky="w", padx=10, pady=10)
    e8=Entry(dialog, textvariable=tColumna)
    e8.grid(row=6, column=1)
    
    botonCalcularVar=Button(dialog, text="Calcular Varianza",command=lambda:calcular_Var(e5), bg="silver")
    botonCalcularVar.grid(row=7, column=2, sticky="w", padx=10, pady=10)
    
    label6 = tk.Label(dialog, text="Valor Z :")
    label6.grid(row=8, column=0, sticky="w", padx=10, pady=10)
    e6=Entry(dialog, textvariable=tZ)
    e6.grid(row=8, column=1)
    
    #Deshabilitando campos según elección de comboboxVariable
    if comboboxVariable.current()==0:
        e5.configure(state='disabled')
        e8.configure(state='disabled')
    if comboboxVariable.current()==1:
        e4.configure(state='disabled')
    
    botonCalcularZ=Button(dialog, text="Calcular Z",command=lambda:calcular_Z(e6), bg="silver")
    botonCalcularZ.grid(row=8, column=2, sticky="w", padx=10, pady=10)
    
    label7 = tk.Label(dialog, text="El tamaño estimado de muestra es :")
    label7.grid(row=10, column=0, sticky="w", padx=1, pady=40)
    e7=Entry(dialog, textvariable=tMuestraCorregida)
    e7.grid(row=10, column=1, sticky="w", padx=10, pady=40)

    bold_font = font.Font(weight="bold")
    labelTitle = tk.Label(dialog, text="Muestreo Estratificado y Gráfico", font=bold_font)
    labelTitle.grid(row=11, column=0,sticky="nsew",columnspan=4)
    
    label9 = tk.Label(dialog, text="Nombre de columna - estrato :")
    label9.grid(row=12, column=0, sticky="w", padx=10, pady=10)
    e9=Entry(dialog, textvariable=tEstrato)
    e9.grid(row=12, column=1, sticky="w", padx=10, pady=10)

    botonTamanioMuestra=Button(dialog, text="Calcular Tamaño de Muestra",command=lambda:tamanio_muestra(e7), bg="lightgreen")
    botonTamanioMuestra.place(x=155, y=320)
    
    botonMuestreo=Button(dialog, text="Generar Muestreo",command=lambda:generar_muestreo(dialog), bg="lightgreen")
    botonMuestreo.place(x=180, y=500)
    
    #if comboboxMuestreo.current()==0:
        #e9.configure(state='disabled')
    
    limpiarCampos()
    
#4) Función que calcula la varianza para los valores de la columna Monto de Vivienda
def calcular_Var(e5):
    valores=df[tColumna.get()]
    lista_vivienda=valores.tolist()
    prom = lambda li:sum(li)/len(li)
    squared_diff = lambda my_list: list(map(lambda x: (x-prom(my_list))**2, my_list))
    varianza = lambda li2: sum(squared_diff(li2))/(len(li2)-1)
    tVarianza=varianza(lista_vivienda)
    print(tVarianza)
    e5.delete(0, tk.END)
    e5.insert(0, tVarianza)
    e5.configure(state='readonly')

#5) Función que calcula el valor de Z (distribución normal)
def calcular_Z(e6):
    tZ=abs(norm.ppf((1-tNivelConfianza.get())/2))
    e6.delete(0, tk.END)
    e6.insert(0, tZ)
    e6.configure(state='readonly')

#6) Función que calcula el tamaño de muestra
def tamanio_muestra(e7):
    if tVarianza.get()==0.0: 
        muestra=(math.pow(tZ.get(),2)*tProporcion.get()*(1-tProporcion.get()))/math.pow(tPrecision.get(),2)
        tMuestraCorregida=round(muestra/(1+(muestra/len(df))),0)
        e7.delete(0, tk.END)
        e7.insert(0, tMuestraCorregida)
        e7.configure(state='readonly')
    elif tProporcion.get()==0.0:
        #muestra=(math.pow(tZ.get(),2)*tVarianza.get())/math.pow(tPrecision.get(),2)
        muestra=(tZ.get()**2)*tVarianza.get()/tPrecision.get()**2
        print(muestra)
        tMuestraCorregida=round(muestra/(1+(muestra/len(df))),0)
        e7.delete(0, tk.END)
        e7.insert(0, tMuestraCorregida)
        e7.configure(state='readonly')
    print(tMuestraCorregida)

#7) Función que permite visualizar la información del dataframe
def visualizar_data():
    # Creando una ventana para la tabla de datos
    modal = tk.Toplevel(window)
    
    # Creando el datatable:
    dataTable = ttk.Treeview(modal)

    nombre_columnnas = df.columns.tolist() #lista que contiene los nombres de todas las columnas presentes en el DataFrame
    dataTable['columns'] = tuple(nombre_columnnas)#se asignan los nombres de las columnas a las columnas de la tabla.

    dataTable.heading("#0", text="ITEM.") #establece el encabezado de la columna en la tabla '#0' es la primera columna de la tabla
    for nombre in nombre_columnnas:
        dataTable.column(nombre, width=100) #propiedades para cada columna
        dataTable.heading(nombre, text=nombre)
    
    dataTable.column("#0", width=60)
    item = 0
    #interrows() permite iterar a través de un DataFrame por filas, devolviendo en cada iteración un par compuesto por el índice de la fila y una serie que contiene los valores de la fila.
    for _ , fila in df.iterrows(): #for index, row in df.iterrows() solo interesa iterar a través de las filas del DataFrame, sin utilizar el índice de cada fila.
        values = tuple(fila[nombre] for nombre in nombre_columnnas) #tupla que contendrá los valores de las filas que corresponden a cada columna.
        dataTable.insert(parent='',index="end",text=item+1, values=values)#inserta una nueva fila
        #index='end' la nueva fila se agregará al final de la tabla existente, después de todas las filas actuales,
        #values=values contendrá los valores para cada columna de la fila.
        #parent=''indica el elemento padre al que se agregará la nueva fila, al ser una cadena vacía significa que la nueva fila se insertará en el nivel superior
        item = item + 1 #incremento del item
    dataTable.grid(row = 0,column=0)
    
    #Se crea la barra de desplazamiento:
    scrollbar = ttk.Scrollbar(modal, orient="vertical", command=dataTable.yview)
    scrollbar.grid(column=1, row=0, sticky="ns")
    dataTable.configure(yscrollcommand=scrollbar.set)
    
    """ # Crear un PandasTable frame 
    frame = Table(modal, dataframe=df)
    frame.show() """

#8) Función que permite generar el muestreo Simple y Estratificado
def generar_muestreo(dialog):
    global dfmuestreo
    if comboboxMuestreo.current()==0:
        dfmuestreo=df.sample(tMuestraCorregida.get(), replace=False, random_state=42)
    elif comboboxMuestreo.current()==2:
        #Para agrupar los datos según la columna IFI y obtener el tamaño (cantidad de elementos), de cada grupo (groupby y size):
        cantidades=df.groupby([tEstrato.get()]).size()   #El valor que se obtiene aquí es una serie de cantidades agrupadas a las que se les debe agregar la lista de las entidades mediante un index (ordenado)
        #Crear un índice para la serie conformada por los grupos de elementos de IFI que hemos encontrado: nombres de las entidades bancarias
        nombre_entidad=cantidades.index
        #index=df["IFI"].unique()  Alternativa en Array de todos los valores de la columna IFI (Tipo de entidad) sin duplicados. Es lo mismo que el index pero los tipos de dato son distintos (array e index)

        #Asignar la suma de los valores de los grupos encontrados a una variable:
        cantidad_entidad=cantidades.values

        #Para saber cuántas filas y columnas tiene nuestro dataframe 'df'  utilizamos la función .shape que devuelve: (filas, columnas)
        #tabla=df.shape
        filas_tabla=df.shape[0]
        #columnas_tabla=df.shape[1]

        #Ingresamos el tamaño de la muestra:
        muestra=tMuestraCorregida.get()

        #Creamos nuestra tabla con la primera fila que son los encabezados
        #tabla_final=df.iloc[[0,1],:]
        filas_concatenadas = pd.DataFrame()

        for i in range(0,len(nombre_entidad)):    #recorrer desde posición 0 hasta 17 los valores de index (nombres de las entidades bancarias)
            estrato=df.loc[df[tEstrato.get()]==nombre_entidad[i]]
            #calculamos el tamaño de muestra directamente proporcional a cada estrato:
            sub_muestra=round((cantidad_entidad[i]/filas_tabla*muestra))
            #Definimos el tamaño del estrato que vamos a filtrar
            sub_estrato=estrato.sample(n=sub_muestra, replace = False)
            #Concatenamos todas las filas en la tabla:
            filas_concatenadas = pd.concat([filas_concatenadas,sub_estrato])

        #Para que se impriman todas las filas y no se trunquen:
        pd.set_option("display.max_rows", None)
        dfmuestreo=filas_concatenadas
        
    guardar_csv()
    dialog.destroy()

#9) Función que permite visualizar los datos del muestreo seleccionado
def visualizar_muestreo():
     # Crear una ventana para la tabla de datos
    modal2 = tk.Toplevel(window)
    
    # Creando el datatable:
    dataTable = ttk.Treeview(modal2)

    nombre_columnnas = dfmuestreo.columns.tolist() #lista que contiene los nombres de todas las columnas presentes en el DataFrame
    dataTable['columns'] = tuple(nombre_columnnas)#se asignan los nombres de las columnas a las columnas de la tabla.

    dataTable.heading("#0", text="ITEM.") #establece el encabezado de la columna en la tabla '#0' es la primera columna de la tabla
    for nombre in nombre_columnnas:
        dataTable.column(nombre, width=100) #propiedades para cada columna
        dataTable.heading(nombre, text=nombre)
    
    dataTable.column("#0", width=60)
    item = 0
    #interrows() permite iterar a través de un DataFrame por filas, devolviendo en cada iteración un par compuesto por el índice de la fila y una serie que contiene los valores de la fila.
    for _ , fila in dfmuestreo.iterrows(): #for index, row in df.iterrows() solo interesa iterar a través de las filas del DataFrame, sin utilizar el índice de cada fila.
        values = tuple(fila[nombre] for nombre in nombre_columnnas) #tupla que contendrá los valores de las filas que corresponden a cada columna.
        dataTable.insert(parent='',index="end",text=item+1, values=values)#inserta una nueva fila
        #index='end' la nueva fila se agregará al final de la tabla existente, después de todas las filas actuales,
        #values=values contendrá los valores para cada columna de la fila.
        #parent=''indica el elemento padre al que se agregará la nueva fila, al ser una cadena vacía significa que la nueva fila se insertará en el nivel superior
        item = item + 1 #incremento del item
    dataTable.grid(row = 0,column=0)
    
    #Se crea la barra de desplazamiento:
    scrollbar = ttk.Scrollbar(modal2, orient="vertical", command=dataTable.yview)
    scrollbar.grid(column=1, row=0, sticky="ns")
    dataTable.configure(yscrollcommand=scrollbar.set)  
    
#10) Función que permite guardar el muestreo generado en un archivo 'csv'    
def guardar_csv():
    #dfmuestreo.to_csv('D:/Cibertec/Ciclo III/Lenguaje de Ciencia de Datos/Proyecto/muestra.csv')
    dfmuestreo.to_csv('muestra.csv')

#11) Función que limpia las cajas de texto
def limpiarCampos():
    tNivelConfianza.set(0.0)
    tPrecision.set(0.0)
    tProporcion.set(0.0)
    tVarianza.set(0.0)
    tZ.set("")
    tMuestraCorregida.set("")
    tColumna.set("")
    tEstrato.set("")

#12) Función que muestra el gráfico
def generar_grafico():
    # Creamos una ventana de tkinter
    ventana_gráfico = tk.Tk()
    ventana_gráfico.title("Gráfico")
    
    # Crear una figura de matplotlib
    fig = Figure(figsize=(7, 5), dpi=70)
    ax = fig.add_subplot(111) #agrega un subplot (subgráfico) a una figura de matplotlib.se crea un solo subplot en una cuadrícula de 1 fila y 1 columna, y el nuevo subplot se coloca en la posición 1 
    ax.bar(list(dfmuestreo[tEstrato.get()].unique()),list(dfmuestreo[tEstrato.get()].value_counts()), align='center', width=0.5)

    # Crear un lienzo de tkinter para mostrar la figura
    lienzo = FigureCanvasTkAgg(fig, master=ventana_gráfico)
    lienzo.draw()
    lienzo.get_tk_widget().pack()
    
#*****WIDGETS*****
# Creando menubar:
menubar = Menu(window)

#Creando menus en el menubar
submenu=Menu(menubar, tearoff=0)
menubar.add_cascade(label="Archivo", menu=submenu)

# Creando sub-menus debajo de menu "Archivo"
archivo = Menu(submenu, tearoff=0)
submenu.add_cascade(label="Salir", command=exit)
 
# Agregar el Menú a la caja
window.config(menu=menubar)  
    
# Creando  combobox, etiquetas, botones y cajas de texto:
    # Creando el combobox Muestreo
comboboxMuestreo = ttk.Combobox(state="readonly", values=["Muestreo Simple", "Muestreo Sistemático", "Muestreo Estratificado"])
comboboxMuestreo.grid(row=1, column=1, padx=10, pady=10)
    # Establecer un valor predeterminado
comboboxMuestreo.set("Seleccionar opción")
    # Creando el combobox Naturaleza de la variable
comboboxVariable=ttk.Combobox(state="readonly", values=["Proporción", "Promedio"])
comboboxVariable.grid(row=3, column=1, padx=10, pady=10)
    # Establecer un valor predeterminado
comboboxVariable.set("Seleccionar opción")

#Encabezado
bold_font = font.Font(weight="bold") 
labelTitle = tk.Label(window, text="Créditos Mi Vivienda", font=bold_font)
labelTitle.grid(row=0, column=0,sticky="nsew",columnspan=3)

#Creando labels y etiquetas:
labelTipoMuestreo = tk.Label(window, text="Dataframe:")
labelTipoMuestreo.grid(row=2, column=0, sticky="w", padx=10, pady=10)

labelNaturalezaVariable = tk.Label(window, text="Tipo de Muestreo:")
labelNaturalezaVariable.grid(row=1, column=0, sticky="w", padx=10, pady=10)

labelNaturalezaVariable = tk.Label(window, text="Naturaleza de Variable:")
labelNaturalezaVariable.grid(row=3, column=0, sticky="w", padx=10, pady=10)

botonCargar=Button(window, text="Cargar Archivo",command=file_upload, bg="silver")
botonCargar.grid(row=2, column=1, sticky="w", padx=10, pady=10)

botonVisualizarData=Button(window, text="Visualizar Data",command=visualizar_data, bg="silver") #fg="darkblack"
botonVisualizarData.grid(row=2, column=2, sticky="w", padx=10, pady=10)

botonIngresar=Button(window, text="  Argumentos  ",command=dialog_argumentos, bg="silver")
botonIngresar.grid(row=3, column=2, sticky="w", padx=10, pady=10)
   
botonVisualizarMuestreo=Button(window, text="Visualizar Muestreo",command=visualizar_muestreo, bg="lightblue")
botonVisualizarMuestreo.grid(row=4, column=1, sticky="w", padx=10, pady=10, columnspan=2)    

botonGenerarGrafico=Button(window, text="Generar Gráfico",command=generar_grafico, bg="lightblue")
botonGenerarGrafico.grid(row=4, column=2, sticky="w", padx=10, pady=10, columnspan=2)      

#*****INTERFAZ GRÁFICA*****               
window.mainloop() 
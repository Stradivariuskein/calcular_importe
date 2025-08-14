import tkinter as tk
from tkinter import ttk

from tkinter import messagebox


from pedidos_api import Item, GetPedido
from calculate_amount import calculate_amount
import os
import sys

SIAAC3_PATH = os.environ.get("SIAAC3_RUTE")
SIAACFE_PATH = os.environ.get("SIAACFE_RUTE")

SYSTEM_KEYS = ["ventas", "electronica"]

if not SIAAC3_PATH:
        # Mostrar cuadro de error si la variable no está definida
        messagebox.showerror("Error", "La variable de entorno 'SIAAC3_RUTE' no está definida.")
        sys.exit(1)
else:
    print(f"Ruta definida: {SIAAC3_PATH}") 

class PedidoApp:
    def __init__(self, root):
        self.pedidos = [] # lista con los pedidos abiretos
        self.total_amount = 0
        self.take_amount = 0

        self.root = root
        self.root.title("Gestión de Pedidos")
        
        # Encabezado
        frame_encabezado = tk.Frame(root)
        frame_encabezado.pack(pady=10)

        # Variable asociada a los Radiobuttons
        self.op_sistema = tk.StringVar(value=SYSTEM_KEYS[0])
        
        tk.Label(frame_encabezado, text="Sistema:").grid(row=0, column=0)
        self.sistema_venta = tk.Radiobutton(frame_encabezado, text="Ventas", value=SYSTEM_KEYS[0], variable=self.op_sistema)
        self.sistema_electronica = tk.Radiobutton(frame_encabezado, text="Electrónica", value=SYSTEM_KEYS[1], variable=self.op_sistema)
        self.sistema_venta.grid(row=0, column=1)
        self.sistema_electronica.grid(row=0, column=2)

        tk.Label(frame_encabezado, text="Número de pedido:").grid(row=0, column=3)
        self.entry_pedido = tk.Entry(frame_encabezado)
        self.entry_pedido.grid(row=0, column=4)
        
        # Botón "Abrir" pedido
        btn_abrir = tk.Button(frame_encabezado, text="Abrir", command=self.get_pedido)
        btn_abrir.grid(row=0, column=5)


        # Botón "Limpiar" todo
        btn_clena = tk.Button(frame_encabezado, text="Limpiar", command=self.reset_app)
        btn_clena.grid(row=1, column=0)

        # Tabla de "original"
        frame_original = tk.LabelFrame(root, text="Original")
        frame_original.pack(padx=10, pady=5, fill="x")
        
        columns = ("Item/Ped", "Cod", "Descripcion", "Cantidad", "Precio", "Subtotal")
        self.tree_original = ttk.Treeview(frame_original, columns=columns, show="headings", height=5)
        
        self.tree_original.heading(columns[0], text=columns[0])
        self.tree_original.column(columns[0], width=60)
        self.tree_original.heading(columns[1], text=columns[1])
        self.tree_original.column(columns[1], width=100)
        self.tree_original.heading(columns[2], text=columns[2])
        self.tree_original.column(columns[2], width=300)
        self.tree_original.heading(columns[3], text=columns[3])
        self.tree_original.column(columns[3], width=70)
        self.tree_original.heading(columns[4], text=columns[4])
        self.tree_original.column(columns[4], width=70)
        self.tree_original.heading(columns[5], text=columns[5])
        self.tree_original.column(columns[5], width=70)

        
        self.tree_original.pack(pady=5, padx=5)

        #Label para mostrar el total del pedido
        self.label_total_pedido = tk.Label(root, text="Total del pedido: $0", font=("Arial", 12), anchor="w")
        self.label_total_pedido.pack(padx=10, pady=5, fill="x")
        
        # Nuevo frame para el porcentaje y el botón de cálculo
        frame_calculo = tk.Frame(root)
        frame_calculo.pack(padx=10, pady=5, fill="x")

        # Porcentaje a sacar
        tk.Label(frame_calculo, text="% a sacar:").grid(row=0, column=0)
        self.entry_porcentaje = tk.Entry(frame_calculo)
        self.entry_porcentaje.grid(row=0, column=1)
        
        # Botón de cálculo
        btn_calcular = tk.Button(frame_calculo, text="Calcular", command=self.calcular_items)
        btn_calcular.grid(row=0, column=2)

        self.label_amount_take = tk.Label(frame_calculo, text="Importe a sacar: $0", font=("Arial", 12), anchor="w")
        self.label_amount_take.grid(row=0, column=3)
        
        # Tabla de "items a sacar"
        frame_items = tk.LabelFrame(root, text="Items a sacar")
        frame_items.pack(padx=10, pady=5, fill="x")
        
        columns = ("Item/Ped", "Cod", "Descripcion", "Cantidad", "Precio", "Subtotal")
        self.tree_items = ttk.Treeview(frame_items, columns=columns, show="headings", height=5)
        
        # Configuración de encabezados y tamaños de columna
        for idx, col in enumerate(columns):
            self.tree_items.heading(col, text=col)
            self.tree_items.column(col, width=(60 if col == "Item/Ped" else 100 if col == "Cod" else 300 if col == "Descripcion" else 70))

        self.tree_items.pack(pady=5, padx=5)

        # Label para mostrar el total de los ítems sacados
        self.label_total_items = tk.Label(root, text="Total de ítems sacados: $0", font=("Arial", 12), anchor="w")
        self.label_total_items.pack(padx=10, pady=10, fill="x")  # Ajustado para posicionarlo al final

        # Vincula el evento de clic en una fila
        self.tree_items.bind("<Double-1>", self.editar_cantidad)

        # Variable para el campo de edición
        self.entry_edit = None

    def editar_cantidad(self, event): # no implementado
        """Permite editar el campo de 'cantidad' de una fila."""
        # Obtiene el elemento seleccionado y el índice de la columna
        item_id = self.tree_items.selection()[0]
        column_index = self.tree_items.identify_column(event.x)

        # Asegurarse de que estamos en la columna 'cantidad' (columna 4 en este caso)
        if column_index == "#4":
            # Obtener posición de la celda seleccionada
            x, y, width, height = self.tree_items.bbox(item_id, column_index)
            
            # Crear un Entry temporal para editar
            self.entry_edit = tk.Entry(self.tree_items, width=10)
            self.entry_edit.place(x=x, y=y, width=width, height=height)
            
            # Obtener el valor actual de cantidad y colocarlo en el Entry
            current_value = self.tree_items.item(item_id, "values")[3]
            self.entry_edit.insert(0, current_value)
            self.entry_edit.focus_set()
            
            # Vincular el evento "Enter" para guardar el cambio
            self.entry_edit.bind("<Return>", lambda e: self.guardar_cantidad(item_id))

    def guardar_cantidad(self, item_id):
        """Guarda el nuevo valor de 'cantidad' en la tabla 'items a sacar' y actualiza la tabla original."""
        
        if "take_" in item_id or "orig_" in item_id:
            item_id=item_id[5:]
        
        
        # Obtener los valores actuales del item en 'items a sacar'
        valores = list(self.tree_items.item(f"take_{item_id}", "values"))
        precio_unitario = float(valores[4])
        original_item_id = f"orig_{item_id}"  
        # Obtener el nuevo valor de la cantidad
        try:
            nueva_cantidad = float(self.entry_edit.get())
        except AttributeError:
            nuevos_valores = list(self.tree_original.item(original_item_id, "values"))
            nueva_cantidad = float(nuevos_valores[3])
        # Calcular el nuevo subtotal del item
        nuevo_subtotal = nueva_cantidad * precio_unitario
        valores[3] = nueva_cantidad  # Actualiza el campo 'cantidad'
        valores[5] = nuevo_subtotal  # Actualiza el campo 'subtotal'
        
        # Actualizar los valores en la tabla 'items a sacar'
        self.tree_items.item(f"take_{item_id}", values=valores)

        # Actualizar la tabla original
        
        valores_original = list(self.tree_original.item(original_item_id, "values"))
        
        # Restar la cantidad modificada en 'items a sacar' a la cantidad original
        item_num = valores[0].split("/")[0]
        for pedido in self.pedidos:
            current_item = pedido.get_item(int(item_num))
            if current_item:
                if valores_original[1] == current_item.code:
                    old_count = round(float(current_item.count), 2)
                    break
        else:
            raise Exception(f"Error no se encontro el item {valores}")


        nueva_cantidad_original = old_count - nueva_cantidad
        nuevo_subtotal_original = nueva_cantidad_original * float(valores_original[4])
        
        # Actualizar cantidad y subtotal en la tabla original
        valores_original[3] = nueva_cantidad_original
        valores_original[5] = nuevo_subtotal_original
        self.tree_original.item(original_item_id, values=valores_original)

        # Eliminar el Entry temporal
        try:
            self.entry_edit.destroy()
            self.entry_edit = None  # Limpia la referencia
        except AttributeError:
            pass # no hacer nada si no se creo la referencia

    def listar_todos_iids(self, tree):
        """
        Lista todos los iids (identificadores) de una tabla (Treeview).
        
        Args:
            tree (ttk.Treeview): El widget Treeview del cual se obtendrán los iids.

        Returns:
            list: Una lista con todos los iids presentes en el Treeview.
        """
        iids = tree.get_children()  # Obtiene todos los iids de la tabla
        print("Listado de todos los iids:")
        for iid in iids:
            print(iid)  # Muestra cada iid en la consola
        return iids


    def cargar_items(self, items):
        """Carga una lista de objetos Item en las tablas 'pedido original' y 'items a sacar'."""

        for row in self.tree_items.get_children():
            self.tree_items.delete(row)
        num_pedido = self.entry_pedido.get()
        # Cargar cada item en la tabla original
        
        for item in items:

            self.tree_original.insert("", "end", iid=f"orig_{num_pedido}_{item.item_num}", values=(
                f"{item.item_num}/{num_pedido}",
                item.code,
                item.description,
                item.count,
                item.price,
                item.subtotal
            ))


    def get_pedido(self):
        pedido_num = self.entry_pedido.get()
        for pedido in self.pedidos:
            if str(pedido.num) == pedido_num:
                messagebox.showwarning("Advertencia", f"El pedido numero {pedido_num} ya esta abierto")
                return
            
        if self.op_sistema.get() == SYSTEM_KEYS[0]:
            api = GetPedido(f"{SIAAC3_PATH}/PEDIDOS2.DBF", system=SYSTEM_KEYS[0])
            print(self.op_sistema.get())
        elif self.op_sistema.get() == SYSTEM_KEYS[1]:
            api = GetPedido(f"{SIAACFE_PATH}/PEDIDOS2.DBF", system=SYSTEM_KEYS[0])
            print(self.op_sistema.get())
        else:
            messagebox.showwarning("Advertencia", f"Error inesperado no se pudo identicar el sistema selecionado")

        pedido = api.get_pedido(pedido_num)
        # cambia el valor de lavel
        self.total_amount += round(pedido.amount,2)
        self.label_total_pedido["text"] = f"Total del pedido: ${self.total_amount}"

        self.pedidos.append(pedido)
        self.cargar_items(pedido.items)
        
    def calcular_items(self):
        """dado un porcentaje del monto final quita items hasta llegar al imnporte deseado"""
        #borrar items anteriores
        for row in self.tree_items.get_children():
            self.tree_items.delete(row)
            
        # Lógica para calcular los items a sacar en base al porcentaje ingresado
        percent = float(self.entry_porcentaje.get()) / 100
        percent_amount_take = round(self.total_amount*percent, 2)
        self.label_amount_take["text"] = f"Importe a sacar: ${percent_amount_take}"
        items = calculate_amount(self.pedidos,percent)

        #ordena los items segun el numero de pedido y luego por el numero de item
        items_take_out = {}
        for item, item_id in items[0]:
            num_pedido = item_id.split("_")[0]
            if not num_pedido in items_take_out:
                items_take_out[num_pedido] = []
            
            items_take_out[num_pedido].append((item, item_id))
        # ordena de menor a mayor por el numer de item
        self.items_take_out = []
        for pedido, items in items_take_out.items():
            print(items)
            self.items_take_out += sorted(items, key=lambda x: x[0].item_num)
            print(items)
            
        

        #self.items_take_out = items[0]
        take_amount = 0
        # Cargar cada ítem en la tabla
        for item, item_id in self.items_take_out:
            take_amount += round(float(item.subtotal[0]), 2)
            num_pedido = item_id.split("_")[0]
            self.tree_items.insert("", "end", iid=f"take_{item_id}", values=(
                    f"{item.item_num}/{num_pedido}",
                    item.code,
                    item.description,
                    item.count,
                    item.price,
                    item.subtotal
                ))
            self.guardar_cantidad(item_id)
        
        # cambia el valor de lavel
        self.take_amount = take_amount
        self.label_total_items["text"] = f"Total del pedido: ${self.take_amount}"
        
        new_amount = self.total_amount - take_amount
        self.label_total_pedido["text"] = f"Total del pedido: ${new_amount}"


    # vacia la tabla q se lepasa como parametro
    def clena_tabla(self, treeview):
        for item in treeview.get_children():
            treeview.delete(item)

    # vacia el cotenido del lavel
    def clean_total(self, label):
        label.config(text="Total del pedido :")

    # vacia el cotenido del lavel
    def clean_take_out(self, label):
        label.config(text="Total a sacar :")

    def reset_app(self):
        self.clena_tabla(self.tree_items)
        self.clena_tabla(self.tree_original)

        self.clean_total(self.label_total_pedido)
        self.clean_total(self.label_total_items)

        self.clean_take_out(self.label_amount_take)

        self.pedidos = [] 
        self.total_amount = 0
        self.take_amount = 0

        
if __name__ == "__main__":
    root = tk.Tk()
    app = PedidoApp(root)
    
    #app.calcular_items()
    root.mainloop()

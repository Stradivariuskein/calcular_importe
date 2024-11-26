"""
API PARA PODER VER LOS PEDIDO PEDIDOS DEL SISTEMA (PEDIDOS2.DBF)
"""
import sys

class Item:
    def __init__(self, item_num: int, code: str, price: float, subtotal: float, count: float, description : str) -> None:
        self.item_num = item_num
        self.code = code
        self.price = price
        self.subtotal = subtotal,
        self.count = count
        self.description = description

    def __repr__(self) -> str:
        return f"{self.item_num} {self.code} {self.description} {self.price} {self.count} {self.subtotal}"


class Pedido:
    def __init__(self, num: str, items: list[Item], amount: float) -> None:
        self.num = num
        self.items = items
        self.amount = amount

    def __repr__(self) -> str:
        text = f"{self.num}\n"
        for item in self.items:
            text += f"{item}\n"

        text += f"{self.amount}"
        return text

    def get_item(self, item_num: int):
        try:
            return self.items[item_num-1]
        except Exception as e:
            print(f"error inesperado obteniendo el item[{type(e).__name__}]: {e}")
            return None


class GetPedido:
    def __init__(self, arch_path):
        
        self.pedidos_txt = open(arch_path, "r")


    def get_pedido(self, num_pedido):
        file_pedido = self.pedidos_txt
        try: # valuido q sea un numero
            int(num_pedido)
        except ValueError:
            print(F"Error numero de pedido no valido -> {num_pedido}")
            return None
        
        regex_pedido = " " + num_pedido + " " # exprecion regular para filtrar " {num} " (con espacios) si tiene asterisco es porque se anulo ej: "*{num} "

        file_pedido.seek(0, 2)
        file_size = file_pedido.tell()

        # Calcula la posición para leer 1/16 del archivo
        num_parts = 16
        half_size = file_size // num_parts
        file_pedido.seek(max(0, (half_size * (num_parts - 1)) - 1024))  
        # Lee la última mitad del archivo
        pedidos_txt = file_pedido.read()

        index_pedido = pedidos_txt.find(regex_pedido)
        items = pedidos_txt[index_pedido:].split(num_pedido)[1:] #el primero item esta vacio lo quito
        next_num_pedido = str(int(num_pedido)+1)

        items[-1] = items[-1].split(next_num_pedido)[0]
        
        item_num = 1            
        total = 0
        
        items_list = []
        total = 0
        for item in items:

            try:

                data_item = {
                    'item_num': int(item[:2].strip()),
                    'cod': item[2:11].strip(),
                    'cantidad': round(float(item[11:22].strip()), 3),
                    'precio': round(float(item[23:36].strip()),3),
                    'description': item[37:91].strip(),
                    'subtotal': round(float(item[11:22].strip()), 3) * round(float(item[23:36].strip()),3)
                }

                new_item = Item(data_item['item_num'], data_item['cod'], data_item['precio'], data_item['subtotal'], data_item['cantidad'] ,data_item['description'] )
                
                items_list.append(new_item)
                total+= data_item['subtotal']
                item_num += 1
            except Exception as e:
                print(f"Error en cantidad y preciso {e}")
                sys.exit(1)
        
        pedido = Pedido(num_pedido, items_list, total)
        return pedido



# if __name__ == '__main__':
#     api = GetPedido("X:/siaac3/PEDIDOS2.DBF")

#     print(api.get_pedido("17464"))
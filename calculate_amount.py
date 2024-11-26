from pedidos_api import Item, Pedido


def calculate_amount(pedidos: list[Pedido], percent: float):
    if percent < 1:
        amount_take_out = 0
        current_amount_take_out = 0
        items = []
        for pedido in pedidos:
            amount_take_out +=  pedido.amount * percent
            current_amount_take_out += amount_take_out
            for item in pedido.items:
                items.append((item, f"{pedido.num}_{item.item_num}"))
        items_take_out = []

        # en orden descendente, utiliza `reverse=True`
        items_order_amount = sorted(items , key=lambda x: x[0].subtotal, reverse=True)
        for item, item_id in items_order_amount:
            if current_amount_take_out > item.subtotal[0]:
                current_amount_take_out -= item.subtotal[0]
                if current_amount_take_out >= 0:
                    
                    items_take_out.append((item, item_id))

            
        return [items_take_out, pedido] 
    print("error porcentaje invalido")


    
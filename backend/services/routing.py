from collections import deque
from services.warehouse_net import warehouse_net

def find_nearest_supplier(store, sku, target_warehouse,required_qty, max_depth=3):
    visited = set()
    queue = deque([(target_warehouse,0)])

    while queue:
            current, depth = queue.popleft()
            if depth>max_depth:
                  break
            if current in visited:
                  continue
            
            visited.add(current)


            if current != target_warehouse:
                  qty = store.get_qty(sku, current)
                  if qty >= required_qty:
                        return current
                  
            for neighbour in warehouse_net.get(current,[]):
                  if neighbour not in visited:
                        queue.append((neighbour, depth+1))   

    return None 
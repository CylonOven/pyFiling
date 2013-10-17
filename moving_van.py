#moving_van.py
#program constantly looks in .\move_directions for .order files
#then excicues the move orders in turn.

import os
import shutil

ORDER_DIR = './move_directions'

operations = { "del" : os.remove, #delete
               "mv"  : shutil.move,
               "cp"  : shutil.copyfile
             }

def make_error_order(order, order_dir):
    "closes the order file, then renames it 'error!%odername'"
    order.close()
    new_path = list(os.path.split(order_dir))
    new_path[1] = "!error!" +new_path[1]
    os.rename(order_dir, os.path.join(*new_path))


while 1:
    print("looking for orders...")
    order_list = os.listdir(ORDER_DIR)
    for order in order_list:
        if order.startswith("!error!"):
            continue
        order_file = open(os.path.join(ORDER_DIR, order))
        command = order_file.readline().strip()
        print("opening %s"%order)
        if command not in operations:
            make_error_order(order_file, os.path.join(ORDER_DIR, order))
        command = operations[command]
        try:
            command(*[line.strip() for line in order_file.readlines()])
        except:
            make_error_order(order_file, os.path.join(ORDER_DIR, order))    
        else:
            order_file.close()
            os.remove(os.path.join(ORDER_DIR, order))
        

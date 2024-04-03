def get_name_and_last_name(name):
    data = name.split()
    if len(data) == 4:
        return (f'{data[0]} {data[1]}', f'{data[2]} {data[3]}')
    return (f'{data[0]} {data[1]}', f'{data[2]}')
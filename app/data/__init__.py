with open('app/simple_passwords', 'r') as file:
    simple_passwords = tuple(map(lambda x: x.strip(), file.readlines()))

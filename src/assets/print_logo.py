def print_logo():
    try:
        with open("assets/logo.txt") as logo_file:
            print(logo_file.read())

    except Exception:
        return

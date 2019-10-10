import config


def index_page():
    message = """
        <h1>Settings:</h1>
        <form action="show_errors/1" method="post">
            <input type="submit" name="show_errors_1" value="Show Errors: Yes" />
        </form>
        <form action="show_errors/0" method="post">
            <input type="submit" name="show_errors_0" value="Show Errors: No" />
        </form>
        <form action="short_log/1" method="post">
            <input type="submit" name="short_log_1" value="Short Log: Yes" />
        </form>
        <form action="short_log/0" method="post">
            <input type="submit" name="short_log_0" value="Short Log: No" />
        </form>
        """
    return default_page(message)


def default_page(message):
    return f"""
        <html>
        <head>
        </head>
        <body style="background-color:{config.get_setting(config.PATH, 'Settings', 'bg_color')}">
            {message}
            <a href='/' >Home</a>
        </body>
        </html>
        """.encode('utf-8')

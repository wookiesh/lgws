from .lgws import Client
from .utils import AliasedGroup, KEYMAP
from wakeonlan import send_magic_packet
import click


@click.group(cls=AliasedGroup)
@click.option("-d", "--debug", help="View debug information", is_flag=True)
def cli(debug):
    """
    Get a hold of your LG WebOS Tv from the magical Cli

    \b
    Commands may be shortened for convenience:
        - l for listen
        - i for info
        and so on..
    """
    if debug:
        import logging

        logging.basicConfig(level=logging.DEBUG)


@cli.command()
def register():
    "Request pairing with the TV"
    click.echo("Not yet..")


@cli.command()
def discover():
    "Discover existing smart TV on the LAN and create config file"
    click.echo("Not yet..")


@cli.command()
def on(broadcast="192.168.1.255"):
    "Wake on lan"
    send_magic_packet(Client.load_config().get("mac"), ip_address=broadcast)


@cli.command()
def off():
    "Go back to sleep"
    Client().sc.power_off()


@cli.command()
def info():
    "Get general info from the TV"
    import json

    click.echo(json.dumps(Client().sc.info(), indent=True))


@cli.command()
@click.argument("application", required=False)
@click.option(
    "-v", "--detailed", is_flag=True, help="Display detailed information about the app"
)
def app(application=None, detailed=False):
    "Get or sets the running app"
    c = Client()
    if application == None:
        if detailed:
            import json

            click.echo(json.dumps(c.apps[c.ac.get_current()].data, indent=True))
        else:
            click.echo(c.ac.get_current())
    else:
        xApp = list(c.apps[a] for a in c.apps if application in a)
        if xApp:
            c.ac.launch(xApp[0])
        else:
            click.echo(f"Error: application '{application}' not available", err=True)


@cli.command()
def close():
    "Close running app"
    c = Client()
    app = c.apps.get(c.ac.get_current())
    c.ac.close(c.ac.launch(app))


@cli.command()
@click.argument("message")
def toast(message):
    "Toast it on the screen"
    Client().sc.notify(message)


@cli.command()
@click.argument("message")
def type(message):
    "Send it as keyoard strokes"
    Client().ic.type(message)


@cli.command()
@click.argument("key")
def send(key):
    "Send a remote key"
    c = Client()
    if key == "enter":
        c.ic.enter()
    elif key in c.ic.INPUT_COMMANDS:
        c.ic.connect_input()
        getattr(c.ic, key)()
        c.ic.disconnect_input()


@cli.command()
def listen():
    "Listen for inputs and forward them to the TV (CTRL-C to exit)"

    try:
        from pynput.mouse import Listener as MListener

        c = Client()
        c.ic.connect_input()
        c.last_x = c.last_y = None

        def on_move(x, y):
            if c.last_x is None:
                c.last_x, c.last_y = x, y
            else:
                c.ic.move(x - c.last_x, y - c.last_y)
                c.last_x, c.last_y = x, y
                # print('Pointer moved to {0}'.format((x, y)))

        def on_click(x, y, button, pressed):
            c.ic.click()

        def on_scroll(x, y, dx, dy):
            print(f"Scrolled {'down' if dy < 0 else 'up'} at {(x,y)}")

        m = MListener(on_move=on_move, on_click=on_click, on_scroll=on_scroll)
        m.start()

        while True:
            inp = click.getchar()
            mapped = KEYMAP.get(inp)
            if not mapped:
                click.echo(f"Don't know what to do with '{inp}'", err=True)
            else:
                getattr(getattr(c, mapped[0]), mapped[1])()
    except KeyboardInterrupt:
        m.stop()

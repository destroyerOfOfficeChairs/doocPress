import argparse

def handle_args():
    parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter, description="""
    Generate files for hosting one or more wordpress sites in Docker containers
    """)
    parser.add_argument("--domains", nargs="+", required=True, help="""
    These are the domain names you ulitmately want your wordpress instances to serve.\n
    For Example, if you only want to set up one website:\n
    \t--domains example.com\n
    Or if you have a few domains:\n
    \t--domains foo.com bar.com baz.com\n
    Your docker containers will be named by whatever comes before the first '.'\n
    """)
    parser.add_argument("--username", required=True, help="""
    The username you wish to set for the Traefik Dashboard.\n
    """)
    parser.add_argument("--password", required=True, help="""
    The password for your Traefik username.\n
    """)
    parser.add_argument("--email", required=True, help="""
    The email which certbot will use to generate your SSL cert.\n
    """)

    return parser.parse_args()

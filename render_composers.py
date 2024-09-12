import argparse
import bcrypt
import os
import random
import string
import yaml

from jinja2 import Environment, FileSystemLoader

DEV_SITE     = "templates/dev_site.j2"
DEV_TRAEFIK  = "templates/dev_traefik.j2"
DEV_ENV      = "templates/dev_env.j2"
PROD_SITE    = "templates/prod_site.j2"
PROD_TRAEFIK = "templates/prod_traefik.j2"
PROD_ENV     = "templates/prod_env.j2"

class IndentedDumper(yaml.Dumper):
    def increase_indent(self, flow=False, indentless=False):
        return super(IndentedDumper, self).increase_indent(flow, False)
    
def generate_secure_password(length=16):
    # Special characters that are less likely to cause issues
    safe_special_chars = "!@#%^()-_+={}"

    # Combine character sets
    characters = string.ascii_letters + string.digits + safe_special_chars
    
    # Randomly select characters from the pool
    password = ''.join(random.choice(characters) for i in range(length))
    
    # Ensure the password contains at least one of each character type
    if (not any(c in string.ascii_lowercase for c in password) or
        not any(c in string.ascii_uppercase for c in password) or
        not any(c in string.digits for c in password) or
        not any(c in safe_special_chars for c in password)):
        return generate_secure_password(length)
    
    return password

def encrypt_password(username, password):
    bcrypted = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt(rounds=12)).decode("utf-8")
    bcrypted = bcrypted.replace("$", "$$")
    return f"{username}:{bcrypted}"

def generate_dotenv_file_path_string(is_dev, domain):
    sld = domain.split('.')[0]
    dev_path = "dev/" + sld + ".env"
    prod_path = "prod/" + sld + ".env"
    output = dev_path if is_dev else prod_path
    return output

def render_dotenv_string(args, domain):
    path = DEV_ENV if args.dev else PROD_ENV
    db_user_pw = generate_secure_password()
    db_root_pw = generate_secure_password()
    sld = domain.split('.')[0]
    config = {
        'WORDPRESS_DB_HOST':sld + "_DB",
        'WORDPRESS_DB_NAME':sld + "_DB",
        'WORDPRESS_DB_USER':sld + "_USER",
        'WORDPRESS_DB_PASSWORD':db_user_pw,
        'MARIADB_DATABASE':sld + "_DB",
        'MARIADB_USER':sld + "_USER",
        'MARIADB_PASSWORD':db_user_pw,
        'MARIADB_ROOT_PASSWORD':db_root_pw,
    }
    
    # Setup Jinja2 environment
    env = Environment(loader=FileSystemLoader('.'))
    template = env.get_template(path)

    # Render template with environment variables
    rendered_template = template.render(config)

    return rendered_template

def generate_composer_file_path_string(is_dev):
    dev_path = "dev/docker-compose.yaml"
    prod_path = "prod/docker-compose.yaml"
    output = dev_path if is_dev else prod_path
    return output

def render_composer_string(is_dev, domain):
    path = DEV_SITE if is_dev else PROD_SITE
    sld = domain.split('.')[0]
    config = {
        'DB_NETWORK':sld + "_network",
        'DB_SERVICE':sld + "_DB",
        'WP_DOMAIN':domain,
        'WP_SERVICE':sld,
    }
    
    # Setup Jinja2 environment
    env = Environment(loader=FileSystemLoader('.'))
    template = env.get_template(path)

    # Render template with environment variables
    rendered_template = template.render(config)
    
    return rendered_template

def generate_dotenv(args):
    hashed_credentials = encrypt_password(args.username, args.password)
    path = "dev/.env" if args.dev else "prod/.env"
    with open(path, mode="w") as file:
        file.write("HASHED_CREDENTIALS=" + hashed_credentials)

def generate_initial_docker_compose_file(args):
    composer_template_file_path = DEV_TRAEFIK if args.dev else PROD_TRAEFIK
    composer_file_path = generate_composer_file_path_string(args.dev)
    env = Environment(loader=FileSystemLoader('.'))
    composer_template = env.get_template(composer_template_file_path)
    host = args.domains[0]
    config = {
        'HOST':host,
    }
    if not args.dev:
        config['EMAIL'] = args.email
    rendered_composer_template = composer_template.render(config)
    with open(composer_file_path, mode="w") as file:
        file.write(rendered_composer_template)

def add_services_to_main_docker_compose_file(args):
    for domain in args.domains:
        env_file_path = generate_dotenv_file_path_string(args.dev, domain)
        env_file_string = render_dotenv_string(args, domain)
        with open(env_file_path, mode="w") as file:
            file.write(env_file_string)
        composer_file_path = generate_composer_file_path_string(args.dev)
        composer_file_string = render_composer_string(args.dev, domain)
        with open(composer_file_path, mode="a") as file:
            file.write("\n\n" + composer_file_string)

# Kinda hackey, but it works
def add_volumes_and_networks_to_end_of_compose_file(args):
    volumes_string = "volumes:\n"
    networks_string = "\nnetworks:\n  shared_network:\n    name: shared_network"
    for domain in args.domains:
        sld = domain.split('.')[0]
        volumes_string = volumes_string + f"  {sld}:\n  {sld}_DB:\n"
        networks_string = networks_string + f"\n  {sld}_network:\n    driver: bridge"
    finished_string = "\n\n" + volumes_string + networks_string
    composer_file_path = generate_composer_file_path_string(args.dev)
    with open(composer_file_path, mode="a") as file:
        file.write(finished_string)

def main():
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
    parser.add_argument("--email", help="""
    The email which certbot will use to generate your SSL cert.\n
    """)
    parser.add_argument('--dev', action="store_true", help="""
    This is a true/false flag.\n
    If you want to set up a development environment on your local machine, then use this flag.\n
    """)

    args = parser.parse_args()

    if not args.dev:
        if not args.email:
            parser.error("Argument --email is required unless --dev flag is used.")

    directory = "dev" if args.dev else "prod"
    if not os.path.isdir(directory):
        os.makedirs(directory)

    generate_dotenv(args)

    generate_initial_docker_compose_file(args)

    add_services_to_main_docker_compose_file(args)

    add_volumes_and_networks_to_end_of_compose_file(args)


if __name__ == "__main__":
    main()

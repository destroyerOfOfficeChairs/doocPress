import bcrypt
import random
import string

from jinja2 import Template
    
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

def render_dotenv_string(sld, template_file_path, db_user_pw, db_root_pw):
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
    with open(template_file_path) as file:
        template = Template(file.read())
    rendered_template = template.render(config)
    return rendered_template

def generate_dotenv_files(args):
    hashed_credentials = encrypt_password(args.username, args.password)
    traefik_dotenv_template_path = "templates/traefik_env.j2"
    dev_dotenv_template_path = "templates/dev_env.j2"
    prod_dotenv_template_path = "templates/prod_env.j2"
    traefik_dotenv_dev_path = "../dev/.env"
    traefik_dotenv_prod_path = "../prod/.env"
    with open(traefik_dotenv_template_path) as file:
        template = Template(file.read())
    rendered_traefik_dotenv = template.render(HASHED_CREDENTIALS=hashed_credentials)
    with open(traefik_dotenv_dev_path, mode="w") as file:
        file.write(rendered_traefik_dotenv)
    with open(traefik_dotenv_prod_path, mode="w") as file:
        file.write(rendered_traefik_dotenv)
    for domain in args.domains:
        sld = domain.split('.')[0]
        site_dotenv_dev_path = f"../dev/{sld}.env"
        site_dotenv_prod = f"../prod/{sld}.env"
        db_user_pw = generate_secure_password()
        db_root_pw = generate_secure_password()
        dev_dotenv_string = render_dotenv_string(sld, dev_dotenv_template_path, db_user_pw, db_root_pw)
        prod_dotenv_string = render_dotenv_string(sld, prod_dotenv_template_path, db_user_pw, db_root_pw)
        with open(site_dotenv_dev_path, mode="w") as file:
            file.write(dev_dotenv_string)
        with open(site_dotenv_prod, mode="w") as file:
            file.write(prod_dotenv_string)

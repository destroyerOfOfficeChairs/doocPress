from jinja2 import Template

def render_traefik_service_string(email, host, template_file_path):
    config = {
        "EMAIL": email,
        "HOST": host
    }
    with open(template_file_path) as file:
        template = Template(file.read())
    rendered_template = template.render(config)
    return rendered_template

def render_site_services(args, template_file_path):
    rendered_site_services = []
    for domain in args.domains:
        sld = domain.split('.')[0]
        config = {
            'DB_NETWORK':sld + "_network",
            'DB_SERVICE':sld + "_DB",
            'WP_DOMAIN':domain,
            'WP_SERVICE':sld,
        }
        with open(template_file_path) as file:
            template = Template(file.read())
        rendered_template = template.render(config)
        rendered_site_services.append(rendered_template)
    return rendered_site_services

def create_sld_array(args):
    output = []
    for domain in args.domains:
        output.append(domain.split('.')[0])
    return output

def generate_docker_compose_files(args):
    compose_outline_file_path = "templates/compose_outline.j2"
    dev_compose_file_path = "../dev/docker-compose.yaml"
    prod_compose_file_path = "../prod/docker-compose.yaml"
    dev_traefik_template_path = "templates/dev_traefik.j2"
    dev_site_services_template_path = "templates/dev_site.j2"
    prod_traefik_template_path = "templates/prod_traefik.j2"
    prod_site_services_template_path = "templates/prod_site.j2"
    dev_host = args.domains[0].split('.')[0] + ".localhost"
    prod_host = args.domains[0]
    dev_traefik_service_string = render_traefik_service_string(args.email, dev_host, dev_traefik_template_path)
    dev_site_services_string_array = render_site_services(args, dev_site_services_template_path)
    prod_traefik_service_string = render_traefik_service_string(args.email, prod_host, prod_traefik_template_path)
    prod_site_services_string_array = render_site_services(args, prod_site_services_template_path)
    services = create_sld_array(args)
    with open(compose_outline_file_path) as file:
        dev_compose_template = Template(file.read())
    with open(compose_outline_file_path) as file:
        prod_compose_template = Template(file.read())
    dev_compose_string = dev_compose_template.render(
        traefik=dev_traefik_service_string,
        sites=dev_site_services_string_array,
        services=services)
    prod_compose_string = prod_compose_template.render(
        traefik=prod_traefik_service_string,
        sites=prod_site_services_string_array,
        services=services)
    with open(dev_compose_file_path, mode="w") as file:
        file.write(dev_compose_string)
    with open(prod_compose_file_path, mode="w") as file:
        file.write(prod_compose_string)

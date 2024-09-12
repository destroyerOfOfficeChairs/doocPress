# WordPress Deployment with AWS CloudFormation, Docker, and Ansible

## Overview

**doocPress** is a WordPress deployment solution designed to work seamlessly
with AWS. It automates the deployment of multiple WordPress sites on a single
EC2 instance using Docker, Traefik, and Ansible. The project includes three
core Python scripts that handle key creation, CloudFormation stack setup, and
Docker Compose file generation.

### Version

1.0

## Features

- Automated WordPress deployment on AWS EC2
- Support for multiple domains
- Each domain has its own MariaDB container
- Python scripts to create AWS resources and generate necessary files
- Docker Compose setup for managing WordPress containers
- Traefik integration for reverse proxying and automatic SSL certificate generation
- Traefik dashboard secured by authentication
- Development mode for local testing without HTTPS

## Prerequisites

Before you begin, ensure you have the following:

- An AWS account with permissions to create EC2 resources
- AWS CLI installed and configured correctly
  - You should be able to enter `aws sts get-caller-identity` in your terminal
    and receive some sensible output.
- Python, boto3, and Ansible installed on your local machine

## Setup and Installation

### 1. Clone the Repository

```
git clone git@github.com:destroyerOfOfficeChairs/doocPress.git
cd doocPress
```

### 2. Run key.py

```
python3 key.py --region us-east-1
```

Creates a key pair on AWS and stores an ssh key on your machine in the `~/.ssh`
directory. Change the region to one which you prefer. After you run this, a new
file will be created: `ansible/external_vars.yaml`. This stores some data which
will be used throughout the rest of the process.

### 3. Run cfn.py

```
python3 cfn.py
```

After running this, You should have a CloudFormation stack up and running on AWS
in the same region you specified when you ran the `key.py` script. Some more
values will be written to `ansible/external_vars.yaml`.

### 4. Run render_composers.py

This creates the `docker-compose.yaml` file as well as the associated `.env`
files. The files are written to a newly created directory named `prod`.

```
python3 render_composers.py --domains example.com foo.com bar.com --username your_desired_username --password your_desired_password --email youremail@example.com
```

--domains is followed by a list of domains you would like to host, separated by
spaces.

--username is the username you would like to assign for use with the Traefik dashboard.

--password is the password for the Traefik dashboard user

--email is the email which will be used with Lets Encrypt for SSL certs.

Your dashboard's URL will depend on whichever domain you put in the list first.
In this example, the dashboard would be available at `dashboard.example.com`.
If the --domains argument was given as `--domains foobarbaz.com example1.com
example2.com`, then the dashboard would be available at
`dashboard.foobarbaz.com`.

Your Docker containers will be named based on whatever comes before the first
'.' character for each domain.

### 5. DNS

Manually point your DNS to the EC2 instance IP. You can find the IP address in
`ansible/external_vars.yaml`, or in the AWS console.

### 6. Run the Ansible playbook

```
cd ansible
ansible-playbook doocPlaybook.yaml
```

### 7. Access Your WordPress Site

Once the playbook has successfully run, your WordPress sites will be
accessible at your domains!

## Dev Mode

If you want to create a development environment which you run locally, you can
use the `--dev` flag with the `render_composers.py` script. If you use the
`--dev` flag, you do not need to specify an email.

```
python3 render_composers.py --domains wp1.localhost wp2.localhost --username yourusername --password yourpassword
```

This will create a new directory named `dev`. You can run the dev version by running:

```
cd dev
docker compose up -d
```

You should be able to access your local wordpress site by opening your browser
and navigating to `wp1.localhost`, or whichever domain you had specified.

## Roadmap

- Create an automated way to host additional domains and sites.
- Create an automated way to remove a sites.
- Automate database backups and content backups to an S3 bucket.
- Create a tool which streamlines migration away from this single EC2 instance setup.
- Create a tool which seamlessly imports backup data.
- Create a monitoring and alert system
- Add error handling to the Python scripts.
- Create an "all in one" Python script, so the user does not have to run 3 scripts.

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request
with your changes.

## License

This project is licensed under the MIT License. See the LICENSE file for more
details.

## Changelog

### 1.0

Initial commit

import argparse
import boto3
import os
import string
import yaml

def check_key_exists(key_name, region):
    ec2 = boto3.client('ec2', region_name=region)
    output = False
    try:
        res = ec2.describe_key_pairs(KeyNames=[key_name])
        output = True
    finally:
        return output

def create_key_pair(key_name, key_file_path, region):
    ec2 = boto3.client('ec2', region_name=region)
    response = ec2.create_key_pair(KeyName=key_name)
    with open(key_file_path, 'w') as key_file:
        key_file.write(response['KeyMaterial'])
    os.chmod(key_file_path, 0o400)

def write_selected_args_to_yaml(args, key_file_path, output_file):
    yaml_data = {
        'KEY_FILE_PATH': key_file_path,
        'REGION': args.region,
        'KEY_NAME': args.key_name,
    }
    with open(output_file, 'a') as yaml_file:
        yaml.dump(yaml_data, yaml_file, default_flow_style=False)

def main():
    parser = argparse.ArgumentParser(description='Deploy resources and configure them using AWS and Ansible')
    parser.add_argument('--region', required=True, help='AWS region in which you wish to create resources')
    parser.add_argument('--key-name', default='doocPressKey', help='Name of the EC2 key pair (as it will appear in the AWS console, so no need to add .pem at the end)')
    parser.add_argument('--key-directory', default='~/.ssh/', help='The directory where you would like to store the key')
    args = parser.parse_args()
    key_file_path = os.path.expanduser(f'{args.key_directory}{args.key_name}.pem')
    key_exists_on_local_machine = os.path.isfile(key_file_path)
    key_exists_in_region = check_key_exists(args.key_name, args.region)
    if key_exists_on_local_machine:
        print(f"SSH key already exists in location: {key_file_path}")
    elif key_exists_in_region:
        print(f"SSH key already exists in region: {args.region}")
    else:
        create_key_pair(args.key_name, key_file_path, args.region)
        print(f"You now have an EC2 key here: {key_file_path}")
        write_selected_args_to_yaml(args, key_file_path, "ansible/external_vars.yaml")
        print("Variables written to: ansible/external_vars.yaml")

if __name__ == '__main__':
    main()

import argparse
import boto3
import os
import requests
import string
import yaml

def check_stack_exists(stack_name, region):
    cfn = boto3.client('cloudformation', region_name=region)
    output = False
    try:
        res = cfn.describe_stacks(StackName=stack_name)
        output = True
    finally:
        return output

def run_cloudformation(stack_name, template_file, key_name, region):
    client = boto3.client('cloudformation', region_name=region)
    with open(template_file, 'r') as file:
        template_body = file.read()
    parameters = [
        {
            'ParameterKey': 'KeyName',
            'ParameterValue': key_name
        }
    ]
    response = client.create_stack(
        StackName=stack_name,
        TemplateBody=template_body,
        Parameters=parameters,
        Capabilities=['CAPABILITY_IAM', 'CAPABILITY_NAMED_IAM'],  # If your template includes IAM resources
    )
    print(f"Stack creation initiated for '{stack_name}'. Stack ID: {response['StackId']}")
    print("Waiting for stack creation to complete")
    waiter = client.get_waiter('stack_create_complete')
    waiter.wait(StackName=stack_name)
    print("Stack creation complete")

def get_instance_public_ip(stack_name, region):
    ec2 = boto3.client('ec2', region_name=region)
    stack = boto3.client('cloudformation', region_name=region).describe_stack_resources(StackName=stack_name)
    instance_id = next(
        r['PhysicalResourceId'] for r in stack['StackResources'] if r['ResourceType'] == 'AWS::EC2::Instance'
    )
    reservations = ec2.describe_instances(InstanceIds=[instance_id])
    public_ip = reservations['Reservations'][0]['Instances'][0]['PublicIpAddress']
    print(f"EC2 instance with ID {instance_id} has public IP: {public_ip}")
    return public_ip

def write_selected_args_to_yaml(args, public_ip, output_file):
    yaml_data = {
        'HOST_IP': public_ip,
        'STACK_NAME': args.stack_name
    }
    with open(output_file, 'a') as yaml_file:
        yaml.dump(yaml_data, yaml_file, default_flow_style=False)

def readFromExternalVars(yaml_key):
    with open("ansible/external_vars.yaml", "r") as file:
        data = yaml.safe_load(file)
    value = data[yaml_key]
    return value

def main():
    parser = argparse.ArgumentParser(description='Deploy resources and configure them using AWS and Ansible')
    parser.add_argument('--stack-name', default='doocPressStack', help='What you would like the CloudFormation stack to be named')
    parser.add_argument('--template-file', default='templates/Ec2Cfn.yaml', help='Path to the CloudFormation template file')
    args = parser.parse_args()
    key_name = readFromExternalVars("KEY_NAME")
    region = readFromExternalVars("REGION")
    stack_exists = check_stack_exists(args.stack_name, region)
    if stack_exists:
        print(f"CloudFormation stack already exists: {args.stack_name}")
    else:
        run_cloudformation(args.stack_name, args.template_file, key_name, region)
        public_ip = get_instance_public_ip(args.stack_name, region)
        write_selected_args_to_yaml(args, public_ip, 'ansible/external_vars.yaml')

if __name__ == '__main__':
    main()

import boto3

def fetch_ec2_instance_details():
    # Take AWS credentials and region from the user
    aws_access_key = input("Enter your AWS Access Key ID: ")
    aws_secret_key = input("Enter your AWS Secret Access Key: ")
    aws_region = input("Enter your AWS Default Region (e.g., us-east-1): ")

    # Ensure that AWS keys and region are correctly formatted
    if not aws_access_key or not aws_secret_key or not aws_region:
        print("Error: Missing required AWS credentials or region.")
        return

    # Initialize a session using user-provided credentials
    try:
        ec2_client = boto3.client(
            'ec2',
            aws_access_key_id=aws_access_key,
            aws_secret_access_key=aws_secret_key,
            region_name=aws_region
        )

        # Fetch and display EC2 instance details
        response = ec2_client.describe_instances()

        # Check if there are any instances in the response
        if not response['Reservations']:
            print("No EC2 instances found.")
        else:
            for reservation in response['Reservations']:
                for instance in reservation['Instances']:
                    instance_id = instance.get('InstanceId')
                    instance_type = instance.get('InstanceType')
                    state = instance['State']['Name']
                    public_ip = instance.get('PublicIpAddress')
                    private_ip = instance.get('PrivateIpAddress')

                    print(f"Instance ID: {instance_id}")
                    print(f"Instance Type: {instance_type}")
                    print(f"State: {state}")
                    print(f"Public IP: {public_ip}")
                    print(f"Private IP: {private_ip}")
                    print("-" * 40)

    except Exception as e:
        print(f"Error fetching EC2 instances: {e}")

# Call the function
fetch_ec2_instance_details()

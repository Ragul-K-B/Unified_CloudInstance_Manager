import boto3


def start_stop_ec2_instance(action, instance_id):
    # Take AWS credentials and region from the user
    aws_access_key = input("Enter your AWS Access Key ID: ")
    aws_secret_key = input("Enter your AWS Secret Access Key: ")
    aws_region = input("Enter your AWS Default Region (e.g., us-east-1): ")

    # Initialize a session using user-provided credentials
    ec2_client = boto3.client(
        'ec2',
        aws_access_key_id=aws_access_key,
        aws_secret_access_key=aws_secret_key,
        region_name=aws_region
    )

    try:
        if action == 'start':
            # Start the EC2 instance
            response = ec2_client.start_instances(InstanceIds=[instance_id])
            print(f"Starting EC2 instance {instance_id}...")
        elif action == 'stop':
            # Stop the EC2 instance
            response = ec2_client.stop_instances(InstanceIds=[instance_id])
            print(f"Stopping EC2 instance {instance_id}...")
        else:
            print("Invalid action. Please choose either 'start' or 'stop'.")
            return

        # Display response from AWS
        print(response)
    except Exception as e:
        print(f"Error performing the action: {e}")


# User input for action and instance ID
action = input("Enter the action (start/stop): ").lower()
instance_id = input("Enter the EC2 instance ID: ")

# Call the function to start/stop the EC2 instance
start_stop_ec2_instance(action, instance_id)

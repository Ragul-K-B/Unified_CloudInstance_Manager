import boto3

# Get AWS credentials and instance details from user
ACCESS_KEY = input("Enter your AWS Access Key: ").strip()
SECRET_KEY = input("Enter your AWS Secret Key: ").strip()
REGION = input("Enter your AWS Region (e.g., us-east-1): ").strip()
INSTANCE_ID = input("Enter the EC2 Instance ID: ").strip()
NEW_NAME = input("Enter the new name for the instance: ").strip()

def change_instance_name(instance_id, new_name):
    try:
        ec2 = boto3.client(
            "ec2",
            aws_access_key_id=ACCESS_KEY,
            aws_secret_access_key=SECRET_KEY,
            region_name=REGION,
        )

        # Set the Name tag
        ec2.create_tags(
            Resources=[instance_id],
            Tags=[{"Key": "Name", "Value": new_name}]
        )

        print(f"Instance {instance_id} name changed to '{new_name}' successfully.")

    except Exception as e:
        print(f"Error updating instance name: {e}")

# Call the function
change_instance_name(INSTANCE_ID, NEW_NAME)

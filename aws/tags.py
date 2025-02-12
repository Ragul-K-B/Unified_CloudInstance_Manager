import boto3

# Get AWS credentials from user
ACCESS_KEY = input("Enter your AWS Access Key: ").strip()
SECRET_KEY = input("Enter your AWS Secret Key: ").strip()
REGION = input("Enter your AWS Region (e.g., us-east-1): ").strip()

# Get instance ID from user
INSTANCE_ID = input("Enter the EC2 Instance ID: ").strip()

# Get tags from user
tags = []
while True:
    key = input("Enter tag key (or press Enter to stop): ").strip()
    if not key:
        break
    value = input(f"Enter value for '{key}': ").strip()
    tags.append({"Key": key, "Value": value})

def add_tags_to_instance(instance_id, tags):
    try:
        ec2 = boto3.client(
            "ec2",
            aws_access_key_id=ACCESS_KEY,
            aws_secret_access_key=SECRET_KEY,
            region_name=REGION,
        )

        ec2.create_tags(Resources=[instance_id], Tags=tags)
        print(f"Tags {tags} added successfully to instance {instance_id}")

    except Exception as e:
        print(f"Error adding tags: {e}")

# Call the function
if tags:
    add_tags_to_instance(INSTANCE_ID, tags)
else:
    print("No tags provided. Exiting.")

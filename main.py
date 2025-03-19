from flask import Blueprint, render_template, flash, redirect, url_for, request
from flask_login import login_required, current_user
import boto3

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/profile')
@login_required
def profile():
    return render_template('profile.html', name=current_user.name)

@main.route('/aws')
@login_required
def aws():
    # ✅ Fetch credentials from the `Users` table
    aws_access_key = current_user.access
    aws_secret_key = current_user.secret
    aws_region = "us-east-1"

    if not aws_access_key or not aws_secret_key:
        return "Error: AWS credentials not found in the user profile", 401

    try:
        # ✅ Connect to EC2 using user's credentials
        ec2_client = boto3.client(
            'ec2',
            aws_access_key_id=aws_access_key,
            aws_secret_access_key=aws_secret_key,
            region_name=aws_region
        )

        # ✅ Fetch instance details
        response = ec2_client.describe_instances()
        instances = []
        for reservation in response['Reservations']:
            for instance in reservation['Instances']:
                instances.append({
                    'InstanceId': instance.get('InstanceId'),
                    'InstanceType': instance.get('InstanceType'),
                    'State': instance['State']['Name'],
                    'PublicIp': instance.get('PublicIpAddress', 'N/A'),
                    'PrivateIp': instance.get('PrivateIpAddress', 'N/A'),
                    'Name': next((tag['Value'] for tag in instance.get('Tags', []) if tag['Key'] == 'Name'), 'Unnamed')
                })

        # ✅ Send data to aws.html
        return render_template('aws.html', instances=instances)

    except Exception as e:
        return f"Error fetching EC2 details: {e}", 500
@main.route('/rename_instance/<instance_id>', methods=['GET', 'POST'])
@login_required
def rename_instance(instance_id):
    """Handle renaming of an EC2 instance"""
    if request.method == 'POST':
        new_name = request.form.get('new_name')

        if not new_name:
            flash("New name is required!", "danger")
            return redirect(url_for('main.rename_instance', instance_id=instance_id))

        # ✅ Fetch AWS credentials from the user's profile
        aws_access_key = current_user.access
        aws_secret_key = current_user.secret
        aws_region = "us-east-1"

        try:
            # ✅ Connect to EC2
            ec2_client = boto3.client(
                'ec2',
                aws_access_key_id=aws_access_key,
                aws_secret_access_key=aws_secret_key,
                region_name=aws_region
            )

            # ✅ Rename the instance by updating its tag
            ec2_client.create_tags(
                Resources=[instance_id],
                Tags=[{"Key": "Name", "Value": new_name}]
            )

            flash(f"Instance {instance_id} renamed to {new_name}", "success")
            return redirect(url_for('main.aws'))  # Redirect back to AWS dashboard

        except Exception as e:
            app.logger.error(f"Error renaming instance {instance_id}: {str(e)}")
            flash(f"Error renaming instance: {str(e)}", "danger")
            return redirect(url_for('main.rename_instance', instance_id=instance_id))

    # **Render the rename form for GET requests**
    return render_template('rename_instance.html', instance_id=instance_id)
@main.route('/ec2_add_tags/<instance_id>',methods=['GET'])
@login_required
def ec2_add_tags(instance_id):
    """ Render a form to add tags to an EC2 instance """
    return render_template('add_tags.html', instance_id=instance_id)

@main.route('/add_tags', methods=['POST'])
@login_required
def add_tags():
    """ Handle adding tags to an EC2 instance """
    instance_id = request.form.get('instance_id')
    tag_key = request.form.get('tag_key')
    tag_value = request.form.get('tag_value')

    if not instance_id or not tag_key or not tag_value:
        flash("Instance ID, tag key, and tag value are required!", "danger")
        return redirect(url_for('main.aws'))

    # ✅ Fetch AWS credentials from the user's profile
    aws_access_key = current_user.access
    aws_secret_key = current_user.secret
    aws_region = "us-east-1"

    try:
        # ✅ Connect to EC2
        ec2_client = boto3.client(
            'ec2',
            aws_access_key_id=aws_access_key,
            aws_secret_access_key=aws_secret_key,
            region_name=aws_region
        )

        # ✅ Add tags to the instance
        ec2_client.create_tags(
            Resources=[instance_id],
            Tags=[{"Key": tag_key, "Value": tag_value}]
        )

        flash(f"Tag '{tag_key}: {tag_value}' added to Instance {instance_id}", "success")
        return redirect(url_for('main.aws'))  # Redirect back to the AWS dashboard

    except Exception as e:
        flash(f"Error adding tag: {e}", "danger")
        return redirect(url_for('main.aws'))
@main.route('/ec2_view_tags/<instance_id>')
@login_required
def ec2_view_tags(instance_id):
    """ Fetch and display tags of an EC2 instance """
    aws_access_key = current_user.access
    aws_secret_key = current_user.secret
    aws_region = "us-east-1"

    try:
        # ✅ Connect to EC2
        ec2_client = boto3.client(
            'ec2',
            aws_access_key_id=aws_access_key,
            aws_secret_access_key=aws_secret_key,
            region_name=aws_region
        )

        # ✅ Fetch instance details
        response = ec2_client.describe_instances(InstanceIds=[instance_id])
        instance = response['Reservations'][0]['Instances'][0]

        # ✅ Extract tags
        tags = instance.get('Tags', [])

        return render_template('view_tags.html', instance_id=instance_id, tags=tags)

    except Exception as e:
        flash(f"Error fetching tags: {e}", "danger")
        return redirect(url_for('main.aws'))
@main.route('/ec2/toggle/<instance_id>/<action>',methods=['POST'])
@login_required
def ec2_toggle_instance(instance_id, action):
    aws_access_key = current_user.access
    aws_secret_key = current_user.secret
    aws_region = "us-east-1"

    if not aws_access_key or not aws_secret_key:
        return "Error: AWS credentials not found in the user profile", 401

    try:
        ec2_client = boto3.client(
            'ec2',
            aws_access_key_id=aws_access_key,
            aws_secret_access_key=aws_secret_key,
            region_name=aws_region
        )

        if action == "start":
            ec2_client.start_instances(InstanceIds=[instance_id])
        elif action == "stop":
            ec2_client.stop_instances(InstanceIds=[instance_id])

        return redirect(url_for('main.aws'))

    except Exception as e:
        return f"Error: {e}", 500
@main.route('/azure')
@login_required  # ✅ Place it outside the function
def azure():
    #return render_template('profile.html', name=current_user.name)  # ✅ Ensure return statement
    print("hello from azure")

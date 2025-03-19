from flask import Blueprint, render_template
from flask_login import login_required, current_user
from azure.identity import ClientSecretCredential
from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.network import NetworkManagementClient
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from azure.identity import ClientSecretCredential
from azure.mgmt.compute import ComputeManagementClient
#from azure.mgmt.resource import ResourceManagementClient  # Import for tagging

azure_fun = Blueprint('azure_fun', __name__)

@azure_fun.route('/dashboard')
@login_required
def dashboard():
    # Get Azure credentials from the current user
    client_id = current_user.client_id
    tenant_id = current_user.tenant_id
    client_secret = current_user.client_secret
    subscription_id = current_user.subscription_id

    if not (client_id and tenant_id and client_secret and subscription_id):
        return "Azure credentials are missing!", 400

    # Authenticate with Azure
    credential = ClientSecretCredential(tenant_id, client_id, client_secret)

    # Initialize Azure clients
    compute_client = ComputeManagementClient(credential, subscription_id)
    network_client = NetworkManagementClient(credential, subscription_id)

    # Fetch all Virtual Machines
    vms = []
    for vm in compute_client.virtual_machines.list_all():
        # Get the VM state
        instance_view = compute_client.virtual_machines.instance_view(vm.id.split("/")[-5], vm.name)
        statuses = instance_view.statuses
        vm_state = statuses[-1].display_status if statuses else "Unknown"

        # Get Public & Private IP
        public_ip, private_ip = None, None
        nic_id = vm.network_profile.network_interfaces[0].id
        nic_name = nic_id.split("/")[-1]
        nic_resource_group = nic_id.split("/")[4]
        nic = network_client.network_interfaces.get(nic_resource_group, nic_name)

        if nic.ip_configurations:
            private_ip = nic.ip_configurations[0].private_ip_address
            if nic.ip_configurations[0].public_ip_address:
                public_ip_id = nic.ip_configurations[0].public_ip_address.id
                public_ip_name = public_ip_id.split("/")[-1]
                public_ip_resource_group = public_ip_id.split("/")[4]
                public_ip = network_client.public_ip_addresses.get(public_ip_resource_group, public_ip_name).ip_address

        # Append VM data
        vms.append({
            "name": vm.name,
            "resource_group": vm.id.split("/")[4],  # Extract resource group
            "region": vm.location,
            "size": vm.hardware_profile.vm_size,
            "state": vm_state.split()[-1].lower(),
            "public_ip": public_ip,
            "private_ip": private_ip,
        })

    # Render the dashboard template with VM data
    return render_template("azure_dash.html", vms=vms)


@azure_fun.route('/addtags', methods=['GET', 'POST'])
@login_required
def addtags():
    if request.method == 'POST':
        resource_group = request.form.get("resource_group")
        vm_name = request.form.get("vm_name")
        key = request.form.get("tag_key")
        value = request.form.get("tag_value")

        if not (resource_group and vm_name and key and value):
            return "Missing required fields", 400

        # Authenticate with Azure
        client_id = current_user.client_id
        tenant_id = current_user.tenant_id
        client_secret = current_user.client_secret
        subscription_id = current_user.subscription_id
        credential = ClientSecretCredential(tenant_id, client_id, client_secret)
        compute_client = ComputeManagementClient(credential, subscription_id)

        # Fetch VM
        vm = compute_client.virtual_machines.get(resource_group, vm_name)

        # Update VM tags
        tags = vm.tags if vm.tags else {}
        tags[key] = value
        compute_client.virtual_machines.begin_update(resource_group, vm_name, {"tags": tags})

        flash(f"Tag '{key}: {value}' added to {vm_name} successfully!", "success")
        return redirect(url_for('azure_fun.dashboard'))

    # If it's a GET request, render the form
    resource_group = request.args.get("resource_group")
    vm_name = request.args.get("vm_name")
    return render_template("add_tags_azure.html", resource_group=resource_group, vm_name=vm_name)
@azure_fun.route('/viewtags/<resource_group>/<vm_name>')
@login_required
def viewtags(resource_group, vm_name):
    # Authenticate with Azure
    client_id = current_user.client_id
    tenant_id = current_user.tenant_id
    client_secret = current_user.client_secret
    subscription_id = current_user.subscription_id

    if not (client_id and tenant_id and client_secret and subscription_id):
        return "Azure credentials are missing!", 400

    credential = ClientSecretCredential(tenant_id, client_id, client_secret)
    compute_client = ComputeManagementClient(credential, subscription_id)

    # Fetch VM details
    vm = compute_client.virtual_machines.get(resource_group, vm_name)

    # Get tags
    tags = vm.tags if vm.tags else {}

    return render_template("view_tags_azure.html", vm_name=vm_name, tags=tags)
@azure_fun.route('/start_vm/<resource_group>/<vm_name>', methods=['POST'])
@login_required
def start_vm(resource_group, vm_name):
    # Authenticate with Azure
    client_id = current_user.client_id
    tenant_id = current_user.tenant_id
    client_secret = current_user.client_secret
    subscription_id = current_user.subscription_id

    credential = ClientSecretCredential(tenant_id, client_id, client_secret)
    compute_client = ComputeManagementClient(credential, subscription_id)

    try:
        # Start the VM
        compute_client.virtual_machines.begin_start(resource_group, vm_name)
        flash(f"VM {vm_name} is starting!", "success")
    except Exception as e:
        flash(f"Error starting VM {vm_name}: {str(e)}", "danger")

    return redirect(url_for('azure_fun.dashboard'))


@azure_fun.route('/stop_vm/<resource_group>/<vm_name>', methods=['POST'])
@login_required
def stop_vm(resource_group, vm_name):
    # Authenticate with Azure
    client_id = current_user.client_id
    tenant_id = current_user.tenant_id
    client_secret = current_user.client_secret
    subscription_id = current_user.subscription_id

    credential = ClientSecretCredential(tenant_id, client_id, client_secret)
    compute_client = ComputeManagementClient(credential, subscription_id)

    try:
        # Stop the VM
        compute_client.virtual_machines.begin_power_off(resource_group, vm_name)
        flash(f"VM {vm_name} is stopping!", "success")
    except Exception as e:
        flash(f"Error stopping VM {vm_name}: {str(e)}", "danger")

    return redirect(url_for('azure_fun.dashboard'))
@azure_fun.route('/restart_vm', methods=['POST'])
@login_required
def restart_vm():
    resource_group = request.args.get("resource_group")
    vm_name = request.args.get("vm_name")

    if not (resource_group and vm_name):
        return "Missing VM details", 400

    # Authenticate with Azure
    client_id = current_user.client_id
    tenant_id = current_user.tenant_id
    client_secret = current_user.client_secret
    subscription_id = current_user.subscription_id
    credential = ClientSecretCredential(tenant_id, client_id, client_secret)
    compute_client = ComputeManagementClient(credential, subscription_id)

    # Restart VM
    compute_client.virtual_machines.begin_restart(resource_group, vm_name)

    flash(f"Restarting {vm_name} in {resource_group}!", "info")
    return redirect(url_for('azure_fun.dashboard'))

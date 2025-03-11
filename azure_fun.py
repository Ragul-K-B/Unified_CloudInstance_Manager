from flask import Blueprint, render_template
from flask_login import login_required, current_user
from azure.identity import ClientSecretCredential
from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.network import NetworkManagementClient

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

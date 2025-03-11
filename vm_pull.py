from azure_fun.identity import ClientSecretCredential
from azure_fun.mgmt.compute import ComputeManagementClient
from azure_fun.mgmt.resource import SubscriptionClient
import json

# 🔹 Replace these values with your actual credentials
TENANT_ID = "ed72a49a-602e-4dbb-962b-ebe01c989242"
CLIENT_ID = "662b1a16-ca66-45f3-bc2a-cb5ac38045e9"
CLIENT_SECRET = "rfN8Q~gdIRhNQJiSH07yA6vf~GLynp0p44HeLb~4"  # ⚠ Store securely, don't hardcode

SUBSCRIPTION_ID = "7a042b9a-1cba-48c1-a158-a054c137c7ad"
RESOURCE_GROUP = "miniproject_group"

# 🔹 Authenticate using ClientSecretCredential
credential = ClientSecretCredential(
    tenant_id=TENANT_ID,
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET
)

# 🔹 Initialize Compute Client
compute_client = ComputeManagementClient(credential, SUBSCRIPTION_ID)

# 🔹 Function to print VM details
def print_vm_details(vm):
    """Print detailed VM information"""
    print(f"\n🔹 VM Name: {vm.name}")
    print(f"   - Location: {vm.location}")
    print(f"   - Resource Group: {vm.id.split('/')[4]}")
    print(f"   - VM Size: {vm.hardware_profile.vm_size}")

    # OS Information
    if vm.storage_profile.os_disk:
        os_disk = vm.storage_profile.os_disk
        print(f"   - OS Type: {vm.storage_profile.os_disk.os_type}")
        print(f"   - OS Disk Name: {os_disk.name}, Type: {os_disk.managed_disk.storage_account_type}")

    # Network Information
    if vm.network_profile.network_interfaces:
        print(f"   - Network Interfaces:")
        for nic in vm.network_profile.network_interfaces:
            print(f"     - {nic.id}")

    # Print full VM JSON data
    print(f"\n   🔸 Full VM Data:\n{json.dumps(vm.as_dict(), indent=4)}")


# 🔹 List all VMs in the subscription
print("\n✅ Listing All VMs in Subscription:")
vm_found = False
for vm in compute_client.virtual_machines.list_all():
    print_vm_details(vm)
    vm_found = True

if not vm_found:
    print("\n❌ No VMs found. Check if the service principal has the right permissions.")

# 🔹 List VMs in the specific resource group
print(f"\n✅ Checking VMs in Resource Group: {RESOURCE_GROUP}")
try:
    vms = compute_client.virtual_machines.list(RESOURCE_GROUP)
    for vm in vms:
        print_vm_details(vm)
        vm_found = True
except Exception as e:
    print(f"\n❌ Error: Unable to access resource group '{RESOURCE_GROUP}'.\n{e}")

if not vm_found:
    print("\n❌ No VMs found in the specified resource group.")

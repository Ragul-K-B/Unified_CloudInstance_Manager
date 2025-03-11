import requests
from azure_fun.identity import ClientSecretCredential

# Authentication details
TENANT_ID = "ed72a49a-602e-4dbb-962b-ebe01c989242"
CLIENT_ID = "662b1a16-ca66-45f3-bc2a-cb5ac38045e9"
CLIENT_SECRET = "rfN8Q~gdIRhNQJiSH07yA6vf~GLynp0p44HeLb~4"  # ⚠ Store securely, don't hardcode

SUBSCRIPTION_ID = "7a042b9a-1cba-48c1-a158-a054c137c7ad"
RESOURCE_GROUP = "miniproject_group"
# Authenticate using ClientSecretCredential
credential = ClientSecretCredential(
    tenant_id=TENANT_ID,
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET
)

# Obtain an access token
token = credential.get_token("https://management.azure.com/.default").token

# Set the API version
API_VERSION = "2024-07-01"

# Define the initial URL to list all VMs in the resource group
url = f"https://management.azure.com/subscriptions/{SUBSCRIPTION_ID}/resourceGroups/{RESOURCE_GROUP}/providers/Microsoft.Compute/virtualMachines?api-version={API_VERSION}"

# Set the headers, including the Authorization bearer token
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

# Function to get VMs with pagination
def get_vms(url):
    vms = []
    while url:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise an error for bad status codes
        data = response.json()
        vms.extend(data.get('value', []))
        url = data.get('nextLink')  # Get the next page URL
    return vms

# Retrieve all VMs
vm_list = get_vms(url)

# Check if VMs are found
if not vm_list:
    print("\n❌ No VMs found in the subscription.")
else:
    print("\n✅ Listing All VMs in Subscription:")
    for vm in vm_list:
        print(f"🔹 VM Name: {vm['name']}, Resource Group: {vm['id'].split('/')[4]}")

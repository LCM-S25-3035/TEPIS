import requests

# ✅ Base URL for the City of Toronto CKAN Open Data API
base_url = "https://ckan0.cf.opendata.inter.prod-toronto.ca"

# ✅ Get metadata for the "festivals-events" package
package_url = f"{base_url}/api/3/action/package_show"
params = { "id": "festivals-events" }

# Fetch package metadata
response = requests.get(package_url, params=params)

# Check if the request was successful
if response.status_code == 200:
    package = response.json()

    # ✅ Iterate through resources in the package
    for idx, resource in enumerate(package["result"]["resources"]):
        print(f"\nResource #{idx + 1}: {resource['name']}")
        print(f"Format: {resource['format']}")
        print(f"Datastore Active: {resource['datastore_active']}")
        print(f"Resource ID: {resource['id']}")

        # ✅ If it's not in the datastore, get direct download URL
        if not resource["datastore_active"]:
            resource_url = f"{base_url}/api/3/action/resource_show?id={resource['id']}"
            resource_metadata = requests.get(resource_url).json()

            # Get download URL
            download_url = resource_metadata["result"]["url"]
            print(f"Download URL: {download_url}")

        else:
            # ✅ If it's a datastore resource, fetch first 5 records
            data_url = f"{base_url}/api/3/action/datastore_search"
            data_params = {"resource_id": resource["id"], "limit": 5}
            data = requests.get(data_url, params=data_params).json()

            print("Sample Records:")
            for record in data["result"]["records"]:
                print(record)

else:
    print(f"Failed to retrieve package metadata: {response.status_code}")

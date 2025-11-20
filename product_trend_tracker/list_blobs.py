from azure.storage.blob import BlobServiceClient

CONNECTION_STR = "DefaultEndpointsProtocol=https;AccountName=producttrendstorage2025;AccountKey=ODlteOmY3kA1ElkbXF3GKPj4kp1qXet9von78KhS2X6x2skX1hqpRopAhLkx83VcJkl39/gDq27f+AStBsqMoQ==;EndpointSuffix=core.windows.net"
CONTAINER_NAME = "snapshots"

blob_service_client = BlobServiceClient.from_connection_string(CONNECTION_STR)
container_client = blob_service_client.get_container_client(CONTAINER_NAME)

print("\nListing blobs in container:\n")
for blob in container_client.list_blobs():
    print(f"{blob.name}    |    {blob.size} bytes    |    Last Modified: {blob.last_modified}")

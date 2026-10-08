import grpc

from proto import storage_pb2
from proto import storage_pb2_grpc


SERVER_ADDRESS = "localhost:50051"


with open("certs/ca.crt", "rb") as f:
    ca_cert = f.read()


credentials = grpc.ssl_channel_credentials(
    root_certificates=ca_cert
)

channel = grpc.secure_channel(
    SERVER_ADDRESS,
    credentials
)

stub = storage_pb2_grpc.FileStorageStub(channel)

request = storage_pb2.DownloadRequest(
    filename="test.txt"
)

try:
    response = stub.Download(request)

    print("Request berhasil:")
    print(response.message)

except grpc.RpcError as e:
    print("Request ditolak")
    print("Status:", e.code())
    print("Detail:", e.details())

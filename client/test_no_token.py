import grpc

from proto import storage_pb2
from proto import storage_pb2_grpc


channel = grpc.insecure_channel("localhost:50051")

stub = storage_pb2_grpc.FileStorageStub(channel)

request = storage_pb2.DownloadRequest(
    filename="test.txt"
)

try:
    response = stub.Download(request)

    print(response.message)

except grpc.RpcError as e:
    print("REQUEST DITOLAK")
    print("Status:", e.code())
    print("Pesan:", e.details())

import sys
import os

import grpc

from proto import storage_pb2
from proto import storage_pb2_grpc

from server.auth import generate_token


SERVER_ADDRESS = "localhost:50051"


def create_metadata(role="user"):
    token = generate_token("maulana", role)

    return [
        ("authorization", f"Bearer {token}")
    ]

def create_secure_channel():
    with open("certs/ca.crt", "rb") as f:
        ca_cert = f.read()

    with open("certs/client.crt", "rb") as f:
        client_cert = f.read()

    with open("certs/client.key", "rb") as f:
        client_key = f.read()

    credentials = grpc.ssl_channel_credentials(
        root_certificates=ca_cert,
        private_key=client_key,
        certificate_chain=client_cert
    )

    return grpc.secure_channel(
        SERVER_ADDRESS,
        credentials
    )

def upload_file(filename, role):
    channel = create_secure_channel()
    stub = storage_pb2_grpc.FileStorageStub(channel)

    with open(filename, "rb") as f:
        content = f.read()

    request = storage_pb2.UploadRequest(
        filename=os.path.basename(filename),
        content=content
    )

    response = stub.Upload(
        request,
        metadata=create_metadata(role)
    )
    print(response.message)


def download_file(filename, role):
    channel = create_secure_channel()
    stub = storage_pb2_grpc.FileStorageStub(channel)

    request = storage_pb2.DownloadRequest(
        filename=filename
    )

    response = stub.Download(
        request,
        metadata=create_metadata(role)
    )

    if not response.success:
        print(response.message)
        return

    output_file = "downloaded_" + filename

    with open(output_file, "wb") as f:
        f.write(response.content)

    print(response.message)
    print(f"File disimpan sebagai: {output_file}")


def main():
    if len(sys.argv) < 3:
        print("Penggunaan:")
        print("  python client/client.py upload <file> [role]")
        print("  python client/client.py download <file> [role]")
        return

    command = sys.argv[1]
    filename = sys.argv[2]

    role = "user"

    if len(sys.argv) >= 4:
        role = sys.argv[3]

    if command == "upload":
        upload_file(filename, role)

    elif command == "download":
        download_file(filename, role)

    else:
        print("Command tidak dikenal")

if __name__ == "__main__":
    main()

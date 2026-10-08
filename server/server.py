import os
from concurrent import futures

import grpc

from proto import storage_pb2
from proto import storage_pb2_grpc

from server.security import calculate_sha256
from server.checksum import save_checksum, get_checksum
from server.auth import verify_token
from server.rbac import has_permission
from server.labels import get_security_label
from server.audit import write_audit_log


STORAGE_DIR = "storage"


class AuthInterceptor(grpc.ServerInterceptor):

    def intercept_service(self, continuation, handler_call_details):

        metadata = dict(
            handler_call_details.invocation_metadata
        )

        auth_header = metadata.get("authorization")

        if not auth_header:
            return self.unauthenticated_handler(
                "JWT token diperlukan"
            )

        if not auth_header.startswith("Bearer "):
            return self.unauthenticated_handler(
                "Format token tidak valid"
            )

        token = auth_header.split(" ", 1)[1]

        payload = verify_token(token)

        if payload is None:
            return self.unauthenticated_handler(
                "JWT token tidak valid atau sudah expired"
            )

        handler = continuation(handler_call_details)

        if handler is None:
            return None

        def unary_unary(request, context):

            context.user = payload.get("username")
            context.role = payload.get("role")

            return handler.unary_unary(
                request,
                context
            )

        return grpc.unary_unary_rpc_method_handler(
            unary_unary,
            request_deserializer=handler.request_deserializer,
            response_serializer=handler.response_serializer
        )

    def unauthenticated_handler(self, message):

        def deny(request, context):

            context.abort(
                grpc.StatusCode.UNAUTHENTICATED,
                message
            )

        return grpc.unary_unary_rpc_method_handler(
            deny
        )


class FileStorageServicer(
    storage_pb2_grpc.FileStorageServicer
):

    def Upload(self, request, context):

        username = getattr(
            context,
            "user",
            None
        )

        role = getattr(
            context,
            "role",
            None
        )

        security_label = get_security_label(
            request.filename
        )

        if not has_permission(
            role,
            security_label
        ):

            write_audit_log(
                username,
                role,
                "UPLOAD",
                request.filename,
                security_label,
                "DENIED"
            )

            context.abort(
                grpc.StatusCode.PERMISSION_DENIED,
                (
                    f"Akses ditolak. Role '{role}' "
                    f"tidak memiliki izin untuk file "
                    f"{security_label}"
                )
            )

        os.makedirs(
            STORAGE_DIR,
            exist_ok=True
        )

        filepath = os.path.join(
            STORAGE_DIR,
            request.filename
        )

        with open(filepath, "wb") as f:
            f.write(request.content)

        checksum = calculate_sha256(
            request.content
        )

        save_checksum(
            request.filename,
            checksum
        )

        write_audit_log(
            username,
            role,
            "UPLOAD",
            request.filename,
            security_label,
            "SUCCESS"
        )

        print(
            f"[UPLOAD] {request.filename}"
        )

        print(
            f"[USER] {username}"
        )

        print(
            f"[ROLE] {role}"
        )

        print(
            f"[LABEL] {security_label}"
        )

        print(
            f"[SHA-256] {checksum}"
        )

        return storage_pb2.UploadResponse(
            success=True,
            message=(
                f"File {request.filename} "
                f"berhasil di-upload. "
                f"SHA-256: {checksum}"
            )
        )

    def Download(self, request, context):

        username = getattr(
            context,
            "user",
            None
        )

        role = getattr(
            context,
            "role",
            None
        )

        security_label = get_security_label(
            request.filename
        )

        if not has_permission(
            role,
            security_label
        ):

            write_audit_log(
                username,
                role,
                "DOWNLOAD",
                request.filename,
                security_label,
                "DENIED"
            )

            context.abort(
                grpc.StatusCode.PERMISSION_DENIED,
                (
                    f"Akses ditolak. Role '{role}' "
                    f"tidak memiliki izin untuk file "
                    f"{security_label}"
                )
            )

        filepath = os.path.join(
            STORAGE_DIR,
            request.filename
        )

        if not os.path.exists(filepath):

            write_audit_log(
                username,
                role,
                "DOWNLOAD",
                request.filename,
                security_label,
                "NOT_FOUND"
            )

            return storage_pb2.DownloadResponse(
                success=False,
                message="File tidak ditemukan"
            )

        with open(filepath, "rb") as f:
            content = f.read()

        actual_checksum = calculate_sha256(
            content
        )

        expected_checksum = get_checksum(
            request.filename
        )

        print(
            f"[DOWNLOAD] {request.filename}"
        )

        print(
            f"[USER] {username}"
        )

        print(
            f"[ROLE] {role}"
        )

        print(
            f"[LABEL] {security_label}"
        )

        print(
            f"[EXPECTED SHA-256] {expected_checksum}"
        )

        print(
            f"[ACTUAL SHA-256]   {actual_checksum}"
        )

        if expected_checksum != actual_checksum:

            write_audit_log(
                username,
                role,
                "DOWNLOAD",
                request.filename,
                security_label,
                "INTEGRITY_FAILED"
            )

            print(
                "[INTEGRITY FAILED] "
                "File telah berubah!"
            )

            return storage_pb2.DownloadResponse(
                success=False,
                message=(
                    "INTEGRITY FAILED: "
                    "Checksum file tidak sesuai"
                )
            )

        write_audit_log(
            username,
            role,
            "DOWNLOAD",
            request.filename,
            security_label,
            "SUCCESS"
        )

        return storage_pb2.DownloadResponse(
            success=True,
            message=(
                f"File {request.filename} "
                f"integrity OK. "
                f"SHA-256: {actual_checksum}"
            ),
            content=content
        )


def serve():
    os.makedirs(STORAGE_DIR, exist_ok=True)

    with open("certs/server.key", "rb") as f:
        server_key = f.read()

    with open("certs/server.crt", "rb") as f:
        server_cert = f.read()

    with open("certs/ca.crt", "rb") as f:
        ca_cert = f.read()

    server_credentials = grpc.ssl_server_credentials(
        [(server_key, server_cert)],
        root_certificates=ca_cert,
        require_client_auth=True
    )

    server = grpc.server(
        futures.ThreadPoolExecutor(max_workers=10),
        interceptors=[AuthInterceptor()]
    )

    storage_pb2_grpc.add_FileStorageServicer_to_server(
        FileStorageServicer(),
        server
    )

    server.add_secure_port(
        "[::]:50051",
        server_credentials
    )

    server.start()

    print("=================================")
    print(" Secure File Storage Server")
    print(" gRPC TLS/mTLS aktif")
    print(" Port: 50051")
    print(" JWT Authentication aktif")
    print(" RBAC + Security Label aktif")
    print(" Audit Log aktif")
    print("=================================")

    server.wait_for_termination()

if __name__ == "__main__":
    serve()

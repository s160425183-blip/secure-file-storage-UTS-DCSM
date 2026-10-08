from server.auth import generate_token


username = "maulana"
role = "user"

token = generate_token(username, role)

print("JWT TOKEN:")
print(token)

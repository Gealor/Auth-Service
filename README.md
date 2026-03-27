# Генерация приватного и публичного ключей
Вводить команды в корневой папке проекта, не в src.
Приватный ключ:

```shell
# Generate an RSA private key, of size 2048
openssl genrsa -out src/core/auth/certs/jwt-private.pem 2048
```

Публичный ключ:

```shell
# Extract the public key from the key pair, which can be used in a certificate
openssl rsa -in src/core/auth/certs/jwt-private.pem -outform PEM -pubout -out src/core/auth/certs/jwt-public.pem
```

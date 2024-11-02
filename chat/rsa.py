import random
import base64
from pyasn1.codec.der.encoder import encode
from pyasn1.codec.der.decoder import decode
from pyasn1.type.univ import Sequence, Integer


def gcd(a, b):
    # PGDC (récursif)
    if b == 0:
        return a
    else:
        return gcd(b, a % b)


def is_prime(n, k=40):
    # Test de primalité de Miller-Rabin
    # n -> nombre à tester
    # k -> nombre de fois à essayer le test de primalité

    # si le nombre est 2, il est premier
    if n == 2:
        return True

    # si le nombre est pair et plus grand que 2, le nombre n'est pas premier
    if n % 2 == 0 and n > 2:
        return False

    s = 0
    t = n - 1

    while t % 2 == 0:
        s += 1
        t = t // 2
    # n - 1 = 2**s*t

    for i in range(k):
        a = random.randint(2, n - 1)
        # x est congru à a**t modulo n
        x = pow(a, t, n)
        if x == 1 or x == n - 1:
            continue
        for i in range(s):
            # x est congru à x**2 modulo n
            x = pow(x, 2, n)
            if x == n - 1:
                break
        else:
            return False
    # Le nombre est probablement premier
    return True


def random_prime_number(dg):
    # Genère un nombre premier de grandeur dg
    min = 10 ** (dg - 1)
    max = 10 ** dg - 1
    n = random.randint(min, max)
    if n % 2 == 0:
        n -= 1
    while True:
        if is_prime(n, 40):
            return n
        n += 2


def create_public_exponent(phi):
    # Genère l'exposant de chiffrement
    while True:
        e = random_prime_number(7)
        # l'exposant est strictement infériereur à phi et plus grand que 1 et est premier avec phi
        if 1 < e < phi and gcd(e, phi) == 1:
            return e


def create_private_exponent(e, phi):
    # Genère l'exposant de déchiffrement
    # d est congru à e**-1 modulo phi (inverse modulaire)
    d = pow(e, -1, phi)
    return d


# Clé publique (données partageable) -> n, e
# Clé privée (données non partageable) -> p, q, d

def privatekey_to_pem(n, e, d, p, q):
    # PKCS #1
    # https://crypto.stackexchange.com/questions/25498/how-to-create-a-pem-file-for-storing-an-rsa-key

    dp = d % (p - 1)
    dq = d % (q - 1)
    qinv = pow(q, -1, p)
    # Header et footer du ficher
    template = '-----BEGIN RSA PRIVATE KEY-----\n{}-----END RSA PRIVATE KEY-----\n'
    seq = Sequence()
    for i, x in enumerate((0, n, e, d, p, q, dp, dq, qinv)):
        seq.setComponentByPosition(i, Integer(x))
    der = encode(seq)
    return template.format(base64.encodebytes(der).decode('ascii'))


def publickey_to_pem(n, e):
    # PKCS #1
    # Header et footer du ficher
    template = '-----BEGIN RSA PUBLIC KEY-----\n{}-----END RSA PUBLIC KEY-----\n'
    seq = Sequence()
    for i, x in enumerate((n, e)):
        seq.setComponentByPosition(i, Integer(x))
    der = encode(seq)
    return template.format(base64.encodebytes(der).decode('ascii'))


def pem_to_privatekey(key):
    # Enlève le header et le footer
    header = "-----BEGIN RSA PRIVATE KEY-----"
    footer = "-----END RSA PRIVATE KEY-----"
    key = key.replace(header, "")
    key = key.replace(footer, "")
    key = key.strip()
    # Base64 en DER
    der = base64.b64decode(key)
    # Decodage du DER
    seq, _ = decode(der)
    # Sequence en liste de nombre entiers (dans l'ordre (0, n, e, d, p, q, dP, dQ, qInv))
    key_int = []
    for i in seq:
        key_int.append(int(i))
    return key_int


def pem_to_publickey(key):
    # Enlève le header et le footer
    header = "-----BEGIN RSA PUBLIC KEY-----"
    footer = "-----END RSA PUBLIC KEY-----"
    key = key.replace(header, "")
    key = key.replace(footer, "")
    key = key.strip()
    # Base64 en DER
    der = base64.b64decode(key)
    # Decodage du DER
    seq, _ = decode(der)
    # Sequence en liste de nombre entiers (dans l'ordre (n, e))
    key_int = []
    for i in seq:
        key_int.append(int(i))
    return key_int


def str_to_int(m):
    m_bytes = m.encode("utf-8")
    m_int = int.from_bytes(m_bytes, byteorder="big")
    return m_int


def int_to_str(m_int):
    # Taille de byte est variante (à comprendre !)
    nb_bytes = 255
    m_bytes = m_int.to_bytes(nb_bytes, byteorder="big")
    m = m_bytes.decode("utf-8")
    return m


def message_encrypt(m, e, n):
    # c est congru à m**e modulo n
    c = pow(m, e, n)
    return c


def message_decrypt(c, d, n):
    # m est congru à c**d modulo n
    m = pow(c, d, n)
    return m

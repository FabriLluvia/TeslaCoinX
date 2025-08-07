import hashlib

def firmar_transaccion(clave_privada, desde, hacia, monto):
    """
    Crea una firma simple basada en los datos de la transacción y la clave privada.
    """
    contenido = f"{desde}{hacia}{monto}{clave_privada}"
    return hashlib.sha256(contenido.encode()).hexdigest()

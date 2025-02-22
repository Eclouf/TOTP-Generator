import hmac
import hashlib
import time
import base64

def generate_totp_secret(secret_key: str, algo: str = 'sha1', digits: int = 6, period: int = 30) -> str:
    """
    Génère une clé TOTP à partir d'une clé secrète en suivant la RFC 6238.

    :param secret_key: La clé secrète en Base32 à utiliser pour la génération
    :param algo: L'algorithme de hachage à utiliser (sha1, sha256, sha512)
    :param digits: Le nombre de chiffres de la clé TOTP (par défaut : 6)
    :param period: La période de temps pour la clé TOTP (par défaut : 30 secondes)
    :return: La clé TOTP sous forme de chaîne de caractères
    """
    try:
        # Normaliser et padding de la clé Base32
        secret_key = secret_key.upper().strip()
        padding = '=' * ((8 - len(secret_key) % 8) % 8)
        padded_secret = (secret_key + padding).encode('utf-8')
        
        # Décoder la clé Base32
        key = base64.b32decode(padded_secret)
        
        # Obtenir le compteur de temps
        counter = int(time.time() // period)
        
        # Convertir le compteur en bytes (8 octets, big-endian)
        counter_bytes = counter.to_bytes(8, 'big')
        
        # Calculer le HMAC
        hash_algo = getattr(hashlib, algo.lower())
        hmac_obj = hmac.new(key, counter_bytes, hash_algo)
        hmac_result = hmac_obj.digest()

        # Générer le code TOTP selon la RFC 6238
        offset = hmac_result[-1] & 0xf
        code_bytes = hmac_result[offset:offset + 4]
        code = int.from_bytes(code_bytes, 'big') & 0x7fffffff
        totp_value = code % (10 ** digits)

        return str(totp_value).zfill(digits)

    except base64.binascii.Error:
        raise ValueError("La clé secrète n'est pas un format Base32 valide")
    except Exception as e:
        raise ValueError(f"Erreur lors de la génération du code TOTP: {str(e)}")
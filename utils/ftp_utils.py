from ftplib import FTP


def connecion_to_ftp(host, username, password, logger=None):
    try:
        logger.info(f"Connexion FTP...")
        ftp = FTP(host)
        ftp = ftp.login(host, username, password)
        if logger:
            logger.info(f"Connexion FTP réussie")
        return ftp
    except Exception as e:
        if logger:
            logger.error(f"Erreur lors de la connexion FTP : {e}")
        raise e

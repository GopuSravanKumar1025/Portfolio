import logging
import socket
from pynetdicom import AE, StoragePresentationContexts
from pydicom import dcmread
from pydicom.errors import InvalidDicomError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_tcp_connectivity(remote_host: str, remote_port: int):
    try:
        with socket.create_connection((remote_host, remote_port), timeout=5):
            logger.info(f"Connection to {remote_host}:{remote_port} successful.")
    except Exception as e:
        logger.error(f"Failed to connect to {remote_host}:{remote_port}: {e}")
        raise

def send_dicom_file(dicom_file: str, remote_host: str, remote_port: int, remote_ae_title: str):
    """
    Sends a DICOM file using C-STORE to a remote DICOM server.
    """
    
    check_tcp_connectivity(remote_host, remote_port)

    try:
       
        dicom_dataset = dcmread(dicom_file)
    except InvalidDicomError:
        logger.error(f"{dicom_file} is not a valid DICOM file.")
        return

    
    ae = AE()
    ae.network_timeout = 10
    ae.acse_timeout = 30
    ae.dimse_timeout = 30

    
    ae.requested_contexts = StoragePresentationContexts

    try:
       
        assoc = ae.associate(remote_host, remote_port, ae_title=remote_ae_title)

        if assoc.is_established:
            logger.info(f"Association established with {remote_host}:{remote_port}. Sending DICOM file...")

            
            status = assoc.send_c_store(dicom_dataset)

            if status:
                logger.info(f"DICOM file sent successfully! Status: {status}")
            else:
                logger.error("Failed to send DICOM file.")

            assoc.release()
        else:
            logger.error("Failed to establish association with the remote server.")
    except Exception as e:
        logger.error(f"An error occurred while sending the DICOM file: {e}")
        raise


dicom_file = 'path_to_valid_dicom_file.dcm'  
remote_host = 'Ip Address' 
remote_port = 104  
remote_ae_title = 'Title eg: jhon..etc anything is prefered'

send_dicom_file(dicom_file, remote_host, remote_port, remote_ae_title)



##Sample code###
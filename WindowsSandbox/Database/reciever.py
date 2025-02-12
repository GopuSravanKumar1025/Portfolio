import os
import logging
import socket
import zipfile

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def receive_and_save_to_zip(zip_file_path, server_port):
    """
    Listens for incoming connections, receives DICOM files, and directly adds them to a ZIP file.
    :param zip_file_path: Path where the ZIP file will be saved.
    :param server_port: Port number to listen for incoming connections.
    :return: None
    """
    # Create a socket to listen for incoming connections
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('0.0.0.0', server_port))  # Bind to all available interfaces
    server_socket.listen(1)  # Listen for one connection at a time
    logger.info(f"Server listening on port {server_port}...")

    # Open the ZIP file to write received files into it
    with zipfile.ZipFile(zip_file_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        try:
            # Wait for a client connection
            client_socket, client_address = server_socket.accept()
            logger.info(f"Connection from {client_address} established!")

            # Receive the files one by one and directly add them to the ZIP archive
            while True:
                # Receive the file name first (assuming client sends a filename before sending the file)
                file_name_length = client_socket.recv(4)  # Receive length of file name (4 bytes)
                if not file_name_length:
                    break  # No data received, break the loop

                file_name_length = int.from_bytes(file_name_length, 'big')  # Convert length to integer
                file_name = client_socket.recv(file_name_length).decode('utf-8')  # Receive the file name
                logger.info(f"Receiving file: {file_name}")

                # Add the file to the ZIP archive directly
                file_data = bytearray()
                while True:
                    data = client_socket.recv(1024)  # Receive data in 1024-byte chunks
                    if not data:
                        break  # End of file
                    file_data.extend(data)

                # Write the file data to the ZIP archive
                zipf.writestr(file_name, file_data)
                logger.info(f"File {file_name} received and added to ZIP archive.")

        except Exception as e:
            logger.error(f"An error occurred during file reception: {e}")
        finally:
            # Close the client and server sockets
            client_socket.close()
            server_socket.close()

    logger.info(f"All files received and saved to {zip_file_path}.")

# Example usage
zip_file_path = r'C:\Users\WDAGUtilityAccount\Desktop\Received_DICOM_Files.zip'  # Path for saving the ZIP file
server_port = 5252  # Port to listen for DICOM file reception

# Receive and save DICOM files directly into a ZIP file
receive_and_save_to_zip(zip_file_path, server_port)

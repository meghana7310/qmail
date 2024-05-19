from qiskit import QuantumCircuit, Aer, execute
from channel_class import ClassicalChannel, QuantumChannel
from cryptography.fernet import Fernet

# Alice's code to establish a quantum key
def alice_quantum_key():
    # Implement your QKD protocol (e.g., BB84) here
    # Return the key
    return 'quantum_key'

# Encrypt message using symmetric encryption
def encrypt_message(message, key):
    cipher_suite = Fernet(key)
    return cipher_suite.encrypt(message.encode())

# Main function
def main():
    quantum_key = alice_quantum_key()
    symmetric_key = b'abcdefghijklmnopqrstuvwxyz123456'  # Replace with a secure random key

    # Message to send
    message = "Hello, Bob! This is a secret message."

    # Encrypt the message using symmetric encryption
    encrypted_message = encrypt_message(message, symmetric_key)

    # Send the encrypted message over the quantum channel
    channel = QuantumChannel()
    channel.send(encrypted_message, [1])  # Sending to Bob

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
from qiskit import *
from qiskit.quantum_info import Statevector
from textwrap import wrap
from random import randrange


# Quantum One-Time pad related methods

def str_to_lbin(message, bin_size=4):
    """
    String to 8 bit binary per character

    :message:str, the message
    """
    clist = [ord(x) for x in message]
    bins = ''.join([format(x,'08b') for x in clist])
    return wrap(bins,bin_size)


def bins_to_str(lbin):
    """
    Return a list of unicode characters into a message 

    :lbin:list(bin), a list of characters
    """
    sbin = ''.join(lbin) 
    lbin8 = wrap(sbin, 8)
    message = chr(int(lbin8[0],2))
    for c in lbin8[1:]:
        message+=chr(int(c,2))

    return message
 

def encode_cinfo_to_qstate(cinfo_bin):
    """
    Return the quantum state that encodes the binary  

    :cinfo_bin:str, string of binary contains the classical information

    return :QuantumCircuit:
    """
    nreg = len(cinfo_bin)
    qcirc = QuantumCircuit(nreg, nreg)
    for i,bit_i in enumerate(cinfo_bin[::-1]):
        if int(bit_i):
            qcirc.x(i)
    return qcirc


def generate_otp_key(key_length):
    """
    Generate key_length random key for one-time pad
    """
    x_key=bin(randrange(2**key_length))[2:] 
    z_key=bin(randrange(2**key_length))[2:] 

    return {'x': x_key, 'z': z_key}


def otp_enc_dec(qcirc, otpkey):
    """
    :qcirc:QuantumCircuit instance
    :key:dict={x:, z:}
    """
    r_x , r_z = otpkey['x'], otpkey['z']
    for i,k in enumerate(zip(r_x,r_z)):
        if k[0]:
            qcirc.x(i)
        if k[1]:
            qcirc.z(i)



def qotp(qcirc, otpkey):
    """
    Quantum one-time pad

    :qmessage:qiksit.QuantumCircuit 
    :key: dict{x:int y:int} 
    :nqubit:int, the number of qubits
    """
    #Alice's part: encoding
    otp_enc_dec(qcirc, otpkey)

    #Alice send the qubits
    #Channel stuff

    #Bob receives qubits, and decrypt them
    otp_enc_dec(qcirc, otpkey)

    #Bob measure the states, single shot
    simulator = Aer.get_backend('qasm_simulator')
    nqubit = len(otpkey['x'])
    for i in range(nqubit):
        qcirc.measure(range(nqubit), range(nqubit))
        counts = execute(qcirc, backend=simulator, shots = 1).result()

    output = list(counts.get_counts().keys())[0] 
    return output



def send_a_qmail_local(message, batch_size=4):
    """ Alice sends to Bob a quantum email

    :nqubit:int, the number of qubits
    :message:str, the secret message that wants to be sent 
    """
    nqubit = batch_size

    print('Alice wants to send %s'%message)

    #send message per batch bits
    Lbins = str_to_lbin(message, batch_size)

    #generate key
    print('generating key...')
    otpkey = generate_otp_key(len(Lbins)*batch_size)
    print('X-encryption key %s'%otpkey['x'], 'Z-encryption key %s'%otpkey['z'])

    key_per_batch = [{'x':x,'z':z} for x,z in zip(wrap(otpkey['x'],batch_size),wrap(otpkey['z'],batch_size))]

    bob_meas_results = []
    for bin_batch,k in zip(Lbins, key_per_batch):  
        print('Performing QOTP for string', bin_batch)
        qcirc = encode_cinfo_to_qstate(bin_batch) 
        bob_meas_results.append(qotp(qcirc, k))
        print('Bob measures',bob_meas_results[-1])
 
    print('Bobs message %s'%bins_to_str(bob_meas_results))
    return bins_to_str(bob_meas_results)


# Grover-related methods

def apply_grover_oracle2(qcirc, dquery):
    """
    grover oracle for query database: 

    :qcirc:QuantumCircuit, the qubits to apply
    :query:str, 00 01 10 11
    """
    qcirc.cz(1,0)
    if dquery == '11':
        qcirc.z(0)
        qcirc.z(1)
    elif dquery == '01':
        qcirc.z(1)
    elif dquery == '10':
        qcirc.z(0)
    else : pass


def multiparty_2grover_local(dquery):
    """
    multiparties 2-qubit grover algorithm with separated oracle
    as the database owner (Oscar). Oscar has a confiedential database,
    and will help Alice to reveal her data.

    :dquery:str, 00 01 10 11
    """
    print("Alice creates state |00>")
    qcirc = QuantumCircuit(2,2) 
    qcirc.h(0)    
    qcirc.h(1)  #at this point qcirc is in the equal superposition of all quantum states    

    print("Alice send qubits to Oscar, quering the database")
    # send ... Channel stuff......

    print("Oscar receives qubits, and apply oracles")
    apply_grover_oracle2(qcirc, dquery)

    print("Oscar sends the qubits back to Alice")
    # send ... Channel stuff......

    print("Alice receives qubits, apply diffusion operator, and measure")
    qcirc.h(0)
    qcirc.h(1)
    qcirc.cz(0,1)
    qcirc.h(0)
    qcirc.h(1)
    qcirc.measure([0,1],[0,1])
    simulator = Aer.get_backend('qasm_simulator')
    counts = execute(qcirc, backend=simulator, shots = 1).result()

    print("Alice measurement outcome", list(counts.get_counts().keys())[0])



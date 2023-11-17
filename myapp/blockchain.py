# blockchain.py

import os
import json
import hashlib
import time

class Blockchain:
    def __init__(self):
        self.chain = self.load_chain()
        self.create_genesis_block()

    def load_chain(self):
        if os.path.exists("blockchain.json"):
            with open("blockchain.json", "r") as file:
                return json.load(file)
        else:
            return []

    def save_chain(self):
        with open("blockchain.json", "w") as file:
            json.dump(self.chain, file)

    def create_genesis_block(self):
        if not self.chain:
            genesis_block = {
                'index': 0,
                'previous_hash': "0",
                'timestamp': time.time(),
                'data': "Genesis Block",
                'current_hash': self.hash_block("0", "Genesis Block", 0),
                'nonce': 0,
            }
            self.chain.append(genesis_block)
            self.save_chain()

    def add_block(self, data):
        # Add a new block to the blockchain
        index = len(self.chain)
        previous_block = self.chain[-1] if self.chain else None

        if previous_block:
            previous_hash = previous_block['current_hash']
        else:
            previous_hash = "0"

        timestamp = time.time()
        nonce = self.proof_of_work(previous_hash, data, timestamp)
        current_hash = self.hash_block(previous_hash, data, nonce)
        new_block = {
            'index': index,
            'previous_hash': previous_hash,
            'timestamp': timestamp,
            'data': data,
            'current_hash': current_hash,
            'nonce': nonce,
        }
        self.chain.append(new_block)
        self.save_chain()

    def hash_block(self, previous_hash, data, nonce):
        # Hash the block using SHA-256
        block_contents = f"{previous_hash}{data}{nonce}".encode('utf-8')
        return hashlib.sha256(block_contents).hexdigest()

    def proof_of_work(self, previous_hash, data, timestamp):
        # Implement a basic Proof of Work algorithm
        nonce = 0
        while self.valid_proof(previous_hash, data, timestamp, nonce) is False:
            nonce += 1
        return nonce

    def valid_proof(self, previous_hash, data, timestamp, nonce):
        # Check if the hash meets certain criteria (e.g., starts with four leading zeros)
        guess = f"{previous_hash}{data}{timestamp}{nonce}".encode('utf-8')
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:4] == "0000"

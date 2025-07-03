"""Input validation utilities."""

import re
import hashlib
import base58
from typing import Union

def validate_bitcoin_address(address: str, network: str = "mainnet") -> bool:
    """
    Validate Bitcoin address format using pure Python.
    
    Args:
        address: Bitcoin address to validate
        network: Network type (mainnet, testnet, regtest)
    
    Returns:
        bool: True if valid, False otherwise
    """
    try:
        # Basic format validation
        if not address or not isinstance(address, str):
            return False
        
        # Check length (Bitcoin addresses are typically 26-35 characters)
        if len(address) < 26 or len(address) > 62:  # Including bech32
            return False
        
        # Check for valid characters
        if not re.match(r'^[13][a-km-zA-HJ-NP-Z1-9]{25,34}$|^bc1[a-z0-9]{39,59}$', address):
            return False
        
        # For legacy addresses (starting with 1 or 3), validate checksum
        if address.startswith(('1', '3')):
            try:
                # Decode base58 and validate checksum
                decoded = base58.b58decode(address)
                if len(decoded) != 25:  # 21 bytes payload + 4 bytes checksum
                    return False
                
                # Verify checksum
                payload = decoded[:-4]
                checksum = decoded[-4:]
                calculated_checksum = hashlib.sha256(hashlib.sha256(payload).digest()).digest()[:4]
                
                if checksum != calculated_checksum:
                    return False
                    
            except Exception:
                return False
        
        # For bech32 addresses (starting with bc1), basic format validation
        elif address.startswith('bc1'):
            # Basic bech32 format check - more comprehensive validation would require bech32 library
            if not re.match(r'^bc1[a-z0-9]{39,59}$', address):
                return False
        
        return True
        
    except Exception:
        return False

def validate_transaction_hash(tx_hash: str) -> bool:
    """
    Validate Bitcoin transaction hash format.
    
    Args:
        tx_hash: Transaction hash to validate
    
    Returns:
        bool: True if valid, False otherwise
    """
    if not tx_hash or not isinstance(tx_hash, str):
        return False
    
    # Bitcoin transaction hashes are 64 character hex strings
    if len(tx_hash) != 64:
        return False
    
    # Check if it's a valid hex string
    try:
        int(tx_hash, 16)
        return True
    except ValueError:
        return False

def validate_block_hash(block_hash: str) -> bool:
    """
    Validate Bitcoin block hash format.
    
    Args:
        block_hash: Block hash to validate
    
    Returns:
        bool: True if valid, False otherwise
    """
    # Block hashes have the same format as transaction hashes
    return validate_transaction_hash(block_hash)

def validate_block_height(height: Union[str, int]) -> bool:
    """
    Validate Bitcoin block height.
    
    Args:
        height: Block height to validate
    
    Returns:
        bool: True if valid, False otherwise
    """
    try:
        height_int = int(height)
        return 0 <= height_int <= 1000000  # Reasonable upper bound
    except (ValueError, TypeError):
        return False
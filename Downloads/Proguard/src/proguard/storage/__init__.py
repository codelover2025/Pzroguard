"""
Secure Storage Module
Handles encrypted storage of sensitive activity data
"""

import os
import json
from pathlib import Path
from cryptography.fernet import Fernet


class SecureStorage:
    """
    Manages encrypted file storage for sensitive user activity data
    """
    
    def __init__(self, base_path='data'):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
        
        # Load or generate encryption key
        self.key_file = self.base_path / '.encryption_key'
        self.cipher = self._load_or_create_key()
    
    def _load_or_create_key(self):
        """Load existing encryption key or create new one"""
        if self.key_file.exists():
            with open(self.key_file, 'rb') as f:
                key = f.read()
        else:
            key = Fernet.generate_key()
            with open(self.key_file, 'wb') as f:
                f.write(key)
            # Set file as hidden on Windows
            try:
                import win32api
                import win32con
                win32api.SetFileAttributes(
                    str(self.key_file),
                    win32con.FILE_ATTRIBUTE_HIDDEN
                )
            except ImportError:
                pass
        
        return Fernet(key)
    
    def save_encrypted(self, filename, data):
        """
        Save data to encrypted file
        
        Args:
            filename: Name of file to save
            data: Data to save (will be JSON serialized)
        """
        try:
            # Convert data to JSON
            json_data = json.dumps(data, indent=2)
            
            # Encrypt
            encrypted_data = self.cipher.encrypt(json_data.encode())
            
            # Write to file
            file_path = self.base_path / filename
            with open(file_path, 'wb') as f:
                f.write(encrypted_data)
            
            return True
            
        except Exception as e:
            print(f"[ERROR] Error saving encrypted data: {e}")
            return False
    
    def load_encrypted(self, filename):
        """
        Load data from encrypted file
        
        Args:
            filename: Name of file to load
            
        Returns:
            Decrypted data (dict/list)
        """
        try:
            file_path = self.base_path / filename
            
            if not file_path.exists():
                return None
            
            # Read encrypted data
            with open(file_path, 'rb') as f:
                encrypted_data = f.read()
            
            # Decrypt
            decrypted_data = self.cipher.decrypt(encrypted_data)
            
            # Parse JSON
            data = json.loads(decrypted_data.decode())
            
            return data
            
        except Exception as e:
            print(f"[ERROR] Error loading encrypted data: {e}")
            return None
    
    def list_files(self):
        """List all encrypted files"""
        return [
            f.name for f in self.base_path.iterdir()
            if f.is_file() and f.name != '.encryption_key'
        ]
    
    def delete_file(self, filename):
        """Delete encrypted file"""
        try:
            file_path = self.base_path / filename
            if file_path.exists():
                file_path.unlink()
                return True
            return False
        except Exception as e:
            print(f"[ERROR] Error deleting file: {e}")
            return False


__all__ = ['SecureStorage']

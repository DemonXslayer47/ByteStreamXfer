import unittest
from app import encrypt_data, decrypt_data, key  # Make sure to import correctly from your app

class TestEncryptionDecryption(unittest.TestCase):
    def setUp(self):
        # Setup runs before each test method
        self.original_data = b"Hello, World!"  # Data to test

    def test_encryption_decryption(self):
        # Test that data is correctly encrypted and then decrypted back to original
        encrypted_data = encrypt_data(self.original_data)
        decrypted_data = decrypt_data(encrypted_data)
        self.assertEqual(decrypted_data, self.original_data)

    def test_encryption_changes_data(self):
        # Test that encrypted data is not the same as original
        encrypted_data = encrypt_data(self.original_data)
        self.assertNotEqual(encrypted_data, self.original_data)

if __name__ == '__main__':
    unittest.main()
"""
ZeuZ Secrets Management Module

This module provides secure access to encrypted secrets stored on the ZeuZ server.
Secrets are automatically decrypted and can be accessed like a dictionary.

Example:
    from Framework.Built_In_Automation.Shared_Resources.secrets import secret
    
    # Access a secret
    api_key = secret['my_api_key']
    db_password = secret['database_password']
"""

import json
import base64
import inspect
from typing import Dict, Optional

from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.padding import PKCS7

from Framework.Utilities import CommonUtil, RequestFormatter
from Framework.Built_In_Automation.Shared_Resources import BuiltInFunctionSharedResources as sr


from settings import ZEUZ_NODE_PRIVATE_RSA_KEYS_DIR


MODULE_NAME = inspect.getmodulename(__file__)


class Secret:
    """
    A class to securely fetch and decrypt secrets from the ZeuZ server.
    
    Secrets are accessed like a dictionary: secret['key_name']
    The class automatically:
    - Fetches the encrypted secret from the server
    - Decrypts it using the private key
    - Caches the result for performance # Disabled for now
    """
    
    def __init__(self):
        self._cache: Dict[str, str] = {}
        self._private_key_folder = ZEUZ_NODE_PRIVATE_RSA_KEYS_DIR
        
    def __getitem__(self, key_name: str) -> str:
        """
        Retrieve a secret by key name.
        
        Args:
            key_name: The name of the secret to retrieve
            
        Returns:
            The decrypted secret value
            
        Raises:
            KeyError: If the secret cannot be found or accessed
            Exception: If decryption fails
        """
        sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
        
        if key_name in self._cache:
            CommonUtil.ExecLog(sModuleInfo, f"Retrieved secret '{key_name}' from cache", 0)
            return self._cache[key_name]
        
        try:
            test_id = None
            if sr.Test_Shared_Variables("zeuz_current_tc"):
                current_tc = sr.Get_Shared_Variables("zeuz_current_tc")
                if isinstance(current_tc, dict) and "testcase_no" in current_tc:
                    test_id = current_tc["testcase_no"]
            node_id = sr.Get_Shared_Variables("node_id") or None

            step_data = sr.Get_Shared_Variables(CommonUtil.dont_prettify_on_server[0])
            if step_data and isinstance(step_data, list) and len(step_data) >= int(CommonUtil.current_action_no):
                current_action = step_data[int(CommonUtil.current_action_no) - 1]
                action_details = []
                for action in current_action:
                    if action and len(action) >= 3:
                        action_details.append({"left": action[0], "middle": action[1], "right": action[2]})
            params = {}
            if test_id:
                params["test_id"] = test_id
            if node_id:
                params["node_id"] = node_id
            if action_details:
                params["action_details"] = json.dumps({"values": action_details, "extra": "{}"})

            CommonUtil.ExecLog(sModuleInfo, f"Fetching secret '{key_name}' from server", 0)
            
            response = RequestFormatter.request(
                method="GET",
                url=RequestFormatter.form_uri(f"/d/api/v1/zeuz-secrets/{key_name}"),
                params=params,
                verify=False
            )
            
            if response.status_code == 403:
                CommonUtil.ExecLog(
                    sModuleInfo,
                    f"Access denied to secret '{key_name}'. Check permissions.",
                    3
                )
                raise KeyError(f"Access denied to secret '{key_name}'")
            
            if response.status_code != 200:
                CommonUtil.ExecLog(
                    sModuleInfo,
                    f"Failed to fetch secret '{key_name}': {response.status_code}",
                    3
                )
                raise KeyError(f"Secret '{key_name}' not found or inaccessible")
            
            data = response.json()
            encrypted_value = data.get("value")
            
            if not encrypted_value:
                CommonUtil.ExecLog(
                    sModuleInfo,
                    f"Secret '{key_name}' has no value",
                    3
                )
                raise KeyError(f"Secret '{key_name}' has no value")
            
            decrypted_value = self._decrypt_data(encrypted_value)

            
            # Cache the decrypted value
            # self._cache[key_name] = decrypted_value
            
            if key_name not in CommonUtil.zeuz_disable_var_print:
                CommonUtil.zeuz_disable_var_print[key_name] = decrypted_value
            
            CommonUtil.ExecLog(
                sModuleInfo,
                f"Successfully retrieved and decrypted secret '{key_name}'",
                1
            )
            
            return decrypted_value
            
        except KeyError:
            raise
        except Exception as e:
            CommonUtil.ExecLog(
                sModuleInfo,
                f"Error retrieving secret '{key_name}': {str(e)}",
                3
            )
            raise KeyError(f"Failed to retrieve secret '{key_name}': {str(e)}")

    
    def _load_private_keys(self):
        sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
        
        try:
            if not self._private_key_folder.exists():
                CommonUtil.ExecLog(
                    sModuleInfo,
                    f"Private key folder not found at {self._private_key_folder}",
                    3
                )
                raise FileNotFoundError(f"Private key folder not found at {self._private_key_folder}")
            
            private_keys = []
            for pem_file in self._private_key_folder.glob("*.pem"):
                with open(pem_file, 'rb') as f:
                    private_key = serialization.load_pem_private_key(f.read(), password=None)
                    private_keys.append(private_key)
            
            if not private_keys:
                raise FileNotFoundError(f"No .pem files found in {self._private_key_folder}")
            
            return private_keys
        except Exception as e:
            CommonUtil.ExecLog(
                sModuleInfo,
                f"Failed to load private keys: {str(e)}",
                3
            )
            raise
    
    def _decrypt_data(self, encrypted_data: str) -> str:
        """
        Decrypt data that was encrypted using hybrid encryption (RSA + AES).
        
        Args:
            encrypted_data: Base64 encoded JSON string containing encrypted key, IV, and data
            
        Returns:
            Decrypted plaintext string
        """
        private_keys = self._load_private_keys()
        
        decoded_data = base64.b64decode(encrypted_data)
        data = json.loads(decoded_data.decode('utf-8'))
        
        encrypted_aes_key = base64.b64decode(data['encryptedKey'])
        iv = base64.b64decode(data['iv'])
        encrypted_content = base64.b64decode(data['encryptedData'])
        
        for private_key in private_keys:
            try:
                aes_key = private_key.decrypt(
                    encrypted_aes_key,
                    padding.OAEP(
                        mgf=padding.MGF1(algorithm=hashes.SHA256()),
                        algorithm=hashes.SHA256(),
                        label=None
                    )
                )
                
                cipher = Cipher(algorithms.AES(aes_key), modes.CBC(iv))
                decryptor = cipher.decryptor()
                decrypted_padded = decryptor.update(encrypted_content) + decryptor.finalize()
                
                unpadder = PKCS7(128).unpadder()
                decrypted = unpadder.update(decrypted_padded) + unpadder.finalize()
                
                return decrypted.decode('utf-8')
            except Exception:
                continue
        
        raise Exception("No private key could decrypt the data")
    
    def clear_cache(self, key_name: Optional[str] = None):
        """
        Clear the cache for a specific secret or all secrets.
        
        Args:
            key_name: Optional specific secret to clear. If None, clears all.
        """
        if key_name:
            self._cache.pop(key_name, None)
        else:
            self._cache.clear()


secret = Secret()

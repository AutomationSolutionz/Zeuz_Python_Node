# Author: sazid

from typing import Any, Callable
import traceback
import asyncio
import random
import json
import httpx
from colorama import Fore
from pathlib import Path
from urllib.parse import urlparse

from Framework.Utilities import RequestFormatter, ConfigModule, CommonUtil
from Framework.Utilities.RequestFormatter import REQUEST_TIMEOUT
from Framework.node_server_state import STATE


class DeployHandler:
    """
    DeployHandler is responsible for maintaining the connection with deploy
    service and fetch any necessary resources to run test cases.
    """

    COMMAND_DONE = b"DONE"
    COMMAND_CANCEL = b"CANCEL"
    COMMAND_KEY_REQUEST = b"KEY_REQUEST"
    COMMAND_PRIVATE_KEY = b"PRIVATE_KEY"
    ERROR_PREFIX = b"error"

    def __init__(
        self,
        on_connect_callback: Callable[[bool], None],
        response_callback: Callable[[Any], None],
        cancel_callback: Callable[[], None],
        done_callback: Callable[[], bool],
    ) -> None:
        self.on_connect_callback = on_connect_callback
        self.response_callback = response_callback
        self.cancel_callback = cancel_callback

        # Done callback should return true if node does not want to run anymore
        # test cases, false otherwise.
        self.done_callback = done_callback

        self.backoff_time = 0

    async def on_message(self, message) -> bool:
        """Returns True if the handler should quit, False otherwise."""

        if message == self.COMMAND_DONE:
            # We're done for this run session.
            return await self.done_callback()

        elif message == self.COMMAND_CANCEL:
            # Run cancelled by the user/service.
            await self.cancel_callback()
            return False
        
        elif message.startswith(b'{"command":"KEY_REQUEST"'):
            self.handle_key_request(message)
            return False
        
        elif message.startswith(b'{"command":"PRIVATE_KEY"'):
            self.handle_private_key(message)
            return False

        await self.response_callback(message)
        return False

    def on_error(self, error) -> None:
        print("[deploy] Error communicating with the deploy service.")
        print(error)
        if self.backoff_time < 6:
            self.backoff_time += 1

    def handle_key_request(self, message: bytes) -> None:
        """
        Handle KEY_REQUEST command.
        Server is asking this node to share its private key that matches the provided public key.
        """
        try:
            payload = json.loads(message)
            request_id = payload["request_id"]
            public_key_pem = payload["public_key"]
            receiver_node_ids = payload["receiver_node_ids"]
            print(f"[key-request] Received request {request_id} to share key with {receiver_node_ids}")
            
            private_key_pem = self.get_private_key_matching_public_key(public_key_pem)
            
            if private_key_pem:
                self.respond_to_key_request(request_id, private_key_pem)
            else:
                print("[key-request] ERROR: No private key found matching the provided public key")
        except Exception as e:
            print(f"[key-request] Error handling key request: {e}")
            traceback.print_exc()

    def handle_private_key(self, message: bytes) -> None:
        """
        Handle PRIVATE_KEY command.
        Server is sending us a private key.
        """
        try:
            payload = json.loads(message)
            key_id = payload["key_id"]
            private_key_pem = payload["private_key"]
            
            print(f"[private-key] Received key {key_id}")
            
            self.save_private_key(key_id, private_key_pem)
            
            print(f"[private-key] Key {key_id} saved successfully")
        except Exception as e:
            print(f"[private-key] Error handling private key: {e}")
            traceback.print_exc()

    def get_private_key_matching_public_key(self, public_key_pem: str) -> str | None:
        try:
            from settings import ZEUZ_NODE_PRIVATE_RSA_KEYS_DIR
            from cryptography.hazmat.primitives import serialization
            
            key_folder = Path(ZEUZ_NODE_PRIVATE_RSA_KEYS_DIR)
            if not key_folder.exists():
                print("[key-request] Key folder does not exist")
                return None
            
            # Parse the provided public key
            try:
                target_public_key = serialization.load_pem_public_key(
                    public_key_pem.encode('utf-8')
                )
                target_public_key_bytes = target_public_key.public_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PublicFormat.SubjectPublicKeyInfo
                )
            except Exception as e:
                print(f"[key-request] Error parsing provided public key: {e}")
                return None
            
            # Get all PEM files
            pem_files = list(key_folder.glob("*.pem"))
            
            if not pem_files:
                print("[key-request] No private key files found")
                return None
            
            # Search through all keys to find matching private key
            for pem_file in pem_files:
                try:
                    with open(pem_file, 'rb') as f:
                        private_key_bytes = f.read()
                        
                    # Load the private key
                    private_key = serialization.load_pem_private_key(
                        private_key_bytes, 
                        password=None
                    )
                    
                    # Extract its public key
                    derived_public_key = private_key.public_key()
                    derived_public_key_bytes = derived_public_key.public_bytes(
                        encoding=serialization.Encoding.PEM,
                        format=serialization.PublicFormat.SubjectPublicKeyInfo
                    )
                    
                    # Compare public keys
                    if derived_public_key_bytes == target_public_key_bytes:
                        print(f"[key-request] Found matching private key: {pem_file.name}")
                        # Return the private key in traditional RSA PRIVATE KEY format
                        return private_key.private_bytes(
                            encoding=serialization.Encoding.PEM,
                            format=serialization.PrivateFormat.TraditionalOpenSSL,
                            encryption_algorithm=serialization.NoEncryption()
                        ).decode('utf-8')
                        
                except Exception as e:
                    print(f"[key-request] Error reading key file {pem_file.name}: {e}")
                    continue
            
            print("[key-request] No private key matches the provided public key")
            return None
            
        except Exception as e:
            print(f"[key-request] Error searching for matching private key: {e}")
            traceback.print_exc()
            return None

    def save_private_key(self, key_id: str, private_key_pem: str) -> None:
        """
        Save the received private key to encrypted storage.
        This key is saved to the same location where generated keys are stored.
        """
        try:
            from settings import ZEUZ_NODE_PRIVATE_RSA_KEYS_DIR
            from cryptography.hazmat.primitives import serialization
            
            key_folder = Path(ZEUZ_NODE_PRIVATE_RSA_KEYS_DIR)
            key_folder.mkdir(parents=True, exist_ok=True)
            
            private_key = serialization.load_pem_private_key(
                private_key_pem.encode('utf-8'),
                password=None,
            )
            
            key_filename = f"received-{key_id}.pem"
            key_path = key_folder / key_filename
            
            with open(key_path, 'wb') as f:
                f.write(private_key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.TraditionalOpenSSL,
                    encryption_algorithm=serialization.NoEncryption()
                ))
            
            print(f"[private-key] Saved to: {key_path}")
        except Exception as e:
            print(f"[private-key] Error saving private key: {e}")
            traceback.print_exc()

    def respond_to_key_request(self, request_id: str, private_key_pem: str) -> None:
        """
        Respond to a key request - server will automatically distribute to receivers.
        """
        try:
            server_url = urlparse(
                ConfigModule.get_config_value("Authentication", "server_address")
            )
            api_url = f"{server_url.scheme}://{server_url.netloc}/zsvc/deploy/v1/respond-to-key-request"
            
            # Get node ID
            node_id = CommonUtil.MachineInfo().getLocalUser().lower()
            
            response = RequestFormatter.request(
                "post",
                api_url,
                json={
                    "request_id": request_id,
                    "donor_node_id": node_id,
                    "private_key": private_key_pem
                },
                verify=False
            )
            
            if response.ok:
                result = response.json()
                success_count = result.get('success_count', 0)
                print(f"[key-request] Successfully distributed key to {success_count} receiver nodes")
            else:
                print(f"[key-request] Failed to respond to key request: {response.status_code}")
                print(f"[key-request] Response: {response.text}")
        except Exception as e:
            print(f"[key-request] Error responding to key request: {e}")
            traceback.print_exc()

    async def run(self, host: str) -> None:
        reconnect = False
        server_online = False
        async with httpx.AsyncClient(timeout=httpx.Timeout(70.0), verify=False) as client:
            while True:
                if STATE.reconnect_with_credentials is not None:
                    break

                if reconnect:
                    if server_online:
                        await asyncio.sleep(0.1)
                    else:
                        await asyncio.sleep(random.randint(1, 3))

                await self.on_connect_callback(reconnect)

                try:
                    reconnect = True
                    resp = await self.fetch(host, client)
                    if resp is None:
                        break

                    if resp.content.startswith(self.ERROR_PREFIX):
                        server_online = False
                        self.on_error(resp.content)
                        continue

                    if resp.status_code == httpx.codes.NO_CONTENT:
                        server_online = False
                        continue

                    if not resp.is_success:
                        server_online = False
                        print(
                            "[deploy] facing difficulty communicating with the server, status code:",
                            resp.status_code,
                            " | reconnecting",
                        )
                        try:
                            print(Fore.YELLOW + str(resp.content))
                        except Exception:
                            pass

                        # Encountered a server error, retry.
                        await asyncio.sleep(random.randint(1, 3))
                        return

                    should_quit = await self.on_message(resp.content)
                    if should_quit:
                        break

                    reconnect = False
                    server_online = True
                except httpx.ReadTimeout:
                    pass
                except Exception:
                    traceback.print_exc()
                    print("[deploy] RETRYING...")

    async def fetch(self, host: str, client: httpx.AsyncClient) -> httpx.Response | None:
        try:
            api_key = ConfigModule.get_config_value("Authentication", "api-key")
            headers = {"X-API-KEY": api_key}
            
            while True:
                if STATE.reconnect_with_credentials is not None:
                    return None
                
                try:
                    resp = await client.get(host, headers=headers)
                    return resp
                except asyncio.CancelledError:
                    return None
                except Exception:
                    if STATE.reconnect_with_credentials is not None:
                        return None
                    await asyncio.sleep(0.1)
        except Exception:
            return None

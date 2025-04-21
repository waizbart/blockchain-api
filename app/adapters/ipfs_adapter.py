import json
from typing import Any, Dict, Optional

import ipfshttpclient

from app.adapters.storage_adapter import StorageAdapter


class IPFSAdapter(StorageAdapter):
    """
    IPFS implementation of the storage adapter.
    """

    def __init__(self, ipfs_url: str = "/ip4/127.0.0.1/tcp/5001"):
        """
        Initialize the IPFS adapter.

        Args:
            ipfs_url: The URL of the IPFS node to connect to.
        """
        self.client = ipfshttpclient.connect(ipfs_url)

    def store(self, data: Any) -> str:
        """
        Store data on IPFS and return the content identifier (CID).

        Args:
            data: The data to store.

        Returns:
            The IPFS CID.
        """
        # Convert data to JSON if it's not already a string
        if not isinstance(data, str):
            data = json.dumps(data)

        # Add the data to IPFS
        result = self.client.add_str(data)

        return result

    def retrieve(self, identifier: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve data from IPFS by its CID.

        Args:
            identifier: The IPFS CID.

        Returns:
            The retrieved data as a dictionary, or None if retrieval fails.
        """
        try:
            # Get the data from IPFS
            data = self.client.cat(identifier).decode('utf-8')

            # Parse JSON data
            return json.loads(data)
        except Exception as e:
            print(f"Error retrieving data from IPFS: {str(e)}")
            return None

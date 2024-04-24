#  Copyright 2024 Google LLC
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
# flake8: noqa
from typing import Optional

from google.cloud.compute_v1.types import Address
from google.cloud.compute_v1.services.addresses.client import AddressesClient
from google.cloud.compute_v1.services.global_addresses import GlobalAddressesClient


# <INGREDIENT get_static_ip_address>
def get_static_ip_address(
    project_id: str, address_name: str, region: Optional[str] = None
) -> Address:
    """
    Retrieves a static external IP address, either regional or global.

    Args:
    project_id (str): project ID.
    address_name (str): The name of the IP address.
    region (Optional[str]): The region of the IP address if it's regional. None if it's global.

    Raises: google.api_core.exceptions.NotFound: in case of address not found

    Returns:
    Address: The Address object containing details about the requested IP.
    """
    if region:
        # Use regional client if a region is specified
        client = AddressesClient()
        address = client.get(project=project_id, region=region, address=address_name)
    else:
        # Use global client if no region is specified
        client = GlobalAddressesClient()
        address = client.get(project=project_id, address=address_name)

    return address


# </INGREDIENT>

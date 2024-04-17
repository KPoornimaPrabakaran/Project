# Copyright 2022 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# This file contains code samples that demonstrate how to get list of service account.


# [START iam_list_service_accounts]
def list_service_accounts(project_id: str) -> None:
    from google.cloud import iam_admin_v1
    from google.cloud.iam_admin_v1 import types
    """
    Get list of service accounts.
    project_id: ID or number of the Google Cloud project you want to use.
    account_id: ID or email which will be unique identifier of the service account
    display_name (optional): human-readable name, which will be assigned to the service account
    """

    iam_admin_client = iam_admin_v1.IAMClient()
    request = types.ListServiceAccountsRequest()

    request.name = f"projects/{project_id}"

    accounts = iam_admin_client.list_service_accounts(request=request)

    for account in accounts.accounts:
        print(f"Got service account: {account.email}")


if __name__ == "__main__":
    # To run the sample you would need
    # iam.serviceAccounts.list permission (roles/iam.serviceAccountViewer))

    # Your Google Cloud project ID.
    project_id = "your-google-cloud-project-id"

    # Existing service account name within the project specified above.
    account_id = account_name = "test-service-account"

    list_service_accounts(project_id)

# [END iam_list_service_accounts]
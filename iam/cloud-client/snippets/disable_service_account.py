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

# This file contains code samples that demonstrate how to disable service account.

# [START iam_disable_service_account]
def disable_service_account(project_id: str, account: str) -> None:
    from google.cloud import iam_admin_v1
    from google.cloud.iam_admin_v1 import types
    """
    Enables a service account.
    project_id: ID or number of the Google Cloud project you want to use.
    account: ID or email which is unique identifier of the service account.
    """

    iam_admin_client = iam_admin_v1.IAMClient()
    request = types.DisableServiceAccountRequest()
    name = f"projects/{project_id}/serviceAccounts/{account}"

    request.name = name
    iam_admin_client.disable_service_account(request=request)

    request = types.GetServiceAccountRequest()
    request.name = name

    service_account = iam_admin_client.get_service_account(request=request)
    if service_account.disabled:
        print(f"Disabled service account: {account}")


if __name__ == "__main__":
    # To run the sample you would need
    # iam.serviceAccounts.enable permission (roles/iam.serviceAccountAdmin)

    # Your Google Cloud project ID.
    project_id = "your-google-cloud-project-id"

    # Existing service account name within the project specified above.
    account_name = "test-service-account"
    account_id = f"{account_name}@{project_id}.iam.gserviceaccount.com"

    disable_service_account(project_id, account_id)

# [END iam_disable_service_account]
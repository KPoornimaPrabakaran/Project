#!/usr/bin/env python

# Copyright 2016 Google Inc. All Rights Reserved.
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

import time

# [START instantiate]
from googleapiclient.discovery import build

client_service = build("jobs", "v2")
# [END instantiate]


# [START commute_search]
def commute_search(client_service, company_name):
    request_metadata = {
        "user_id": "HashedUserId",
        "session_id": "HashedSessionId",
        "domain": "www.google.com",
    }
    start_location = {"latitude": 37.422408, "longitude": -122.085609}
    commute_preference = {
        "road_traffic": "TRAFFIC_FREE",
        "method": "TRANSIT",
        "travel_time": "1000s",
        "start_location": start_location,
    }
    job_query = {"commute_filter": commute_preference}
    if company_name is not None:
        job_query.update({"company_names": [company_name]})
    request = {
        "query": job_query,
        "request_metadata": request_metadata,
        "job_view": "FULL",
        "enable_precise_result_size": True,
    }
    response = client_service.jobs().search(body=request).execute()
    print(response)


# [END commute_search]


def run_sample():
    import base_company_sample
    import base_job_sample

    company_to_be_created = base_company_sample.generate_company()
    company_created = base_company_sample.create_company(
        client_service, company_to_be_created
    )
    company_name = company_created.get("name")

    job_to_be_created = base_job_sample.generate_job_with_required_fields(company_name)
    job_to_be_created.update(
        {"locations": ["1600 Amphitheatre Pkwy, Mountain View, CA 94043"]}
    )
    job_name = base_job_sample.create_job(client_service, job_to_be_created).get("name")

    # Wait several seconds for post processing
    time.sleep(10)
    commute_search(client_service, company_name)

    base_job_sample.delete_job(client_service, job_name)
    base_company_sample.delete_company(client_service, company_name)


if __name__ == "__main__":
    run_sample()

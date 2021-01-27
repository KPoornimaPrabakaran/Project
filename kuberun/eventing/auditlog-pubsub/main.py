# Copyright 2021 Google LLC.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os

from flask import Flask, request

app = Flask(__name__)


@app.route("/", methods=["POST"])
def index():
    # Gets the Pub/Sub topic name from the CloudEvent header
    # Example: "pubsub.googleapis.com/projects/_/topics/my-topic
    topic = request.headers.get("ce-subject")

    print(f"Created Pub/Sub topic: {topic}")
    return ("", 204)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))

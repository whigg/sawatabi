#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright 2021 Kotaro Terada
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

import argparse
import datetime
import random
import string
import time

from google.cloud import pubsub_v1

# from google.oauth2 import service_account


"""
This script publishes test messages to GCP Pub/Sub for debugging.

Sample Usage:
$ GOOGLE_APPLICATION_CREDENTIALS="./gcp-key.json" python sample/pubsub/publish_pubsub.py \
    --project=your-project \
    --topic=your-topic

$ GOOGLE_APPLICATION_CREDENTIALS="./gcp-key.json" python sample/pubsub/publish_pubsub.py \
    --project=your-project \
    --topic=your-topic \
    --interval=10.0 \
    --random-text

$ GOOGLE_APPLICATION_CREDENTIALS="./gcp-key.json" python sample/pubsub/publish_pubsub.py \
    --project=your-project \
    --topic=your-topic \
    --interval=30.0 \
    --random-number

$ GOOGLE_APPLICATION_CREDENTIALS="./gcp-key.json" python sample/pubsub/publish_pubsub.py \
    --project=your-project \
    --topic=your-topic \
    --interval=0.1 \
    --incremental-text \
    --incremental-end=100
"""


def main() -> None:
    parser = argparse.ArgumentParser()

    # fmt: off

    # Pub/Sub options
    parser.add_argument(
        "--project",
        dest="project",
        required=True,
        help="Google Cloud Platform project name.")
    parser.add_argument(
        "--topic",
        dest="topic",
        required=True,
        help="Google Cloud Pub/Sub topic name to publish messages to.")

    # Random
    parser.add_argument(
        "--random-text",
        dest="random_text",
        action="store_true",
        help="If true, a message will be a random text string.")
    parser.add_argument(
        "--random-number",
        dest="random_number",
        action="store_true",
        help="If true, a message will be a random number.")
    parser.add_argument(
        "--random-city",
        dest="random_city",
        action="store_true",
        help="If true, a message will be a random city JSON string.")

    # Incremental
    parser.add_argument(
        "--incremental-text",
        dest="incremental_text",
        action="store_true",
        help="If true, a message will be a text string whose length increments.")
    parser.add_argument(
        "--incremental-number",
        dest="incremental_number",
        action="store_true",
        help="If true, a message will be a incremental number.")
    parser.add_argument(
        "--incremental-end",
        dest="incremental_end",
        type=int,
        default=-1,
        help="Number for finish the increments.")

    parser.add_argument(
        "--interval",
        dest="interval",
        type=float,
        default=1.0,
        help="Message interval in second.")

    # fmt: on

    args = parser.parse_args()

    # client = pubsub_v1.PublisherClient(credentials=service_account.Credentials.from_service_account_file(os.environ["GOOGLE_APPLICATION_CREDENTIALS"]))
    client = pubsub_v1.PublisherClient()
    topic_path = client.topic_path(args.project, args.topic)

    i = 1
    while True:
        dt_now = datetime.datetime.now()
        if args.random_text:
            words = []
            for _ in range(random.randint(1, 10)):
                word = "".join([random.choice(string.ascii_letters + string.digits) for i in range(random.randint(1, 10))])
                words.append(word)
            message = " ".join(words) + "."
        elif args.random_number:
            n = random.randint(1, 99)
            message = str(n)
        elif args.random_city:
            name = "".join([random.choice(string.ascii_letters) for i in range(random.randint(2, 10))]).capitalize()
            lon = random.uniform(120.0, 140.0)
            lat = random.uniform(20.0, 40.0)
            message = f'{{"{name}": [{lon}, {lat}]}}'
        elif args.incremental_text:
            message = "".join([random.choice(string.ascii_letters + string.digits) for i in range(i)])
        elif args.incremental_number:
            message = str(i)
        else:
            message = f"This is a test message at {dt_now}."

        client.publish(topic_path, message.encode("utf-8"))
        print(f"[{dt_now}] Sent message to '{topic_path}': {message}")

        if i == args.incremental_end:
            break
        i += 1
        time.sleep(args.interval)


if __name__ == "__main__":
    main()

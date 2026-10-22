#!/usr/bin/env python3
import json

inventory = {
      "labservers": {
        "hosts": ["node1", "node2"]
      },
      "_meta": {
        "hostvars": {}
      }
    }

print(json.dumps(inventory))

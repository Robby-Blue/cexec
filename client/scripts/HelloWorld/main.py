import json
print("Hello Python")

with open("/app/output/output.json", "w") as f:
    json.dump({
        "webhook": {
            "title": "Lorem Ipsum",
            "embeds": [
                {
                    "fields": [
                        {
                            "name": "custom webhook",
                            "value": "from the HelloWorld script",
                            "inline": False
                        },
                    ],
                }
            ]
        }
    }, f)
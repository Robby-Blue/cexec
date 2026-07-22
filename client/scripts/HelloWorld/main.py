import json
print("Hello Python")

with open("/app/output/run/hello.txt", "w") as f:
    f.write("HelloWorld run file")

with open("/app/output/global/hello.txt", "w") as f:
    f.write("HelloWorld global file")
    
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
        },
        "new_tasks": [
            {
                "script": "ByeWorld"
            }
        ]
    }, f)
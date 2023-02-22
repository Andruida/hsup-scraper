#!/usr/bin/env python3

import requests as req
import json
import time
import os

with open("config.json") as f:
    config = json.load(f)

URL_BASE = "https://hsup.nkfih.gov.hu"
IMAGES_PATH = "images/"
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36 OPR/95.0.0.0"

if not os.path.exists(IMAGES_PATH):
    os.mkdir(IMAGES_PATH)

output = open("output.md", "w")
output.write("% HSUP tananyag 2. félév\n% Andruida\n\n")

# authenticate

if not config.get("bearer"):
    res = req.post(URL_BASE+"/api/auth/login", json=config, headers={"User-Agent": UA})

    if res.status_code != 201:
        print("Login failed")
        exit(1)

    res_json = res.json()
    bearer = res_json["token"]
    user = res_json["user"]

    config["bearer"] = bearer
    with open("config.json", "w") as f:
        json.dump(config, f, indent=4)

    print("Logged in as", user["fullName"])
else:
    bearer = config["bearer"]

auth_header = {
    "authorization": "Bearer "+bearer,
    "User-Agent": UA
}

# get data

res = req.get(URL_BASE+"/api/progress", headers=auth_header)

if res.status_code != 200:
    print("Failed to lesson index")
    exit(1)

# object like in progress.json
progress = res.json()

processedModules = []
for id, lesson in progress["lessons"].items():
    if lesson["module_rel"]["subject_rel"] != progress["currentProgress"]["subjectId"]:
        continue
    if lesson["module_rel"]["external_id"] not in processedModules:
        print("Processing module:", lesson["module_rel"]["external_id"], lesson["module_rel"]["name"])
        processedModules.append(lesson["module_rel"]["external_id"])
        # write module header
        output.write((
            "# {name}\n\n"
            "> Becsült olvasási idő: {estimated_time}\n\n"
            "{description}\n\n"
        ).format(
            name=lesson["module_rel"]["name"],
            estimated_time=lesson["module_rel"]["estimated_time"],
            description=lesson["module_rel"]["description"]
        ))
    # write lesson header
    output.write((
        "# {title}\n\n"
        "{description}\n\n"
    ).format(
        title=(lesson["title"] + " [+]" if len(lesson["bonus_for_personalities"]) > 0 else lesson["title"]),
        description=lesson.get("description", "")
    ))

    # get lesson content
    time.sleep(0.5)
    print("Fetching:", id, lesson["title"])
    res = req.get(URL_BASE+"/api/lesson/"+id, headers=auth_header)

    if res.status_code != 200:
        print("Failed to get lesson content")
        continue

    content = res.json()

    for section in content["sections"]:
        # write section header
        output.write("---\n\n")
        if section.get("header"):
            output.write((
                "## {header}\n\n"
            ).format(
                header=section["header"]
            ))
        for p in section["paragraphs"]:
            if p.get("subheader"):
                # write subheader
                output.write((
                    "### {subheader}\n\n"
                ).format(
                    subheader=p["subheader"]
                ))
            if p.get("text"):
                output.write((
                    "{text}\n\n"
                ).format(
                    text=p["text"]
                ))
            if p.get("image"):
                img = req.get(p["image"]["url"], headers={"User-Agent": UA})

                if (img.status_code != 200):
                    print("Failed to download image", p["image"]["url"])
                else:
                    with open(IMAGES_PATH+p["image"]["name"], "wb") as f:
                        f.write(img.content)
                
                # write image reference
                output.write((
                    "![{alt}]({image_path})\n"
                ).format(
                    alt=p["image"].get("alternativeText"),
                    image_path=IMAGES_PATH+p["image"]["name"]
                ))
                if p["image"].get("caption"):
                    output.write((
                        "*{caption}*\n"
                    ).format(
                        caption=p["image"]["caption"]
                    ))
                output.write("\n")


output.close()
# process data for pre-training in LlamaFactory format
import json
from process_utils import is_english_simple, bbox_2_point, bbox_2_bbox
import task_prompts
from tqdm import tqdm
import os
import random
import argparse


parser = argparse.ArgumentParser(description="Process data for pre-training in LlamaFactory format.")

parser.add_argument("--data_dir", default="/global/cfs/cdirs/m3930/$USER/SeeClick/data",
                    help="Base data directory (default: /global/cfs/cdirs/m3930/$USER/SeeClick/data)")

args = parser.parse_args()

# Expand $USER if present
data_dir = os.path.expandvars(args.data_dir)

# Auto-construct paths from data_dir
mobile_imgs = os.path.join(data_dir, "mobile/combined")
web_imgs = os.path.join(data_dir, "web/cpfs01/user/chengkanzhi/seeclick_web_imgs")
widgetcap_json = os.path.join(data_dir, "mobile/widget_captioning.json")
ricosca_json = os.path.join(data_dir, "mobile/ricosca.json")
screensum_json = os.path.join(data_dir, "mobile/screen_summarization.json")
web_json = os.path.join(data_dir, "web/seeclick_web.json")
coco_imgs = None
llava_json = None

# widget captioning & RICOSCA grounding
widgetcap_train = json.load(open(widgetcap_json, "r"))
ricosca_train = json.load(open(ricosca_json, "r"))
mobile_text_2_point = []
mobile_text_2_bbox = []
mobile_data_loca = {"widgetcap": widgetcap_train, "ricosca": ricosca_train}
for data_name, data in mobile_data_loca.items():

    print("Processing " + str(data_name))
    for i, item in tqdm(enumerate(data)):
        img_filename = item["img_filename"]
        img_path = os.path.join(mobile_imgs, img_filename)

        goal = item["instruction"]
        click_point = bbox_2_point(item["bbox"])
        click_bbox = bbox_2_bbox(item["bbox"])

        # text_2_point
        prompt = random.choice(task_prompts.loca_point_prompt).format(goal)
        messages_point = [
            {"role": "user", "content": "<image>" + prompt},
            {"role": "assistant", "content": click_point}
        ]
        mobile_text_2_point.append({
            "messages": messages_point,
            "images": [img_path]
        })

        # text_2_bbox
        prompt = random.choice(task_prompts.loca_bbox_prompt).format(goal)
        messages_bbox = [
            {"role": "user", "content": "<image>" + prompt},
            {"role": "assistant", "content": click_bbox}
        ]
        mobile_text_2_bbox.append({
            "messages": messages_bbox,
            "images": [img_path]
        })

print("Num of mobile_text_2_point: " + str(len(mobile_text_2_point)))
print("Num of mobile_text_2_bbox: " + str(len(mobile_text_2_bbox)))

# UI summarization
screensum_train = json.load(open(screensum_json, "r"))
mobile_screensum = []
print("Processing screensum")
i = 0
for i, item in tqdm(enumerate(screensum_train)):

    img_filename = item["img_filename"]
    img_path = os.path.join(mobile_imgs, img_filename)

    captions = item["captions"]
    random.shuffle(captions)
    for caption in captions[:3]:
        prompt = random.choice(task_prompts.screen_caption_prompt)
        messages = [
            {"role": "user", "content": "<image>" + prompt},
            {"role": "assistant", "content": caption}
        ]
        mobile_screensum.append({
            "messages": messages,
            "images": [img_path]
        })
        i += 1

print("Num of screensum: " + str(len(mobile_screensum)))

# widget captioning
widgetcap_train = json.load(open(widgetcap_json, "r"))
mobile_widgetcap = []
print("Processing widgetcap")
for i, item in tqdm(enumerate(widgetcap_train)):
    img_filename = item["img_filename"]
    img_path = os.path.join(mobile_imgs, img_filename)

    goal = item["instruction"]
    click_point = bbox_2_point(item["bbox"])

    prompt = random.choice(task_prompts.widgetcap_prompt).format(click_point)
    messages = [
        {"role": "user", "content": "<image>" + prompt},
        {"role": "assistant", "content": goal}
    ]
    mobile_widgetcap.append({
        "messages": messages,
        "images": [img_path]
    })

print("Num of widgetcap " + str(len(mobile_widgetcap)))

# web
web_train = json.load(open(web_json, "r"))
web_loca_point = []
web_loca_bbox = []
web_ocr_point = []
web_ocr_bbox = []
num_ele_valid = 0
print("Processing web")
for i, item in tqdm(enumerate(web_train)):

    img_filename = item["img_filename"]
    img_path = os.path.join(web_imgs, img_filename)

    eles_valid = []
    for ele in item["elements"]:
        if len([item for item in ele["bbox"] if item < 0]) != 0:
            continue
        if len(ele["instruction"]) > 60 or ele["instruction"].strip() == '':
            continue
        if ('{' in ele["instruction"]) or ('}' in ele["instruction"]):
            continue
        if not is_english_simple(ele["instruction"]):
            continue
        eles_valid.append(ele)

    if len(eles_valid) == 0:
        continue
    num_ele_valid += len(eles_valid)

    # text_2_point - multi-turn conversation
    random.shuffle(eles_valid)
    messages = []
    prompt = random.choice(task_prompts.web_loca_all_point_prompt)
    prompt += ' '

    for j, item in enumerate(eles_valid):
        if j == 0:
            # First turn includes image and prompt
            user_content = "<image>" + prompt + item["instruction"]
        else:
            # Subsequent turns are just the instruction
            user_content = item["instruction"]

        click_point = bbox_2_point(item["bbox"])
        messages.append({"role": "user", "content": user_content})
        messages.append({"role": "assistant", "content": click_point})

    web_loca_point.append({
        "messages": messages,
        "images": [img_path]
    })

    # text_2_bbox - multi-turn conversation
    random.shuffle(eles_valid)
    messages = []
    prompt = random.choice(task_prompts.web_loca_all_bbox_prompt)
    prompt += ' '

    for j, item in enumerate(eles_valid):
        if j == 0:
            user_content = "<image>" + prompt + item["instruction"]
        else:
            user_content = item["instruction"]

        click_bbox = bbox_2_bbox(item["bbox"])
        messages.append({"role": "user", "content": user_content})
        messages.append({"role": "assistant", "content": click_bbox})

    web_loca_bbox.append({
        "messages": messages,
        "images": [img_path]
    })

    # point_2_text - multi-turn conversation
    random.shuffle(eles_valid)
    messages = []
    prompt = random.choice(task_prompts.web_ocr_all_point_prompt)
    prompt += ' '

    for j, item in enumerate(eles_valid):
        click_point = bbox_2_point(item["bbox"])
        if j == 0:
            user_content = "<image>" + prompt + click_point
        else:
            user_content = click_point

        messages.append({"role": "user", "content": user_content})
        messages.append({"role": "assistant", "content": item["instruction"]})

    web_ocr_point.append({
        "messages": messages,
        "images": [img_path]
    })

    # bbox_2_text - multi-turn conversation
    random.shuffle(eles_valid)
    messages = []
    prompt = random.choice(task_prompts.web_ocr_all_bbox_prompt)
    prompt += ' '

    for j, item in enumerate(eles_valid):
        click_bbox = bbox_2_bbox(item["bbox"])
        if j == 0:
            user_content = "<image>" + prompt + click_bbox
        else:
            user_content = click_bbox

        messages.append({"role": "user", "content": user_content})
        messages.append({"role": "assistant", "content": item["instruction"]})

    web_ocr_bbox.append({
        "messages": messages,
        "images": [img_path]
    })

print("Num of valid elements: " + str(num_ele_valid))
print("Num of web_loca_point: " + str(len(web_loca_point)))
print("Num of web_loca_bbox: " + str(len(web_loca_bbox)))
print("Num of web_ocr_point: " + str(len(web_ocr_point)))
print("Num of web_ocr_bbox: " + str(len(web_ocr_bbox)))

# Skip LLaVA as we don't have COCO images
llava_150k = []
print("Num of llava: " + str(len(llava_150k)) + " (SKIPPED - no COCO images)")

# Apply the same filtering as original
random.shuffle(mobile_text_2_point)
mobile_text_2_point = mobile_text_2_point[:]
random.shuffle(mobile_text_2_bbox)
mobile_text_2_bbox = mobile_text_2_bbox[:56000]
random.shuffle(mobile_screensum)
mobile_screensum = mobile_screensum[:]
random.shuffle(mobile_widgetcap)
mobile_widgetcap = mobile_widgetcap[:42000]
random.shuffle(web_loca_point)
web_loca_point = web_loca_point[:]
random.shuffle(web_loca_bbox)
web_loca_bbox = web_loca_bbox[:54000]
random.shuffle(web_ocr_point)
web_ocr_point = web_ocr_point[:54000]
random.shuffle(web_ocr_bbox)
web_ocr_bbox = web_ocr_bbox[:54000]
random.shuffle(llava_150k)
llava_150k = llava_150k[:]

sft_train = mobile_text_2_point + mobile_text_2_bbox + mobile_screensum + mobile_widgetcap + web_loca_point + web_loca_bbox + web_ocr_point + web_ocr_bbox + llava_150k
print("Num of sft: " + str(len(sft_train)))
output_path = os.path.join(data_dir, "sft_train_llamafactory.json")
json.dump(sft_train, open(output_path, "w"), indent=2)
print("Saved to " + output_path)
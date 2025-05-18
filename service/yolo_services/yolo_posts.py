import re
from datetime import datetime, timedelta

import cv2
import pytesseract

from service.yolo_services.yolo_utils import COMMON_LANGUAGES, languages_list_to_tesseract_lang, normalize_text, \
    denoise_text_for_language_analysis, predict_text_language


def extract_post_data(image, image_results, class_names):
    """
    Extracts the post photo and a dictionary with the rest of the images with their extracted text from with
    pytesseract (with common languages specified).

    The bounding box for the post photo is selected based on the bounding box with the biggest area, and the bounding
    boxes with texts (except comments which all have the same label), are selected based on the box that contains
    the greatest amount of text for a specific label

    :param class_names: the names of the bounding boxes labels
    :param image: the image to which the results with bounding-boxes corresponds
    :param image_results: the bounding boxes extracted from the image
    :return: post photo, a dictionary with the rest of the images and their associated text:
    description/likes/date: {image: ... , text: ...}
    and returns a list with all the comment labels:
    comment:[{image: ... , text: ...},{image: ... , text: ...} ...]
    """
    # COORDINATES FOR PHOTO WITH BIGGEST AREA
    photo_box_coords = None
    max_photo_area = 0
    # OBJECT WITH COORDINATED FOR TEXT BOXES
    best_text_boxes = {}
    comments_boxes = []

    # BOUNDING BOXES FROM RESULTS
    boxes = image_results.boxes.xyxy
    # LABELS FROM RESULTS
    labels = image_results.boxes.cls

    for box, label in zip(boxes, labels):
        x1, y1, x2, y2 = map(int, box)
        label_name = class_names[int(label)]

        # THE REGION OF THE BOX IN THE IMAGE
        roi = image[y1:y2, x1:x2]

        # VERIFY THE PHOTO WITH BIGGEST AREA
        if label_name.lower() == "photo":
            area = (x2 - x1) * (y2 - y1)
            if area > max_photo_area:
                max_photo_area = area
                photo_box_coords = (x1, y1, x2, y2)

        # EXTRACT THE TEXT FROM THE BOX IF IS: description, likes, date, comment
        # comments_background AND description_background ARE IGNORED
        elif label_name.lower() in ["description", "likes", "date"]:
            # TRANSFORM THE IMAGE TO GREY SCALE FOR BETTER TEXT DETECTION
            gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
            # DETECT THE TEXT WITH TESSERACT WITH COMMON LANGUAGES
            text = pytesseract.image_to_string(gray,
                                               lang=languages_list_to_tesseract_lang(COMMON_LANGUAGES))
            # Normalize only the description text
            if label_name.lower() == 'description':
                text = normalize_text(text)

            # print('label:', label_name, ' text:', text)
            # CALCULATE THE LENGTH OF THE TEXT
            text_len = len(text.strip())

            # UPDATE THE LIST WITH BOUNDING BOXES THAT CONTAINS THE GREATEST AMOUNT OF TEXT FOR THE CURRENT LABEL
            if (label_name not in best_text_boxes) or (
                    text_len > best_text_boxes[label_name]['text_len']):
                best_text_boxes[label_name] = {
                    'text': text,
                    'coords': (x1, y1, x2, y2),
                    'text_len': text_len
                }
        elif label_name.lower() in ["comment"]:
            # TRANSFORM THE IMAGE TO GREY SCALE FOR BETTER TEXT DETECTION
            gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
            text = pytesseract.image_to_string(gray,
                                               lang=languages_list_to_tesseract_lang(COMMON_LANGUAGES))
            # normalize the comment
            text = normalize_text(text)
            # print('label:', label_name, ' text:', text)

            # UPDATE THE LIST WITH COMMENTS BOUNDING BOXES (CONTAINS A LIST WITH ALL THE COMMENTS)
            comments_boxes.append({
                'text': text,
                'coords': (x1, y1, x2, y2),
            })

    # COMPUTE THE DICTIONARY WHICH CONTAINS THE BOX IMAGES FOR EACH LABEL, ALONG WITH THEIR EXTRACTED TEXT
    texts_images = {}
    for key, value in best_text_boxes.items():
        x1, y1, x2, y2 = value['coords']
        texts_images[key] = {
            'image': image[y1:y2, x1:x2],
            'text': value['text']
        }
    comments_images = []
    for comm in comments_boxes:
        x1, y1, x2, y2 = comm['coords']
        comments_images.append({
            'image': image[y1:y2, x1:x2],
            'text': comm['text']
        })

    if photo_box_coords:
        x1, y1, x2, y2 = photo_box_coords
        return image[y1:y2, x1:x2], texts_images, comments_images
    return None, texts_images, comments_images


def detect_comments_text_with_specified_language(comments_boxes):
    """
        Receives a list of dictionaries of the detected comments containing the image
        (with which the comment was detected with) and the text extracted without language specified in tesseract model
        :param comments_boxes: list with dictionaries with the image and text associated with the comment
        list: [{'image':image, 'text':text},{'image':image, 'text':text},{'image':image, 'text':text}...]
        :return: list with all the detected comments ['comm1','comm2','comm3','comm4',...]
        """
    if len(comments_boxes) == 0:
        return []
    accurate_comments = []
    for box in comments_boxes:
        try:
            # comments contain the username of the account at the beginning, we remove it so that
            # the language detection is made only on the comment text (without the username of the user's account)
            comment_without_username = ' '.join(box['text'].split()[1:])
            if len(comment_without_username) > 0:
                # print("non accurate text:", comment_without_username)
                # print("denoised text for language detection:",
                #       denoise_text_for_language_analysis(comment_without_username))
                # DETECT THE LANGUAGE OF THE TEXT
                src_lang = predict_text_language(denoise_text_for_language_analysis(comment_without_username))
                print(f"Lang Detected for comment':", src_lang)

                # DETECTS AGAIN THE TEXT WITH SPECIFIED LANGUAGE (BETTER ACCURACY)
                gray = cv2.cvtColor(box['image'], cv2.COLOR_BGR2GRAY)
                # normalize the text before giving it back
                accurate_text = normalize_text(pytesseract.image_to_string(gray, lang=src_lang))
                if len(accurate_text) > 0:
                    accurate_comments.append(accurate_text)
                print("comment with lang text: ", accurate_text)
        except Exception as e:
            # EXCEPTION IF THE PREDICTION COULD NOT BE MADE
            print(f"Error for comment: {e}")

    return accurate_comments


def parse_posts_date(text):
    """
    Date text detected from a post can be in these formats:
    "Month Day" => this year
    "Month Day,Year"
    "2..7 days ago" "1 day ago" => this year
    "2..24 hours ago" "1 hour ago" => TODAY
    "2..60 minutes ago" "1 minute ago" => TODAY
    "2..60 seconds ago" "1 seconds ago" => TODAY
    :param text: the date in text format
    :return: the date parsed or None
    """
    now = datetime.now()

    patterns = [
        (r'\s*([A-Z][a-z]+)\s*(\d{1,2})\s*,\s*(\d{4})\s*',
         lambda m: datetime.strptime(f"{m.group(1)} {m.group(2)} {m.group(3)}", "%B %d %Y")),
        (r"\s*([A-Z][a-z]+)\s*(\d{1,2})\s*(\d{4})\s*",
         lambda m: datetime.strptime(f"{m.group(1)} {m.group(2)} {m.group(3)}", "%B %d %Y")),
        (r'\s*([A-Z][a-z]+)\s*(\d{1,2})\s*',
         lambda m: datetime.strptime(f"{m.group(1)} {m.group(2)} {now.year}", "%B %d %Y")),
        (r'\s*(\d+)\s*days?\s*ago\s*', lambda m: now - timedelta(days=int(m.group(1)))),
        # if the date it's seconds/minutes/hours ago it means the post was posted today
        (r'\s*(\d+)\s*hours?\s*ago\s*', lambda m: now),
        (r'\s*(\d+)\s*minutes?\s*ago\s*', lambda m: now),
        (r'\s*(\d+)\s*seconds?\s*ago\s*', lambda m: now),
    ]

    for pattern, parser in patterns:
        match = re.search(pattern, text)
        if match:
            return parser(match)

    return None  # No match found

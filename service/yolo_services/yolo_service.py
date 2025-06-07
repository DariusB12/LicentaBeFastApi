import re

from ultralytics import YOLO

from service.yolo_services.yolo_posts import extract_post_data, detect_comments_text_with_specified_language, \
    parse_posts_date
from service.yolo_services.yolo_profile import extract_profile_data, detect_description_text_with_specified_language
from service.utils.yolo_utils import base64_to_cv2_img, parse_number, cv2_img_to_base64

yolo_model_profile = YOLO(
    'ai_models/yolov11/insta_profile_model/800px_no_augmentation batch 16 kaggle/weights/best.pt')
# yolo_model_post = YOLO("ai_models/yolov11/insta_post_model/800px_no_augmentation_batch16_kaggle/weights/best.pt")
yolo_model_post = YOLO("ai_models/yolov11/insta_post_model/800px_no_augmentation_batch8_kaggle/weights/best.pt")



# DICTIONARY WITH CLASS INDEXES AS KEYS AND LABEL NAMES AS VALUES
class_names_labels_profile = yolo_model_profile.names
class_names_labels_post = yolo_model_post.names


def detect_from_profile_capture(image_base64):
    """
    Detects the description, no_followers, no_following, no_posts, username and the profile photo from a screen_shot
    of an instagram profile encoded in base64
    :param image_base64: the screen_shot encoded
    :return: the profile photo base64 encoded, the texts of:description and username, and the numbers of followers, following and posts
    Throws 400 BAD_REQUEST if the image is not a valid base64 format

    If data wasn't detected in the image then the following invalid input will be assigned to each label:
    profile_photo: None
    username = ''
    description = ''
    followers = -1
    following = -1
    posts = -1
    """
    image_cv = base64_to_cv2_img(image_base64)

    # DETECT FROM IMAGE USING YOLOv11 MODEL
    results = yolo_model_profile(image_cv)

    profile_photo, text_boxes = extract_profile_data(image_cv, results[0], class_names_labels_profile)

    # WE NEED THE TEXT FROM DESCRIPTION LABEL TO BE EXTRACTED WITH TESSERACT IN ITS LANGUAGE
    language_detected_texts = detect_description_text_with_specified_language(
        text_boxes.get('description') if text_boxes.get('description') is not None else None
    )

    username = ''
    followers = -1
    following = -1
    posts = -1
    if text_boxes.get('username'):
        username = text_boxes['username']['text']
    if text_boxes.get('followers'):
        followers_parsed = parse_number(text_boxes['followers']['text'])
        if followers_parsed is not None:
            followers = followers_parsed
    if text_boxes.get('following'):
        following_parsed = parse_number(text_boxes['following']['text'])
        if following_parsed is not None:
            following = following_parsed
    if text_boxes.get('posts'):
        posts_parsed = parse_number(text_boxes['posts']['text'])
        if posts_parsed is not None:
            posts = posts_parsed
    description = language_detected_texts

    if profile_photo is not None:
        return cv2_img_to_base64(profile_photo), username, description, followers, following, posts
    return profile_photo, username, description, followers, following, posts


def detect_from_post_capture(image_base64):
    """
    Detects description, no_likes, date, comments and the post photo from a screen_shot of an instagram post
    encoded in base64
    :param image_base64: the screen_shot encoded
    :return: the post photo base64 encoded, the texts of:description and comments, the no of likes,
    the no of comments (cannot detect from image, so will always be -1 = private) and the date
    Throws 400 BAD_REQUEST if the image is not a valid base64 format

    If data wasn't detected in the image then the following invalid input will be assigned to each label:
    post_photo: None
    description = ''
    comments: []
    date = None
    no_likes = -1
    no_comments = -1
    """

    image_cv = base64_to_cv2_img(image_base64)

    # DETECT FROM IMAGE USING YOLOv11 MODEL
    results = yolo_model_post(image_cv)

    post_photo, text_boxes, comments_boxes = extract_post_data(image_cv, results[0], class_names_labels_post)

    # WE NEED THE TEXT FROM DESCRIPTION AND COMMENTS TO BE EXTRACTED WITH TESSERACT IN THEIR LANGUAGES
    description_accurate_detected_texts = detect_description_text_with_specified_language(
        text_boxes.get('description')
    )
    comments_accurate_detected_texts = detect_comments_text_with_specified_language(comments_boxes)

    # THE DESCRIPTION AND COMMENTS TEXT DETECTED WITH LANGUAGE SPECIFIED ARE NOW NORMALIZED BUT THE USERNAME
    # OF THE DESCRIPTION/COMMENT AT THE BEGINNING OF THE TEXTS ARE NOT REMOVED, WE NEED TO REMOVE THEM AND
    # IF THE TEXTS ARE EMPTY AFTER THIS PROCESS, THEN THE COMMENT/DESCRIPTION IS REMOVED (CONSIDERED UNDETECTED)

    # remove username from description
    description_accurate_detected_texts = re.sub(r'^\s*\S+\s*', '', description_accurate_detected_texts, count=1)
    # remove username from comments
    for i in range(0, len(comments_accurate_detected_texts)):
        comments_accurate_detected_texts[i] = re.sub(r'^\s*\S+\s*', '', comments_accurate_detected_texts[i], count=1)

    no_likes = -1  # if no likes detected consider them private
    no_comments = -1  # cannot detect no of comments from posts screen_shots so suppose they are private
    date = None

    # Convert likes into numbers or if are not detected, consider them private
    if text_boxes.get('likes') is not None:
        parsed_likes = parse_number(text_boxes['likes']['text'])
        if parsed_likes is not None:
            no_likes = parsed_likes
    # print("likes:", no_likes)

    # Normalized date text
    if text_boxes.get('date') is not None:
        print('date not parsed:', text_boxes['date']['text'])
        parsed_date = parse_posts_date(text_boxes['date']['text'])
        if parsed_date is not None:
            print('date parsed:',parsed_date)
            date = parsed_date
    # print("date:", date)

    if post_photo is not None:
        return (cv2_img_to_base64(post_photo),
                description_accurate_detected_texts, no_likes, no_comments, date, comments_accurate_detected_texts)
    return (post_photo, description_accurate_detected_texts, no_likes,
            no_comments, date, comments_accurate_detected_texts)

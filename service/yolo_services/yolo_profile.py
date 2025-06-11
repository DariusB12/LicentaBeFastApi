import cv2
from pytesseract import pytesseract

from logging_config import logger
from service.utils.yolo_utils import languages_list_to_tesseract_lang
from service.utils.lang_utils import normalize_text, COMMON_LANGUAGES, predict_text_language_fasttext_lid218, \
    normalize_text_for_language_analysis, MAX_CHARACTERS_LENGTH_LINGUA, predict_text_language_lingua


def extract_profile_data(image, image_results, class_names):
    """
    Extracts the profile photo and a dictionary with the rest of the images with their extracted text from it with
    pytesseract (with the common languages specified).

    The bounding box for the profile image is selected based on the bounding box with the biggest area, and the bounding
    boxes with texts, are selected based on the box that contains the greatest amount of text for a specific label

    :param class_names: the names of the bounding boxes labels
    :param image: the image to which the results with bounding-boxes corresponds
    :param image_results: the bounding boxes extracted from the image
    :return: profile photo, and a dictionary with the rest of the images
    description/followers/following/posts/username: {image: ... , text: ...}
    """
    # COORDINATES FOR PHOTO WITH BIGGEST AREA
    photo_box_coords = None
    max_photo_area = 0
    # OBJECT WITH COORDINATED FOR TEXT BOXES
    best_text_boxes = {}

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

        # EXTRACT THE TEXT FROM THE BOX IF IS: description, followers, following, posts or username
        # background AND followed_by ARE IGNORED
        elif label_name.lower() not in ["background", "followed_by"]:
            # TRANSFORM THE IMAGE TO GREY SCALE FOR BETTER TEXT DETECTION
            gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
            # DETECT THE TEXT WITH TESSERACT WITH COMMON LANGUAGES
            text = pytesseract.image_to_string(gray,
                                               lang=languages_list_to_tesseract_lang(COMMON_LANGUAGES))
            # Normalize only the description text
            if label_name.lower() == 'description':
                text = normalize_text(text)
                # Remove description if FollowedBy box is confused by yolo model with Description box
                if text.lower().startswith('followed by') | text.lower().startswith(' followed by'):
                    text = ''
            # print('label:',label_name,' text:',text)

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

    # COMPUTE THE DICTIONARY WHICH CONTAINS THE BOX IMAGES FOR EACH LABEL, ALONG WITH THEIR EXTRACTED TEXT
    texts_images = {}
    for key, value in best_text_boxes.items():
        x1, y1, x2, y2 = value['coords']
        texts_images[key] = {
            'image': image[y1:y2, x1:x2],
            'text': value['text']
        }

    if photo_box_coords:
        x1, y1, x2, y2 = photo_box_coords
        return image[y1:y2, x1:x2], texts_images
    return None, texts_images


def detect_description_text_with_specified_language(description_boxes):
    """
    Receives a dictionary of the description containing the image (which the description was detected with) and
    the text extracted without language specified in tesseract model
    :param description_boxes: dictionary with the image and text associated with the description
    dictionary: {'image':image, 'text':text}
    :return: the description extracted with language specified in tesseract
    """
    if description_boxes is None:
        return ''
    accurate_description = ''
    try:
        # profile description contains the username of the account at the beginning, we remove it so that
        # the language detection is made only on the description text (without the username of the user's account)
        description_without_username = ' '.join(description_boxes['text'].split()[1:])
        if len(description_without_username) > 0:
            print("non accurate text:", description_without_username)
            description_without_username_denoised = normalize_text_for_language_analysis(description_without_username)
            print("denoised text for language detection:", description_without_username_denoised)
            # VERIFY IF IT IS A SHORT/LONG TEXT
            if len(description_without_username_denoised) <= MAX_CHARACTERS_LENGTH_LINGUA:
                # DETECT THE LANGUAGE WITH LINGUA
                src_lang = predict_text_language_lingua(description_without_username_denoised)
                print(f"Lang lingua for description:", src_lang)
            else:
                # DETECT THE LANGUAGE WITH lid218
                src_lang = predict_text_language_fasttext_lid218(description_without_username_denoised)
                print(f"Lang lid218 for description:", src_lang)

            # DETECTS AGAIN THE TEXT WITH SPECIFIED LANGUAGE (BETTER ACCURACY)
            gray = cv2.cvtColor(description_boxes['image'], cv2.COLOR_BGR2GRAY)
            # normalize the text before giving it back
            accurate_text = normalize_text(pytesseract.image_to_string(gray, lang=src_lang))
            if len(accurate_text) > 0:
                accurate_description = accurate_text
            # print("accurate text: ", accurate_text)
    except Exception as e:
        logger.error('prediction could not be made')
        # EXCEPTION IF THE PREDICTION COULD NOT BE MADE
        print(f"Error for description: {e}")

    return accurate_description

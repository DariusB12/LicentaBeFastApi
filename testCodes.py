from dotenv import load_dotenv
import os

from ultralytics import YOLO

model = YOLO(
    "D:\\UBB\\Licenta\\app\\TrasaturiPersonalitateBe\\LicentaBeFastApi\\ai_models\\yolov11\\insta_profile_model\\800px_no_augmentation batch 16 kaggle\\weights\\best.pt")


if __name__ == '__main__':
    metrics = model.val()
    print(metrics.box.map)  # mAP50-95
    # # Încarcă variabilele din fișierul .env
    # load_dotenv()
    #
    # # Accesează variabila de mediu
    # database_url = os.getenv("DATABASE_URL")
    #
    # print("DATABASE_URL:", database_url)
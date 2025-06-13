from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from database_connection.database import Base
from sqlalchemy.types import TypeDecorator, TEXT
import json

from model.enums.BigFiveModelType import BigFiveModelType
from model.enums.GeneralEmotionType import GeneralEmotionType
from model.enums.HobbyType import HobbyType
from model.enums.InterestDomainType import InterestDomainType
from model.enums.PersonalityType import PersonalityType


class JSONEncodedList(TypeDecorator):
    """
    Encoding/Decoding JSON for lists of enums
    """
    impl = TEXT

    def __init__(self, enum_class, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.enum_class = enum_class

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        return json.dumps([item.value for item in value])

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        return [self.enum_class(item) for item in json.loads(value)]


class JSONEncodedEnumKeyDict(TypeDecorator):
    """
    Encoding/Decoding JSON for dictionaries with enums as keys
    """
    impl = TEXT

    def __init__(self, enum_class, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.enum_class = enum_class

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        return json.dumps({k.value: v for k, v in value.items()})

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        return {self.enum_class(k): v for k, v in json.loads(value).items()}


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)


class SocialMediaAccount(Base):
    __tablename__ = "social_media_accounts"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, nullable=False)
    profile_description = Column(String, default='', nullable=False)
    no_followers = Column(Integer, default=0, nullable=False)
    no_following = Column(Integer, default=0, nullable=False)
    no_of_posts = Column(Integer, default=0, nullable=False)
    profile_photo_filename = Column(String, nullable=False)  # STORE THE PATH OF THE PROFILE PHOTO
    modified = Column(Boolean, nullable=False,
                      default=False)  # TRUE IF THE ANALYSIS WAS MADE BEFORE AN UPDATE ON ENTITY

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)


class Analysis(Base):
    __tablename__ = "analysis"
    id = Column(Integer, primary_key=True, index=True)

    interest_domains = Column(JSONEncodedList(InterestDomainType))
    hobbies = Column(JSONEncodedList(HobbyType))

    general_emotions = Column(JSONEncodedEnumKeyDict(GeneralEmotionType))
    personality_types = Column(JSONEncodedEnumKeyDict(PersonalityType))
    big_five_model = Column(JSONEncodedEnumKeyDict(BigFiveModelType))

    creationDate = Column(DateTime, nullable=False)

    social_account_id = Column(Integer, ForeignKey("social_media_accounts.id"), unique=True, nullable=False)


class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    description = Column(String, default='', nullable=False)
    noLikes = Column(Integer, default=-1, nullable=False)
    noComments = Column(Integer, default=-1, nullable=False)
    datePosted = Column(DateTime, nullable=False)

    social_account_id = Column(Integer, ForeignKey("social_media_accounts.id"), nullable=False)


class PostPhoto(Base):
    __tablename__ = "post_photos"

    id = Column(Integer, primary_key=True, index=True)
    post_photo_filename = Column(String,
                                 nullable=False)  # STORE THE PATHS OF THE PHOTOS, AND PHOTOS ARE STORED ON SYSTEM

    post_id = Column(Integer, ForeignKey("posts.id"), nullable=False)


class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(String, nullable=False)

    post_id = Column(Integer, ForeignKey("posts.id"), nullable=False)


User.social_accounts = relationship("SocialMediaAccount", back_populates="user", cascade="all, delete-orphan")

SocialMediaAccount.user = relationship("User", back_populates="social_accounts")
SocialMediaAccount.posts = relationship("Post", back_populates="social_account", cascade="all, delete-orphan")
SocialMediaAccount.analysis = relationship("Analysis", back_populates="social_account", uselist=False,
                                           cascade="all, delete-orphan")

Analysis.social_account = relationship("SocialMediaAccount", back_populates="analysis")

Post.photos = relationship("PostPhoto", back_populates="post", cascade="all, delete-orphan")
Post.comments = relationship("Comment", back_populates="post", cascade="all, delete-orphan")
Post.social_account = relationship("SocialMediaAccount", back_populates="posts")

PostPhoto.post = relationship("Post", back_populates="photos")
Comment.post = relationship("Post", back_populates="comments")

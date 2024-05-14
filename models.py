from sqlalchemy import Column, Column as mapped_column, Text, ForeignKey ,Enum ,Float ,String, Integer, TIMESTAMP 
from sqlalchemy.orm import declarative_base, Mapped, relationship
from pydantic import BaseModel


Base = declarative_base()

#注册表单
class User_FormBase(BaseModel):
    phone_number: str
    password: str
 
#更改用户数据
class UserBase(BaseModel):
    name: str         #姓名
    birth: str        #生日
    gender: str       #性别
    bio: str          #简历
    about: str        #介绍
    coin: str         #硬币
 
#创建订单
class UserOrderCreateBase(BaseModel):
    general_situation: str
    specific_question: str
    attach_picture: str     #存照片之后改#

class UserOrderRewardBase(BaseModel):
    rating: str
    write_review: str
    reward: int
class UserCollectionBase(BaseModel):
    user_id: int
    adviser_id: int

#顾问
class Adviser_FormBase(BaseModel):
    phone_number: str
    password: str

class AdviserBase(BaseModel):
    name: str
    bio: str
    work: str
    about: str

class AdviserOrderBase(BaseModel):
    order_status: str

class AdviserServiceBase(BaseModel):
    id: int
    service_adjustment: str
    amount_adjustment: str

class AdviserReplyBase(BaseModel):
    reply_text: str

#用户
class User_FormEntity(Base):
    __tablename__ = "user_logon"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    phone_number: Mapped[str] = mapped_column(String(100), nullable=False)
    password: Mapped[str] = mapped_column(String(100), nullable=False)

class UserEntity(Base):
    __tablename__ = "user_info"
    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    birth = Column(String(50))
    gender = Column(String(20))
    bio = Column(Text)
    about = Column(Text)
    coin  = Column(Integer)

#订单创建
class UserOrderCreation(Base):
    __tablename__ = "user_order_creation"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user_info.id'))
    user_data = relationship("UserEntity")
    general_situation = Column(Text)
    specific_question = Column(Text)
    attach_picture = Column(String(200))
    order_id = Column(String(20))
    order_time = Column(String(200))
    delivery_time = Column(String(200))
    status = Column(Enum( 'Pending', 'Expired', 'Completed', 'Expedited', 'Timeout'))

class UserOrderReward(Base):
    __tablename__ = "user_order_reward"
    id = Column(Integer, primary_key=True)
    adviser_id = Column(Integer, ForeignKey("adviser_reply.id"))
    adviser_data = relationship("AdviserReply")
    rating = Column(Float)
    write_review = Column(Text)
    reward = Column(Integer)
    write_time = Column(String(200))

class UserCollection(Base):
    __tablename__ ="user_collection_adviser"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user_info.id'))
    user_data = relationship("UserEntity")
    adviser_id = Column(Integer, ForeignKey('adviser_info.id'))
    adviser_data = relationship("AdviserEntity")

class UserCoinFlow(Base):
    __tablename__ = "user_coin_flow"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user_info.id'))
    coin_change = Column(Integer)
    description = Column(String)
    timestamp = Column(TIMESTAMP)

 #顾问
class Adviser_FormEntity(Base):
    __tablename__ = "adviser_logon"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    phone_number: Mapped[str] = mapped_column(String(100), nullable=False)
    password: Mapped[str] = mapped_column(String(100), nullable=False)

class AdviserEntity(Base):
    __tablename__ = "adviser_info"
    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    bio = Column(Text)
    work = Column(String(50))
    about = Column(Text)

class AdviserHomeEntity(Base):
    __tablename__ = "adviser_home"
    id = Column(Integer, primary_key=True)
    name = Column(String(200))
    coin = Column(Integer)
    work_state = Column(String(200))
    readings = Column(Integer)
    score = Column(Integer)
    comments = Column(Integer)
    on_time = Column(Float)
    reviews = Column(Text)
    complete = Column(Integer)

class AdviserOrderStatus(Base):
    __tablename__ = "adviser_order_status"
    id = Column(Integer, primary_key=True)
    adviser_home_id = Column(Integer,ForeignKey('adviser_home.id'))
    adviser_home_data = relationship("AdviserHomeEntity")
    name = Column(String)
    order_status = Column(Enum('work','idle'))

class AdviserServiceSettings(Base):
    __tablename__ = "adviser_service_settings"
    id = Column(Integer, primary_key=True)
    adviser_id = Column(Integer, ForeignKey('adviser_info.id'))
    adviser_data = relationship("AdviserEntity")
    amount_adjustment = Column(String)
    service_adjustment = Column(Enum( 'open','close'))

class AdviserReply(Base):
    __tablename__ = "adviser_reply"
    id = Column(Integer, primary_key=True)
    adviser_id = Column(Integer, ForeignKey('adviser_home.id'))
    adviser = relationship("AdviserHomeEntity")
    order_id = Column(Integer, ForeignKey('user_order_creation.id'))
    user_order = relationship("UserOrderCreation")
    reply_text = Column(Text)

#用户
class User_FormCreate(User_FormBase):
    ...
class User_FormOut(User_FormBase):
    id: int
class UserOut(BaseModel):
    id: int

#顾问
class Adviser_FormCreate(Adviser_FormBase):
    ...
class Adviser_FormOut(Adviser_FormBase):
    id: int
class AdviserOut(BaseModel):
    id: int



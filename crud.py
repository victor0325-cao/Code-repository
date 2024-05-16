from fastapi import APIRouter, Depends
from sqlalchemy import select
from datetime import datetime, timedelta, timezone
from sqlalchemy.sql.expression import asc
from jose import jwt
from typing import List
import redis, asyncio
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from core.db import SessionDep
from core.security import get_current_user, SECRET_KEY, ALGORITHMS, Token
from random_number import generate_number
from timing import update_status
from models import *


router = APIRouter()


#用户注册
@router.post("/user/logon/",tags=["User"],response_model=User_FormOut)
async def create_user(
    user:User_FormCreate,
    session: SessionDep
    ):
    user_entity = User_FormEntity(phone_number = user.phone_number, password = user.password)
    session.add(user_entity)
    session.commit()
    return user_entity

@router.post("/user/login_token/",tags=["User"])
async def login(login_form: OAuth2PasswordRequestForm = Depends()):
    session = Session()
    try:
        user = session.query(User_FormEntity).filter(User_FormEntity.phone_number == login_form.username).first()
        if not user or user.password != login_form.password:
            raise HTTPException(status_code = 401,
                detail = "Incorrect phone_number or password",
                headers = {"WWW-Authenticate": "Bearer"})

        token_expires = datetime.now(timezone.utc) + timedelta(minutes = 30)
        token_data = {
            "phone_number": login_form.username,
            "exp": token_expires
            }
        token = jwt.encode(token_data, SECRET_KEY, ALGORITHMS)
        return Token(access_token = token, token_type = "bearer")
    finally:
        session.close()

#修改信息
@router.put("/user/info/",tags=["User"],response_model=UserOut)
async def update_user(
    user_id: int,   
    user: UserBase,
    session: SessionDep,
    phone_number: str = Depends(get_current_user)
    ):
    user_entity = session.query(UserEntity).filter(UserEntity.id == user_id).first()
    if user_entity:
        user_entity.name = user.name
        user_entity.birth = user.birth
        user_entity.gender = user.gender
        user_entity.bio = user.bio
        user_entity.about = user.about
        user_entity.coin = user.coin
        try:
            session.commit()
            session.refresh(user_entity)
            return UserOut(id=user_entity.id, message="User updated successfully")
        except sqlalchemy.exc.IntegrityError as e:
            raise HTTPException(status_code=400, detail="Error updating user: " + str(e))
        else:
             raise HTTPException(status_code=404, detail="User not found")

#显示顾问列表
@router.get("/user/adviser_list/",tags=["User"])
def user_adviser_list(session: SessionDep) -> List:
    user_adviser = session.query(AdviserEntity).order_by(asc(AdviserEntity.name)).all()
    results = [{
        "name": adviser.name,
        "bio": adviser.bio
        }for adviser in user_adviser
        ] 
    return results 

#显示顾问主页
@router.get("/user/adviser/home/",tags=["User"])
async def user_adviser_home(session: SessionDep) -> List:
    user_adviser = session.query(AdviserEntity,AdviserServiceSettings).join(AdviserServiceSettings).all()
    results = [{
        "name":adviser_Entity.anme,
        "bio":adviser_Entity.bio,
        "Text resding": service_settings.amount_adjustment,
        "About Me": adviser_Entity.about
        }for adviser_Entity, service_settings in user_adviser
        ]
    return results

#订单创建#
@router.post("/user/order_create",tags=["User"])
async def order_create(
    user_id: int,  
    order_create: UserOrderCreateBase,
    session: SessionDep
    ):
    user = session.query(UserEntity).filter(UserEntity.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not fount")

    order_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    delivery = (datetime.now() + timedelta(hours=24)).strftime('%Y-%m-%d %H:%M:%S')
#添加信息
    new_order = UserOrderCreation(
        user_id = user_id,
        general_situation = order_create.general_situation,
        specific_question = order_create.specific_question,
        attach_picture = order_create.attach_picture,
        order_id = generate_number(18),
        order_time = order_time,
        delivery_time = delivery,
        status = "Pending"
        )
    user.coin -= 10

    # 启动异步定时任务
    asyncio.create_task(update_status(order_time))

    session.add(new_order)
    session.commit()

    return {
        "name ": user.name,
        "coin": user.coin,
        "basic information":{
            "name": user.name,
            "birth": user.birth,
            "gender": user.gender
            }, 
        "general_situation": order_create.general_situation,
        "specific_question": order_create.specific_question,
        "attach_picture": order_create.attach_picture
        }

#订单列表
@router.get("/user/order_list",tags=["User"])
async def order_list(
    session: SessionDep,
    phone_number: str = Depends(get_current_user)
    ):
    user_list = session.query(UserEntity, UserOrderCreation).join(UserOrderCreation).all()
    results = []
    for user_entity, order_creation in user_list:
        user_dict = {
            "name": user_entity.name,
            "order_time": order_creation.order_time,
            "specific_question": order_creation.specific_question,
            "status": order_creation.status
            }
    results.append(user_dict)
    return results

#订单详情
redis_client = redis.StrictRedis(host ='0.0.0.0', port=6379, decode_responses=True)
@router.get("/user/order_details",tags=["User"])
async def order_details(
    session: SessionDep,
    phone_number: str = Depends(get_current_user)
    ):

    cache_key = f"user_order_details:{phone_number}"
    cached_results = redis_client.get(cache_key)
    if cached_results:
        return json.loads(cached_results)

    results = []
    for user_entity, order_creation in user_details:

        user_dict = {
            "name": user_entity.name,
            "status": order_creation.status,
            "order_time": order_creation.order_time,
            "Order ID":order_creation.order_id,
            "general_situation":order_creation.general_situation,
            "specific_question": order_creation.specific_question
            }
        results.append(user_dict)
    return results

#用户打赏
@router.post("/user/order_reward",tags=["User"])
async def order_reward(
    adviser_id: str , 
    order_reward: UserOrderRewardBase,
    session: SessionDep,
    phone_number: str = Depends(get_current_user)
    ):
    if not user_reward:
        raise HTTPException(status_code=404, detail="Order not found")
    write_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    new_reward = UserOrderReward(
        rating = order_reward.rating,
        write_review = order_reward.write_review,
        reward = order_reward.reward,
        write_time = write_time
        )
    user_reward.adviser.coin = user_reward.adviser.coin + new_reward.reward
    user_reward.adviser.readings += 1
    user_reward.adviser.comments += 1
    user_reward.adviser.complete += 1

    session.add(new_reward)
    session.commit()

    return {
        "Adviser Name":user_reward.adviser.name,
        "Rating": new_reward.rating,
        "write_review": new_reward.write_review,
        "reward": new_reward.reward
        }

#收藏顾问
@router.post("/user/collection_adviser",tags=["User"])
async def collection_adviser(
    user_id: str,
    collection_data: UserCollectionBase,
    session: SessionDep,
    phone_number: str = Depends(get_current_user)
    ):

    if not user_collection:
        raise HTTPException(status_code=404, detail="User not found")

    collection = UserCollection(
        user_id = collection_data.user_id,
        adviser_id = collection_data.adviser_id,
        )
    session.add(collection)
    session.commit()

    return{
        "User Name":user_collection.name,
        "Adviser Name": collection.adviser_data.name,
        } 

#用户流水
@router.post("/user/coin_flow",tags=["User"])
async def user_coin_flow(
    user_id: int, 
    coin_change: int, 
    description: str,
    session: SessionDep,
    phone_number: str = Depends(get_current_user)
    ):
    user = session.query(UserEntity).get(user_id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    current_timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    coin_flow = UserCoinFlow(
        user_id = user.id,
        coin_change = coin_change,
        description = description,
        timestamp = current_timestamp
        )

    deduction_now = user.coin + coin_flow.coin_change

    if user:
        user.coin = deduction_now

    session.add(coin_flow)
    session.commit()

    return {
        "Deduction old":user.coin,
        "Deduction now":deduction_now
        }

##adviser顾问端##
#顾问注册
@router.post("/adviser/logon/",tags=["Adviser"], response_model=Adviser_FormOut)
async def create_adviser(
    adviser: Adviser_FormCreate,
    session: SessionDep
    ):
    adviser_entity = Adviser_FormEntity(
        phone_number = adviser.phone_number, 
        password = adviser.password
        )
    session.add(adviser_entity)
    session.commit()
    return adviser_entity

#修改信息
@router.put("/adviser/info/",tags=["Adviser"],response_model=AdviserOut)
async def update_adviser(
    adviser_id: int, adviser: AdviserBase,
    session: SessionDep
    ):
    adviser_entity = session.query(AdviserEntity).filter(AdviserEntity.id == adviser_id).first()
    if adviser_entity:

        adviser_entity.name = adviser.name
        adviser_entity.bio = adviser.bio
        adviser_entity.work = adviser.work
        adviser_entity.about = adviser.about

        try:
            session.commit()
            session.refresh(adviser_entity)
            return AdviserOut(id=adviser_entity.id, message="User updated succ essfull    y")
        except sqlalchemy.exc.IntegrityError as e:
            raise HTTPException(status_code=400, detail="Error updating user: " + str(    e))
        else:
            raise HTTPException(status_code=404 , detail="User not found")

#显示信息
@router.get("/adviser/home/",tags=["Adviser"])
async def adviser_home(
    session: SessionDep
    ):
    adviser =  select(AdviserHomeEntity).order_by(asc (AdviserHomeEntity.name))
    return session.execute(adviser).scalars().all()

#顾问接单状态更新
@router.patch("/adviser/home/",tags=["Adviser"])
async def update_adviser(
    adviser_id: int,
    adviser: AdviserOrderBase,
    session: SessionDep
    ):
    adviser_entity = session.query(AdviserOrderStatus).filter(AdviserOrderStatus.id == adviser_id).first()

    if adviser_entity:
        adviser_entity.order_status = adviser.order_status
        try:
            session.commit()
            session.refresh(adviser_entity)
            return AdviserOut(id=adviser_entity.id, message="User updated successfully")
        except sqlalchemy.exc.IntegrityError as e:
            raise HTTPException(status_code=400, detail="Error updating user: " + str(e))
        else:
            raise HTTPException(status_code=404, detail="User not found")

#顾问服务状态打开，关闭，金额调整
@router.post("/adviser/home/service_settings",tags=["Adviser"])
async def update_service(
    adviser_id: int,adviser: AdviserServiceBase,
    session: SessionDep
    ):
    adviser_service = session.query(AdviserServiceSettings).filter(AdviserServiceSettings.id == adviser_id).first()

    if adviser_service:
        adviser_service.service_adjustment = adviser.service_adjustment
        if adviser.service_adjustment == 'open':
            adviser_service.amount_adjustment = adviser.amount_adjustment

        try:
            session.commit()
            session.refresh(adviser_service)
            return AdviserOut(id=adviser_service.id, message="User updated successfull    y")
        except sqlalchemy.exc.IntegrityError as e:
            raise HTTPException(status_code=400, detail="Error updating user: " + str(    e))
        else:
             raise HTTPException(status_code=404, detail="User not found")

#回复用户
@router.post("/adviser/reply_user",tags=["Adviser"])
async def reply_user(
    adviser_id: int, 
    order_id: str, 
    adviser_reply: AdviserReplyBase,
    session: SessionDep
    ):
    user_order = session.query(UserOrderCreation).filter(UserOrderCreation.id == order_id).first()

    if not user_order:
        raise HTTPException(status_code=404, detail="Order not found")

    reply_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    delivery_time = reply_time

    new_reply = AdviserReply(
        adviser_id = adviser_id,
        order_id = order_id,
        reply_text = adviser_reply.reply_text
        )
    adviser = session.query(AdviserHomeEntity).get(adviser_id)
#这里对顾问回复获得金币未做限制，同一个顾问，同一个订单多次回复，多次增加
    if adviser:
        adviser.coin += 10

    if user_order:
        user_order.status = "Completed"
        user_order.delivery_time = reply_time

    session.add(new_reply)
    session.commit()

    return {
        "Adviser Name": adviser.name,
        "status": user_order.status,
        "Order Time": user_order.order_time,
        "Delivery Time": reply_time,
        "Order ID": order_id,
        "Request Details":{
            "Name": user_order.user_data.name,
            "Date of Birth": user_order.user_data.birth,
            "Gender": user_order.user_data.gender,
            "General Situation": user_order.general_situation,
            "Specific Question": user_order.specific_question,
            "Reply":new_reply.reply_text
             }
        }

#顾问端：用户金币
@router.post("/adviser/user_coin_flow",tags=["Adviser"])
async def user_coin_flow(
    user_id: int, 
    coin_change: int,
    description: str, 
    session: SessionDep
    ):
    user = session.query(UserEntity).get(user_id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    current_timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    user.coin += coin_change

    coin_flow = UserCoinFlow(
        user_id = user.id,
        coin_change = coin_change,
        description = description,
        timestamp = current_timestamp
        )

    session.add(coin_flow)
    session.commit()

    coin_flows = session.query(UserCoinFlow).all()

    coin_flow = [{
        "id": flow.id,
        "user_id": flow.user_id,
        "coin_change": flow.coin_change,
        "description": flow.description,
        "timestamp": flow.timestamp.strftime('%Y-%m-%d %H:%M:%S')
        }for flow in coin_flows
        ]

    return {"coin_flows": coin_flows}

import asyncio

#异步定时任务
async def update_status(order_time):
    try:
        order = db_session.query(UserOrderCreation).filter(UserOrderCreation.order_time == order_time).first()
        if order.sattus == "expedited":
            order.user_data.coin -= 5
            await asyncio.sleep(60*60)  # 延迟1小时
            order.status = "Pending"
            order.user_data.coin += 5
            
            await asyncio.sleep(24*60*60)  # 延迟24小时
            if order.status == "Pending":
                order.user_data.coin += 10
                order.status = "Expired"
                db_session.commit()
#                if order.status == "Expired":
#                    order.status = "TimeOut"
    except Exception as e:
        print(f"An exception occurred in update_status: {e}")

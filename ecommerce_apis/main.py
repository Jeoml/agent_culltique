from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

import models
import schemas
from database import engine, get_db

app = FastAPI()

# Create tables (on startup)
@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)

@app.get("/order-status/{order_id}", response_model=schemas.OrderStatusResponse)
async def get_order_status(order_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(models.Order).where(models.Order.order_id == order_id)
    )
    order = result.scalars().first()

    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    return schemas.OrderStatusResponse(
        order_id=order.order_id,
        status=order.status,
        tracking_id=order.tracking_id
    )

@app.get("/transit-status/{tracking_id}", response_model=schemas.TransitStatusResponse)
async def get_transit_status(tracking_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(models.Transit).where(models.Transit.tracking_id == tracking_id))
    transit = result.scalars().first()
    if not transit:
        raise HTTPException(status_code=404, detail="Tracking ID not found")
    return transit
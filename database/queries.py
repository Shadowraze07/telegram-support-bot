import logging
from typing import List, Optional, Any
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from database.db import async_session
from database.models import User, Ticket

# --- РАБОТА С ПОЛЬЗОВАТЕЛЯМИ ---

async def get_user(tg_id: int) -> Optional[User]:
    """
    Получение пользователя по его Telegram ID .
    Используется для проверки регистрации при входе.
    """
    try:
        async with async_session() as session:
            return await session.scalar(select(User).where(User.telegram_id == tg_id))
    except SQLAlchemyError as e:
        logging.error(f"SQL-ошибка в get_user: {e}") 
        return None

async def add_user(tg_id: int, name: str, group: str, phone: str = None) -> None:
    """
    Регистрация нового пользователя в базе данных .
    """
    try:
        async with async_session() as session:
            user = User(telegram_id=tg_id, name=name, group=group, phone=phone)
            session.add(user)
            await session.commit()
            logging.info(f"Новый пользователь зарегистрирован: ID {tg_id}") # Логирование входа
    except SQLAlchemyError as e:
        logging.error(f"SQL-ошибка в add_user: {e}")
        await session.rollback()

# --- РАБОТА С ЗАЯВКАМИ ---

async def add_ticket(user_tg_id: int, text: str, photo: str = None) -> Optional[int]:
    """
    Создание новой заявки от пользователя .
    Возвращает ID созданной заявки.
    """
    try:
        async with async_session() as session:
            user = await session.scalar(select(User).where(User.telegram_id == user_tg_id))
            if user:
                ticket = Ticket(user_id=user.id, text=text, photo=photo)
                session.add(ticket)
                await session.commit()
                return ticket.id
            return None
    except SQLAlchemyError as e:
        logging.error(f"SQL-ошибка в add_ticket: {e}")
        return None

async def get_my_tickets(user_tg_id: int) -> List[Ticket]:
    """
    Получение истории заявок конкретного пользователя .
    """
    try:
        async with async_session() as session:
            user = await session.scalar(select(User).where(User.telegram_id == user_tg_id))
            if user:
                res = await session.execute(select(Ticket).where(Ticket.user_id == user.id))
                return list(res.scalars().all())
            return []
    except SQLAlchemyError as e:
        logging.error(f"SQL-ошибка в get_my_tickets: {e}")
        return []

# --- ФУНКЦИИ АДМИНИСТРАТОРА ---

async def get_all_users() -> List[User]:
    """
    Получение списка всех зарегистрированных пользователей .
    """
    try:
        async with async_session() as session:
            result = await session.execute(select(User))
            return list(result.scalars().all())
    except SQLAlchemyError as e:
        logging.error(f"SQL-ошибка в get_all_users: {e}")
        return []

async def get_all_tickets() -> List[Any]:
    """
    Получение всех заявок с именами авторов .
    """
    try:
        async with async_session() as session:
            res = await session.execute(select(Ticket, User.name).join(User))
            return list(res.all())
    except SQLAlchemyError as e:
        logging.error(f"SQL-ошибка в get_all_tickets: {e}")
        return []

async def get_user_by_ticket_id(ticket_id: int) -> Optional[int]:
    """
    Поиск Telegram ID пользователя по номеру его заявки.
    Необходим для отправки личного ответа админа .
    """
    try:
        async with async_session() as session:
            result = await session.execute(
                select(User.telegram_id).join(Ticket, User.id == Ticket.user_id).where(Ticket.id == ticket_id)
            )
            return result.scalar()
    except SQLAlchemyError as e:
        logging.error(f"SQL-ошибка в get_user_by_ticket_id: {e}")
        return None

async def update_ticket_status(ticket_id: int, new_status: str) -> bool:
    """
    Изменение статуса заявки администратором .
    Логирует действие без ПД .
    """
    try:
        async with async_session() as session:
            ticket = await session.get(Ticket, ticket_id)
            if ticket:
                ticket.status = new_status
                await session.commit()
                # Логирование действий администраторов (ТЗ п. 6.0)
                logging.info(f"Статус заявки №{ticket_id} изменен на '{new_status}'")
                return True
            return False
    except SQLAlchemyError as e:
        logging.error(f"SQL-ошибка при обновлении статуса №{ticket_id}: {e}")
        return False
    
async def get_tickets_by_status(status: str) -> List[Any]:
    """
    Фильтрация заявок по переданному статусу.
    """
    try:
        async with async_session() as session:
            res = await session.execute(
                select(Ticket, User.name).join(User).where(Ticket.status == status)
            )
            return list(res.all())
    except SQLAlchemyError as e:
        logging.error(f"SQL-ошибка в get_tickets_by_status: {e}")
        return []
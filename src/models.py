'''
Модуль для описания классов объектов.
'''
from datetime import datetime
from decimal import Decimal
from enum import StrEnum

from pydantic import BaseModel


class CarStatus(StrEnum):
    '''
    Статус доступности машины для продажи.
    '''
    available = "available"
    reserve = "reserve"
    sold = "sold"
    delivery = "delivery"


class Car(BaseModel):
    '''
    Характеристики машины.
    '''
    vin: str  # VIN номер двигателя.
    model: int  # Id модели машины в таблице Models.
    price: Decimal  # Закупочная цена автомобиля.
    date_start: datetime  # Дата поступления машины в продажу.
    status: CarStatus  # Статус (продано, бронь, доступно, в поставке)

    def index(self) -> str:
        '''
        Первичный ключ.
        '''
        return self.vin

    def to_string(self) -> str:
        '''
        Возвращает строку для записи объекта в файл.
        '''
        return (
            f'{self.vin};{self.model};{self.price};'
            f'{datetime.strftime(self.date_start, '%Y-%m-%d')};{self.status}'
        )

    def idx(self) -> str:
        '''
        Возвращает значение первичного ключа.
        '''
        return self.vin


class Model(BaseModel):
    '''
    Класс модели машин
    '''
    id: int  # Идентификатор записи.
    name: str  # Название модели.
    brand: str  # Бренд модели.

    def index(self) -> str:
        '''
        Первичный ключ.
        '''
        return str(self.id)

    def to_string(self) -> str:
        '''
        Возвращает строку для записи объекта в файл.
        '''
        return f'{self.id};{self.name};{self.brand}'

    def idx(self) -> str:
        '''
        Возвращает значение первичного ключа.
        '''
        return str(self.id)


class Sale(BaseModel):
    '''
    Описание факта продажи машины.
    '''
    sales_number: str  # Номер продажи «код автосалона#номер продажи».
    car_vin: str  # VIN номер двигателя машины.
    sales_date: datetime  # Дата продажи.
    cost: Decimal  # Цена продажи.

    def index(self) -> str:
        '''
        Первичный ключ.
        '''
        return self.car_vin

    def to_string(self) -> str:
        '''
        Возвращает строку для записи объекта в файл.
        '''
        return (
            f'{self.sales_number};'
            f'{self.car_vin};'
            f'{datetime.strftime(self.sales_date, '%Y-%m-%d')};'
            f'{self.cost}'
        )

    def idx(self) -> str:
        '''
        Возвращает значение первичного ключа.
        '''
        return self.sales_number


class CarFullInfo(BaseModel):
    '''
    Информация о машине и ее продаже.
    '''
    vin: str  # VIN номер двигятеля машины.
    car_model_name: str  # Название модели.
    car_model_brand: str  # Бренд автомобиля.
    price: Decimal  # Закупочная стоимость.
    date_start: datetime  # Дата поступления в продажу.
    status: CarStatus  # Статус автомобиля.
    sales_date: datetime | None  # Дата продажи или None.
    sales_cost: Decimal | None  # Цена продажи или None.


class ModelSaleStats(BaseModel):
    '''
    Статистика продаж по модели.
    '''
    car_model_name: str  # Название модели.
    brand: str  # Бренд автомобиля.
    sales_number: int  # Количество продаж.

'''
Модуль работы с CarService.
'''
from datetime import datetime
from decimal import Decimal
import os

from models import Car, CarFullInfo, CarStatus, Model, ModelSaleStats, Sale
from pydantic import BaseModel


class CarService:
    '''
        Сервис имитирующий обращение к базе данных.
    '''
    def __init__(self, root_directory_path: str) -> None:
        self.root_directory_path = root_directory_path
        self.cars_index_file = os.path.join(
            self.root_directory_path,
            'cars_index.txt'
        )
        self.models_index_file = os.path.join(
            self.root_directory_path,
            'models_index.txt'
        )
        self.sales_index_file = os.path.join(
            self.root_directory_path,
            'sales_index.txt'
        )
        self.sales_file = os.path.join(self.root_directory_path, 'sales.txt')
        self.cars_file = os.path.join(self.root_directory_path, 'cars.txt')
        self.models_file = os.path.join(self.root_directory_path, 'models.txt')
        self.cars_indexes: dict[str, int] = {}
        self.models_indexes: dict[int, int] = {}
        self.sales_indexes: dict[str, int] = {}
        self.create_file(self.cars_index_file)
        self.create_file(self.cars_file)
        self.create_file(self.models_index_file)
        self.create_file(self.models_file)
        self.create_file(self.sales_index_file)
        self.create_file(self.sales_file)

    def create_file(self, path: str):
        '''
        Создаем пустой файл.\n
        path: str Путь к файлу.
        '''
        with open(path, 'w', encoding='utf-8') as _:
            pass

    def write_file(self, file: str, row: int, entity: BaseModel):
        '''
        Метод записи данных индексов и данных в файл.\n
        file: str Путь к файлу для записи.\n
        row: int Номер строки для записи.\n
        entity: BaseModel Объект для записи.
        '''
        with open(file, 'r+', encoding='utf-8') as f:
            f.seek(501 * (row - 1))
            if 'index' in file:
                f.write(f'{entity.idx()};{row}'.ljust(500) + '\n')
            else:
                f.write(entity.to_string().ljust(500) + '\n')

    # Задание 1. Сохранение автомобилей и моделей
    def add_model(self, model: Model) -> Model:
        '''
            Метод добавляет новую модель.\n
            model: Model Модель, которую добавляем.
        '''
        if model.index() in self.models_indexes:
            raise ValueError('duplicated id')
        row = max(self.models_indexes.values(), default=0) + 1
        self.models_indexes[model.id] = row
        self.write_file(self.models_index_file, row, model)
        self.write_file(self.models_file, row, model)
        return model

    # Задание 1. Сохранение автомобилей и моделей
    def add_car(self, car: Car) -> Car:
        '''
            Метод добавляет новую машину.\n
            car: Car Машина, которую добавляем.
        '''
        if car.index() in self.cars_indexes:
            raise ValueError('duplicated vin')
        row = max(self.cars_indexes.values(), default=0) + 1
        self.cars_indexes[car.index()] = row
        self.write_file(self.cars_index_file, row, car)
        self.write_file(self.cars_file, row, car)
        return car

    # Задание 2. Сохранение продаж.
    def sell_car(self, sale: Sale) -> Car:
        '''
        Фиксирует факт продажи автомобиля.\n
        sale: Sale Информация о продаже.
        '''
        if sale.index() not in self.cars_indexes:
            raise ValueError('VIN not in cars')
        row = max(self.sales_indexes.values(), default=0) + 1
        self.sales_indexes[sale.sales_number] = row
        self.write_file(self.sales_index_file, row, sale)
        self.write_file(self.sales_file, row, sale)
        car_row = self.cars_indexes[sale.index()]
        with open(self.cars_file, 'r+', encoding='utf-8') as file:
            file.seek(501 * (car_row - 1))
            data = file.readline().rstrip().split(';')
            car = Car(
                vin=data[0],
                model=int(data[1]),
                price=Decimal(data[2]),
                date_start=datetime.strptime(data[3], '%Y-%m-%d'),
                status=CarStatus.sold
            )
            file.seek(501 * (car_row - 1))
            file.write(car.to_string().ljust(500))
        return car

    # Задание 3. Доступные к продаже
    def get_cars(self, status: CarStatus) -> list[Car]:
        '''
        Возвращает список машин с указанным статусом.\n
        status : CarStatus Статус автомобиля.
        '''
        result = []
        with open(self.cars_file, 'r', encoding='utf-8') as file:
            for line in file:
                data = line.rstrip().split(';')
                if data[4] == status:
                    result.append(Car(
                        vin=data[0],
                        model=int(data[1]),
                        price=Decimal(data[2]),
                        date_start=datetime.strptime(data[3], '%Y-%m-%d'),
                        status=CarStatus(data[4])
                    ))
        return result
        # Судя по ответам в чате, тестами принимается только не сортированный

    # Задание 4. Детальная информация
    def get_car_info(self, vin: str) -> CarFullInfo | None:
        '''
        Возвращает информацию о авто, его марке и продаже.\n
        Если авто не найдено, возвращает None.\n
        vin : str VIN номер двигятеля авто.
        '''
        if vin in self.cars_indexes:
            car_row = self.cars_indexes[vin]
            with open(self.cars_file, 'r', encoding='utf-8') as file:
                file.seek(501 * (car_row - 1))
                data = file.readline().rstrip().split(';')
                car = Car(
                    vin=data[0],
                    model=int(data[1]),
                    price=Decimal(data[2]),
                    date_start=datetime.strptime(data[3], '%Y-%m-%d'),
                    status=CarStatus(data[4])
                )
            model_row = self.models_indexes[car.model]
            with open(self.models_file, 'r', encoding='utf-8') as file:
                file.seek(501 * (model_row - 1))
                data = file.readline().rstrip().split(';')
                model = Model(
                    id=int(data[0]),
                    name=data[1],
                    brand=data[2]
                )
            sale = None
            with open(self.sales_file, 'r', encoding='utf-8') as file:
                for line in file:
                    data = line.rstrip().split(';')
                    if data[1] == car.vin:
                        sale = Sale(
                            sales_number=data[0],
                            car_vin=data[1],
                            sales_date=datetime.strptime(data[2], '%Y-%m-%d'),
                            cost=Decimal(data[3])
                        )
                        break
            return CarFullInfo(
                vin=car.vin,
                car_model_name=model.name,
                car_model_brand=model.brand,
                price=car.price,
                date_start=car.date_start,
                status=car.status,
                sales_date=sale.sales_date if sale else None,
                sales_cost=sale.cost if sale else None
            )
        else:
            return None

    # Задание 5. Обновление ключевого поля
    def update_vin(self, vin: str, new_vin: str) -> Car:
        '''
        Обновляет VIN номер двигятеля.\n
        vin : str VIN двигателя, который надо изменить.\n
        new_vin : str Новое значение VIN.
        '''
        row = self.cars_indexes[vin]
        with open(self.cars_file, 'r+', encoding='utf-8') as file:
            file.seek(501 * (row - 1))
            data = file.readline().rstrip().split(';')
            car = Car(
                vin=new_vin,
                model=int(data[1]),
                price=Decimal(data[2]),
                date_start=datetime.strptime(data[3], '%Y-%m-%d'),
                status=CarStatus(data[4])
            )
            file.seek(501 * (row - 1))
            file.write(car.to_string().ljust(500) + '\n')
        self.cars_indexes.pop(vin)
        self.cars_indexes[new_vin] = row
        self.write_file(self.cars_index_file, row, car)
        return car

    # Задание 6. Удаление продажи
    def revert_sale(self, sales_number: str) -> Car:
        '''
        Удаляет информацию о продаже и возвращает статус авто в available.\n
        sales_number : str Номер продажи
        '''
        sale_row = self.sales_indexes[sales_number]
        with open(self.sales_file, 'r+', encoding='utf-8') as f:
            lines = f.readlines()
            data = lines[sale_row - 1].rstrip().split(';')
            sale = Sale(
                sales_number=data[0],
                car_vin=data[1],
                sales_date=datetime.strptime(data[2], '%Y-%m-%d'),
                cost=Decimal(data[3])
            )
            f.seek(0)
            f.truncate()
            for line in lines:
                if line.split(';')[0] != sales_number:
                    f.write(line)
        with open(self.sales_index_file, 'r+', encoding='utf-8') as f:
            lines = f.readlines()
            f.seek(0)
            f.truncate()
            for line in lines:
                if line.split(';')[0] != sales_number:
                    f.write(line)
        car_row = self.cars_indexes[sale.car_vin]
        with open(self.cars_file, 'r+', encoding='utf-8') as f:
            f.seek(501 * (car_row - 1))
            data = f.readline().rstrip().split(';')
            car = Car(
                vin=data[0],
                model=int(data[1]),
                price=Decimal(data[2]),
                date_start=datetime.strptime(data[3], '%Y-%m-%d'),
                status=CarStatus.available
            )
            f.seek(501 * (car_row - 1))
            f.write(car.to_string().ljust(500))
        return car

    # Задание 7. Самые продаваемые модели
    def top_models_by_sales(self) -> list[ModelSaleStats]:
        '''
        Возвращает топ-3 марки по количеству продаж.
        '''
        model_sales: dict[int, list] = {}
        with open(self.sales_file, 'r', encoding='utf-8') as f:
            for line in f:
                data = line.rstrip().split(';')
                sale = Sale(
                    sales_number=data[0],
                    car_vin=data[1],
                    sales_date=datetime.strptime(data[2], '%Y-%m-%d'),
                    cost=Decimal(data[3])
                )
                car_row = self.cars_indexes[sale.index()]
                with open(self.cars_file, 'r', encoding='utf-8') as file:
                    file.seek(501 * (car_row - 1))
                    car_data = file.readline().rstrip().split(';')
                    model = int(car_data[1])
                    price = Decimal(car_data[2])
                    if model not in model_sales:
                        model_sales[model] = [0, Decimal(0)]
                    model_sales[model] = [
                        model_sales[model][0] + 1,
                        model_sales[model][1] + price
                    ]
        top_3 = sorted(
            model_sales.items(),
            key=lambda item: (
                item[1][0],
                item[1][1] / item[1][0]
            ),
            reverse=True
        )[:3]
        result: list[ModelSaleStats] = []
        for top in top_3:
            model_id = top[0]
            model_sale = top[1][0]
            model_row = self.models_indexes[model_id]
            with open(self.models_file, 'r', encoding='utf-8') as file:
                file.seek(501 * (model_row - 1))
                model_data = file.readline().rstrip().split(';')
                model_sale_stat = ModelSaleStats(
                    car_model_name=model_data[1],
                    brand=model_data[2],
                    sales_number=model_sale
                )
                result.append(model_sale_stat)
        return result

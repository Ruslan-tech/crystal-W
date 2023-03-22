import os
from peewee import *

# создание БД
db = SqliteDatabase('crystal-db.db')


class BaseModel(Model):
    class Meta:
        database = db


class Clients(BaseModel):
    """Таблица Клиенты"""
    user_tg_id = IntegerField() 
    user_name = CharField(max_length=50)


class Services(BaseModel):
    """Таблица Услуги"""
    title = CharField(max_length=80)
    
    
class Cars(BaseModel):
    """Таблица Автомобили"""
    mark = CharField()
    model = CharField()
    color =  CharField(max_length=15)
    num = CharField(max_length=10)


class Client_Cars(BaseModel):
    """Таблица Автомобили клиентов"""
    user_id = ForeignKeyField(Clients)
    cars_id = ForeignKeyField(Cars)


class Subservice(BaseModel):
    """Таблица услуги мойки"""
    title = CharField()
    

class SubservicePolish(BaseModel):
    """Таблица услуги полировки"""
    title = CharField()


class SubserviceDryCleaner(BaseModel):
    """Таблица услуги химчистки"""
    title = CharField()


class SubserviceProtCover(BaseModel):
    """Таблица услуги защитных покрытий"""
    title = CharField()
    

class SubserviceTires(BaseModel):
    title = CharField()


class CarClass(BaseModel):
    """Таблица классы машин"""
    class_title = CharField()


class Price_wash(BaseModel):
    """Таблица цен услуг на мойку"""
    car_class_id = ForeignKeyField(CarClass)
    sub_serv_id = ForeignKeyField(Subservice)
    price = IntegerField()    
    comments = CharField(null=True)
    
    
class PricePolish(BaseModel):
    """Таблица цен услуг на полировку"""
    car_class_id = ForeignKeyField(CarClass)
    sub_serv_id = ForeignKeyField(SubservicePolish)
    price = IntegerField()    
    comments = CharField(null=True)
    
    
class PriceDryCleaner(BaseModel):
    """Таблица цен услуг на химчистку"""
    car_class_id = ForeignKeyField(CarClass)
    sub_serv_id = ForeignKeyField(SubserviceDryCleaner)
    price = IntegerField()    
    comments = CharField(null=True)


class PriceProtCover(BaseModel):
    """Таблица цен услуг на защитные покрытия"""
    car_class_id = ForeignKeyField(CarClass)
    sub_serv_id = ForeignKeyField(SubserviceProtCover)
    price = IntegerField()    
    comments = CharField(null=True)
    
    
class PriceLiquidGlass(BaseModel):
    price = IntegerField()
    service_id = ForeignKeyField(Services)


class ProductPromotions(BaseModel):
    """Таблица акций"""
    service_id = ForeignKeyField(Services)
    description = TextField()
    date_start = DateField()
    date_end = DateField()


# соединение с БД
db.connect()
# создание таблиц
db.create_tables([Clients, Services, Subservice, SubservicePolish, SubserviceDryCleaner, 
                  SubserviceProtCover, CarClass, Price_wash, PricePolish, PriceDryCleaner, PriceProtCover, PriceLiquidGlass, SubserviceTires])


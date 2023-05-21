from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String, JSON
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class CarSourceSite(Base):
    __tablename__ = "car_source_site"

    id = Column(Integer, primary_key=True, autoincrement=True)
    site = Column(String, unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.now())
    updated_at = Column(DateTime, default=datetime.now(), onupdate=datetime.now())


class CarBody(Base):
    __tablename__ = "car_body"

    id = Column(Integer, primary_key=True, autoincrement=True)
    kr_name = Column(String, unique=True, nullable=False)
    ru_name = Column(String)
    en_name = Column(String)
    created_at = Column(DateTime, default=datetime.now())
    updated_at = Column(DateTime, default=datetime.now(), onupdate=datetime.now())


class CarMark(Base):
    __tablename__ = "car_mark"

    id = Column(Integer, primary_key=True, autoincrement=True)
    kr_name = Column(String, unique=True, nullable=False)
    ru_name = Column(String)
    en_name = Column(String)
    created_at = Column(DateTime, default=datetime.now())
    updated_at = Column(DateTime, default=datetime.now(), onupdate=datetime.now())


class CarModel(Base):
    __tablename__ = "car_model"

    id = Column(Integer, primary_key=True, autoincrement=True)
    kr_name = Column(String, unique=True, nullable=False)
    ru_name = Column(String)
    en_name = Column(String)
    created_at = Column(DateTime, default=datetime.now())
    updated_at = Column(DateTime, default=datetime.now(), onupdate=datetime.now())


class CarTransmission(Base):
    __tablename__ = "car_transmission"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.now())
    updated_at = Column(DateTime, default=datetime.now(), onupdate=datetime.now())


class CarGearbox(Base):
    __tablename__ = "car_gearbox"

    id = Column(Integer, primary_key=True, autoincrement=True)
    kr_name = Column(String, unique=True, nullable=False)
    ru_name = Column(String)
    en_name = Column(String)
    created_at = Column(DateTime, default=datetime.now())
    updated_at = Column(DateTime, default=datetime.now(), onupdate=datetime.now())


class CarFuelType(Base):
    __tablename__ = "car_fuel_type"

    id = Column(Integer, primary_key=True, autoincrement=True)
    kr_name = Column(String, unique=True, nullable=False)
    ru_name = Column(String)
    en_name = Column(String)
    created_at = Column(DateTime, default=datetime.now())
    updated_at = Column(DateTime, default=datetime.now(), onupdate=datetime.now())


class Cars(Base):
    __tablename__ = "cars"

    id = Column(Integer, primary_key=True, autoincrement=True)
    source_site_id = Column(Integer, nullable=False)
    car_id = Column(Integer, nullable=False)
    body_id = Column(Integer, nullable=False)
    mark_id = Column(Integer, nullable=False)
    model_id = Column(Integer, nullable=False)
    grade_name = Column(String)
    year = Column(DateTime)
    price = Column(Integer)
    mileage = Column(Integer)
    gearbox_id = Column(Integer)
    transmission_id = Column(Integer)
    fuel_type_id = Column(Integer)
    engine_vol = Column(Integer)
    preview = Column(String)
    number = Column(String)
    vin = Column(String)
    color_id = Column(Integer)
    photos = Column(JSON)
    seller = Column(JSON)
    tech_inspection_url = Column(JSON)
    insurance_url = Column(JSON)
    created_at = Column(DateTime, default=datetime.now())
    updated_at = Column(DateTime, default=datetime.now(), onupdate=datetime.now())
    deleted_at = Column(DateTime)

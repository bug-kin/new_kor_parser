class Source:
    table = 'car_source_site'
    fields = ('id', 'site')


class CarBody:
    table = 'car_body'
    fields = ('id', 'kr_name')


class CarMark:
    table = 'car_mark'
    fields = ('id', 'kr_name')


class CarModel:
    table = 'car_model'
    fields = ('id', 'kr_name')


class Transmission:
    table = 'car_transmission'
    fileds = ('id', 'name')


class Gearbox:
    table = 'car_gearbox'
    fields = ('id', 'kr_name')


class FuelType:
    table = 'car_fuel_type'
    fields = ('id', 'kr_name')


class Connection:
    host = 'pepe.foundation'
    user = 'homestead'
    password = 'homestead'
    database = 'homestead'


class Schema:
    source = Source()
    car_body = CarBody()
    car_mark = CarMark()
    car_model = CarModel()
    transmission = Transmission()
    gearbox = Gearbox()
    fuel_type = FuelType()


class Data:
    connection = Connection()
    schema = Schema()


data = Data()

drop table if exists car_options;
drop table if exists cars;
drop table if exists car_option;
drop table if exists car_color;
drop table if exists car_fuel_type;
drop table if exists car_transmission;
drop table if exists car_gearbox;
drop table if exists car_model;
drop table if exists car_mark;
drop table if exists car_body;


create table if not exists car_source_site (
    id tinyint unsigned primary key auto_increment,
    site varchar(20) not null unique,
    created_at timestamp default now(),
    updated_at timestamp default now()
) COMMENT='Таблица, которая хранит наименование источника.';

INSERT INTO car_source_site (site) VALUES
('bobaedream'),
('encar'),
('kbchachacha');

create table if not exists car_body (
    id tinyint unsigned primary key auto_increment,
    kr_name varchar(20) unique not null,
    ru_name varchar(20),
    en_name varchar(20),
    created_at timestamp default now(),
    updated_at timestamp default now()
) COMMENT='Таблица, которая хранит наименование кузова автомобиля.';

create table if not exists car_mark (
    id smallint unsigned primary key auto_increment,
    kr_name varchar(50) unique not null,
    ru_name varchar(50),
    en_name varchar(50),
    created_at timestamp default now(),
    updated_at timestamp default now()
) COMMENT='Таблица, которая хранит наименование марки автомобиля.';

create table if not exists car_model (
    id smallint unsigned primary key auto_increment,
    kr_name varchar(50) unique not null,
    ru_name varchar(50),
    en_name varchar(50),
    created_at timestamp default now(),
    updated_at timestamp default now()
) COMMENT='Таблица, которая хранит наименование модели автомобиля.';

create table if not exists car_gearbox (
    id tinyint unsigned primary key auto_increment,
    kr_name varchar(20) unique not null,
    ru_name varchar(20),
    en_name varchar(20),
    created_at timestamp default now(),
    updated_at timestamp default now()
) COMMENT='Таблица, которая хранит наименование коробки передач.';

create table if not exists car_transmission (
    id tinyint unsigned primary key auto_increment,
    name varchar(20) unique not null,
    created_at timestamp default now(),
    updated_at timestamp default now()
) COMMENT='Таблица, которая хранит наименование привода автомобиля.';

create table if not exists car_fuel_type (
    id tinyint unsigned primary key auto_increment,
    kr_name varchar(30) unique not null,
    ru_name varchar(30),
    en_name varchar(30),
    created_at timestamp default now(),
    updated_at timestamp default now()
) COMMENT='Таблица, которая хранит наименование топлива.';

create table if not exists car_color (
    id tinyint unsigned primary key auto_increment,
    kr_name varchar(30) unique not null,
    ru_name varchar(30),
    en_name varchar(30),
    created_at timestamp default now(),
    updated_at timestamp default now()
) COMMENT='Таблица, которая хранит наименование цвета авто.';

create table if not exists car_option (
    id smallint unsigned primary key auto_increment,
    kr_name varchar(30) unique not null,
    ru_name varchar(30),
    en_name varchar(30),
    created_at timestamp default now(),
    updated_at timestamp default now()
) COMMENT='Таблица, которая хранит наименование опций для автомобиля.';

create table if not exists cars (
    id bigint unsigned PRIMARY KEY AUTO_INCREMENT,
    source_site_id tinyint unsigned NOT NULL,
    car_id bigint unsigned NOT NULL,
    body_id tinyint unsigned NOT NULL,
    mark_id smallint unsigned NOT NULL,
    model_id smallint unsigned NOT NULL,
    grade_name varchar(50),
    year year,
    price bigint unsigned,
    mileage mediumint unsigned,
    gearbox_id tinyint unsigned,
    transmission_id tinyint unsigned,
    fuel_type_id tinyint unsigned,
    engine_vol smallint unsigned,
    preview varchar(150),
    number varchar(20),
    vin varchar(17),
    color_id tinyint unsigned,
    photos json COMMENT 'Список путей к фотографиям. Пример: ["img_1.jpeg", "img_2.jpeg", ...]',
    seller json COMMENT 'Хранит данные по продавцу в виде JSON. Пример {"name": "Alex Yun", "phone": "0503159674", "address": "Almaty, Abay 150"}',
    tech_inspection_url json,
    insurance_url json,
    created_at timestamp NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp NULL DEFAULT CURRENT_TIMESTAMP,
    deleted_at date COMMENT 'Записывается дата обнаружения удаления машины.',
    foreign key (source_site_id) references car_source_site(id) on update cascade on delete cascade,
    foreign key (body_id) references car_body(id) on update cascade on delete cascade,
    foreign key (mark_id) references car_mark(id) on update cascade on delete cascade,
    foreign key (model_id) references car_model(id) on update cascade on delete cascade,
    foreign key (gearbox_id) references car_gearbox(id) on update cascade on delete cascade,
    foreign key (transmission_id) references car_transmission(id) on update cascade on delete cascade,
    foreign key (fuel_type_id) references car_fuel_type (id) on update cascade on delete cascade,
    foreign key (color_id) references car_color (id) on update cascade on delete cascade
) COMMENT='Таблица, которая данные автомобиля.';
create unique index uniq_car on car(source_site_id, car_id);

create table if not exists car_options (
    id bigint unsigned primary key auto_increment,
    car_id bigint unsigned not null,
    option_id smallint unsigned not null,
    created_at timestamp default now(),
    updated_at timestamp default now(),
    foreign key (car_id) references cars(id) on update cascade on delete cascade,
    foreign key (option_id) references car_option(id) on update cascade on delete cascade
) COMMENT='Таблица, которая хранит опции автомобиля.';
create unique index uniq_car_option on car_options (car_id, option_id);

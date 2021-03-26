import sqlalchemy
from .db_session import SqlAlchemyBase


class Type(SqlAlchemyBase):
    __tablename__ = 'types'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    title = sqlalchemy.Column(sqlalchemy.String(4), nullable=False, unique=True)
    weight = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    cf = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)


class Courier(SqlAlchemyBase):
    __tablename__ = 'couriers'

    courier_id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    courier_type = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('types.id'),
                                     nullable=False)
    regions = sqlalchemy.Column(sqlalchemy.ARRAY(sqlalchemy.Integer), nullable=False)
    working_hours = sqlalchemy.Column(sqlalchemy.ARRAY(sqlalchemy.String(11)), nullable=False)


class Order(SqlAlchemyBase):
    __tablename__ = 'orders'

    order_id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    weight = sqlalchemy.Column(sqlalchemy.Float, nullable=False)
    region = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    delivery_hours = sqlalchemy.Column(sqlalchemy.ARRAY(sqlalchemy.String(11)), nullable=False)

    status = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    assign_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('assigns.id'),
                                  nullable=True)
    owner_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('couriers.courier_id'),
                                 nullable=True)
    complete_time = sqlalchemy.Column(sqlalchemy.String, nullable=True)


class Assign(SqlAlchemyBase):
    __tablename__ = 'assigns'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    owner_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('couriers.courier_id'),
                                 nullable=False)
    type = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('types.id'),
                             nullable=False)
    datetime = sqlalchemy.Column(sqlalchemy.String(28), nullable=False)
    status = sqlalchemy.Column(sqlalchemy.Boolean, nullable=False)

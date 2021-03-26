import sqlalchemy as sa
import sqlalchemy.orm as orm
from sqlalchemy.orm import Session
import sqlalchemy.ext.declarative as dec


SqlAlchemyBase = dec.declarative_base()

__factory = None


def global_init():
    global __factory

    if __factory:
        return

    engine = sa.create_engine('postgresql://postgres:Kostya@localhost:5432/delivery', echo=False)
    __factory = orm.sessionmaker(bind=engine)

    from . import all_models

    SqlAlchemyBase.metadata.create_all(engine)


def create_session() -> Session:
    global __factory
    return __factory()

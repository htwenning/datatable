import pytest
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, INTEGER, String
Base = declarative_base()
metadata = Base.metadata
class Page:
    __tablename__ = 'page'
    page_id = Column(INTEGER)
    page_title = Column(String(255))


@pytest.yield_fixture()
def db():
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    engine = create_engine('sqlite://')
    Session = sessionmaker(bind=engine)
    Base.metadata.create_all(engine)
    session = Session()
    yield session
    session.close()
    

def test_datatable(db):
    from datatable import gen_datatable
    mock_request = {}
    res = gen_datatable(mock_request, Page)
    assert res == 'todo'

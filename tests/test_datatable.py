import pytest
import json
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, INTEGER, String
Base = declarative_base()
metadata = Base.metadata


class Page(Base):

    __tablename__ = 'page'

    page_id = Column(INTEGER)
    page_title = Column(String(255))
    created_by = Column(INTEGER)
    id = Column(INTEGER, primary_key=True)


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
    from datatable import gen_datatable, dt_put, dt_post, dt_delete

    page = Page(page_id=1, page_title='a', created_by=1)
    db.add(page)
    page = Page(page_id=2, page_title='b', created_by=1)
    db.add(page)
    page = Page(page_id=3, page_title='c', created_by=1)
    db.add(page)
    page = Page(page_id=4, page_title='d', created_by=1)
    db.add(page)
    db.commit()

    class Request:
        draw = 1
        start = 0
        length = 10
        search_value = ''

        def __init__(self):
            pass

        @property
        def args(self):
            return {
                'draw': [self.draw],
                'start': [self.start],
                'length': [self.length],
                'search[value]': self.search_value
            }

        @property
        def form(self):
            return {
                '0': 11,
                '1': 'test',
                '2': 3,
                '3': 6
            }

    class Request2:
        def __init__(self):
            pass

        @property
        def form(self):
            return {
                '0': 22,
                '1': 'test_zk',
                '2': 3,
                '3': 6
            }

    request = Request()

    res = gen_datatable(request, db, Page, filter_=lambda x: x.filter(Page.created_by == 1))
    assert json.loads(res.body) == {
        'data': [
            [1, 'a', 1, 1], [2, 'b', 1, 2], [3, 'c', 1, 3], [4, 'd', 1, 4]],
        'draw': 1,
        'recordsTotal': 4,
        'recordsFiltered': 4
    }

    res = gen_datatable(request, db, Page, filter_=lambda x: x.filter(Page.page_title == 'a'))
    assert json.loads(res.body) == {
        'data': [[1, 'a', 1, 1]],
        'draw': 1,
        'recordsTotal': 1,
        'recordsFiltered': 1
    }

    res = gen_datatable(request, db, Page)
    assert json.loads(res.body) == {
        'data': [
            [1, 'a', 1, 1], [2, 'b', 1, 2], [3, 'c', 1, 3], [4, 'd', 1, 4]],
        'draw': 1,
        'recordsTotal': 4,
        'recordsFiltered': 4
    }

    res = gen_datatable(request, db, Page, ret_columns=['page_title'])
    assert json.loads(res.body) == {
        'data': [
            ['a'], ['b'], ['c'], ['d']],
        'draw': 1,
        'recordsTotal': 4,
        'recordsFiltered': 4
    }

    res = gen_datatable(request, db, Page, order_by='page_id', desc=False)
    assert json.loads(res.body) == {
        'data': [
            [1, 'a', 1, 1], [2, 'b', 1, 2], [3, 'c', 1, 3], [4, 'd', 1, 4]],
        'draw': 1,
        'recordsTotal': 4,
        'recordsFiltered': 4
    }

    res = gen_datatable(request, db, Page, order_by='page_id', desc=True)
    assert json.loads(res.body) == {
        'data': [
            [4, 'd', 1, 4], [3, 'c', 1, 3], [2, 'b', 1, 2], [1, 'a', 1, 1]],
        'draw': 1,
        'recordsTotal': 4,
        'recordsFiltered': 4
    }

    request.search_value = 'a'
    res = gen_datatable(request, db, Page)
    assert json.loads(res.body) == {
        'data': [[1, 'a', 1, 1]],
        'draw': 1,
        'recordsTotal': 1,
        'recordsFiltered': 1
    }

    res = dt_post(request, db, Page)
    assert json.loads(res.body).get('code') == 0
    page = db.query(Page).filter(Page.id == 5).one()
    assert page.page_title == 'test'

    request2 = Request2()
    page = Page(page_id=22, page_title='hello', created_by=2)
    db.add(page)
    db.commit()
    page = db.query(Page).filter(Page.id == 6).one()
    assert page.page_title == 'hello'
    primary_key = 'id'
    key_index = 3
    res = dt_put(request2, db, Page, primary_key, key_index)
    assert json.loads(res.body).get('code') == 0
    page = db.query(Page).filter(Page.id == 6).one()
    assert page.page_title == 'test_zk'

    primary_key = 'id'
    key_index = 3
    res = dt_delete(request, db, Page, primary_key, key_index)
    assert json.loads(res.body).get('code') == 0
    page = db.query(Page).filter(Page.id == 6).first()
    assert page == None


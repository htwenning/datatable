from sanic import response
from sqlalchemy import or_, desc as _desc


def gen_datatable(request, db_session, Model, filter_=None, search_columns=None, ret_columns=None, order_by=None, desc=True):
    draw = int(request.args['draw'][0])
    start = int(request.args['start'][0])
    length = int(request.args['length'][0])
    search_value = request.args.get('search[value]')
    query = db_session.query(Model)
    columns = [column.name for column in Model.__table__.columns._all_columns]
    if filter_:
        query = filter_(query)
    records_total = query.count()
    if records_total == 0:
        return response.json({
            'data': [],
            'draw': draw,
            'recordsTotal': records_total,
            'recordsFiltered': records_total
        })
    if search_value:
        if search_columns:
            search_condition = [getattr(Model, attribute).like("%{}%".format(search_value)) for attribute in search_columns]
        else:
            search_condition = [getattr(Model, attribute).like("%{}%".format(search_value)) for attribute in columns]
        records_total = query.filter(or_(*search_condition)).count()
        query = query.filter(or_(*search_condition))
    if order_by:
        query = query.order_by(_desc(getattr(Model, order_by))) if desc else query.order_by(getattr(Model, order_by))
    records_filtered = records_total
    results = query.offset(start).limit(length).all()
    if ret_columns:
        ret = [[getattr(result, attribute) for attribute in ret_columns] for result in results]
    else:
        ret = [[getattr(result, attribute) for attribute in columns] for result in results]
    return response.json({
        'data': ret,
        'draw': draw,
        'recordsTotal': records_total,
        'recordsFiltered': records_filtered
    })


def dt_post(request, db_session, Model, columns=None):
    if not columns:
        columns = [column.name for column in Model.__table__.columns._all_columns]
    form_length = len(request.form)
    column_length = len(columns)
    if form_length != column_length:
        return response.json({
            'code': 1,
            'detail': 'error: columns range out of list'
        })
    model = Model()
    for i in range(form_length):
        setattr(model, columns.pop(0), request.form.get(str(i)))
    db_session.add(model)
    try:
        db_session.commit()
    except Exception as e:
        db_session.rollback()
        return response.json({
            'code': 1,
            'detail': 'error: {}'.format(e)
        })
    return response.json({
        'code': 0,
        'detail': 'success'
    })


def dt_put(request, db_session, Model, primary_key, key_index, columns=None, not_allow=[]):
    if not columns:
        columns = [column for column in Model.__table__.columns._all_columns]
    else:
        columns_dict = {column.name: column for column in Model.__table__.columns._all_columns if column.name in columns}
        columns = [columns_dict.get(column) for column in columns]
    try:
        if isinstance(primary_key, list) and isinstance(key_index, list) and len(primary_key) == len(key_index):
            d = zip(key_index, primary_key)
            filter_condition = []
            for index, attribute in d:
                filter_condition.append(getattr(Model, attribute) == request.form.get(str(index)))
            result = db_session.query(Model).filter(*filter_condition).one()
        else:
            result = db_session.query(Model).filter(getattr(Model, primary_key) == request.form.get(str(key_index))).one()
    except Exception as e:
        return response.json({
            'code': 1,
            'detail': 'error: {}'.format(e)
        })
    length = len(columns)
    for i in range(length):
        if request.form.get(str(i)) and i not in not_allow:
            try:
                setattr(result, columns[0].name, columns[0].type.python_type(request.form.get(str(i))))
                columns.pop(0)
            except Exception as e:
                db_session.rollback()
                return response.json({
                    'code': 1,
                    'detail': 'error: {}'.format(e)
                })
        else:
            columns.pop(0)
    try:
        db_session.commit()
    except Exception as e:
        db_session.rollback()
        return response.json({
            'code': 1,
            'detail': 'error: {}'.format(e)
        })
    return response.json({
        'code': 0,
        'detail': 'success'
    })


def dt_delete(request, db_session, Model, primary_key, key_index, status=None, attribute=None):
    query = db_session.query(Model)
    try:
        if isinstance(primary_key, list) and isinstance(key_index, list) and len(primary_key) == len(key_index):
            d = zip(key_index, primary_key)
            filter_condition = []
            for index, attribute in d:
                filter_condition.append(getattr(Model, attribute) == request.form.get(str(index)))
            result = query.filter(*filter_condition).one()
        else:
            result = query.filter(getattr(Model, primary_key) == request.form.get(str(key_index))).one()
    except Exception as e:
        return response.json({
            'code': 1,
            'detail': 'delete error: {}'.format(e)
        })
    if status and attribute:
        setattr(result, attribute, status)
    else:
        db_session.delete(result)
    try:
        db_session.commit()
    except Exception as e:
        db_session.rollback()
        return response.json({
            'code': 1,
            'detail': 'error: {}'.format(e)
        })
    return response.json({
        'code': 0,
        'detail': 'success'
    })

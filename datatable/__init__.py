from sanic import response
from sqlalchemy import or_, desc as _desc


def gen_datatable(request, db_session, Model, filter_=None, search_columns=None, ret_columns=None, order_by=None, desc=True):
    draw = int(request.args['draw'][0])
    start = int(request.args['start'][0])
    length = int(request.args['length'][0])
    search_value = request.args.get('search[value]')
    query = db_session.query(Model)
    columns = Model.__table__.columns._all_columns
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
            search_condition = [getattr(Model, attribute.name).like("%{}%".format(search_value)) for attribute in columns]
        records_total = query.filter(or_(*search_condition)).count()
        query = query.filter(or_(*search_condition))
    if order_by:
        query = query.order_by(_desc(getattr(Model, order_by))) if desc else query.order_by(getattr(Model, order_by))
    records_filtered = records_total
    results = query.offset(start).limit(length).all()
    if ret_columns:
        ret = [[getattr(result, attribute) for attribute in ret_columns] for result in results]
    else:
        ret = [[getattr(result, attribute.name) for attribute in columns] for result in results]
    return response.json({
        'data': ret,
        'draw': draw,
        'recordsTotal': records_total,
        'recordsFiltered': records_filtered
    })
datatable backend
===
[![Build Status](https://travis-ci.org/htwenning/datatable.svg?branch=master)](https://travis-ci.org/htwenning/datatable)

**requirements** :

- jquery databale.js
- sanic 
- sqlalchemy

**install** :

> pip install Sanic-Sqlalchemy-DataTable

**usage** :

```python
from sanic_sa_datatable import gen_datatable

@app.route('/page')
async def page(request):
    from models import Page
    return gen_datatable(request, Page)

```

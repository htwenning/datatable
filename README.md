datatable backend
===
[![Build Status](https://travis-ci.org/htwenning/datatable.svg?branch=master)](https://travis-ci.org/htwenning/datatable)

requirements:

- jquery databale.js
- sanic 
- sqlalchemy


usage:

```python
from datatable import gen_datatable

@app.route('/page')
async def page(request):
    from models import Page
    return gen_datatable(request, Page)

```

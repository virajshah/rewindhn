from flask import Flask, render_template, request, Response
import pymongo
import bson

from ddd import IN_DEVELOPMENT
from datetime import datetime
import os
import json

app = Flask(__name__)
DB = pymongo.Connection().hnmod.cleaned
DB.create_index('idx')
ACCEPTED_ARGS = set(('spec', 'fields', 'skip', 'limit', 'sort'))

with open(os.path.expanduser('~/pr/rewind/static/rewind/js/templates/page.ejs')) as f:
    page_tpl = f.read()
with open(os.path.expanduser('~/pr/rewind/static/rewind/js/templates/post.ejs')) as f:
    post_tpl = f.read()

class MongoEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        if isinstance(obj, bson.objectid.ObjectId):
            return str(obj)
        return json.JSONEncoder.default(self, obj)

def jsonify(*args, **kwargs):
    return Response(json.dumps(dict(*args, **kwargs), cls=MongoEncoder),
        mimetype='application/json')

@app.route('/api/v1/pages')
def api():
    print request.args
    args = dict((k, json.loads(v)) for k,v in request.args.items() if k in ACCEPTED_ARGS)
    args['limit'] = min(200, args.get('limit', 30))
    args.setdefault('fields', {'_id': False, 'html': False})
    data = list(DB.find(**args))
    return jsonify(results=data, count=len(data))

@app.route('/')
def home():
    last_page = next(DB.find({'page':0}, {'_id':False, 'html':False}).sort('created_at', -1).limit(1))
    max_page_idx = last_page['idx']
    return render_template('base.html',
        pages={ max_page_idx: last_page },
        post_tpl=post_tpl,
        page_tpl=page_tpl)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8010, debug=IN_DEVELOPMENT)

import requests
import datetime

from flask import Flask
from flask import request
from flask_restplus import Resource, Api
from flask_restplus import fields
from flask_restplus import inputs
from flask_restplus import reqparse
from pymongo import MongoClient


# get json data from url
def get_json_from_url(url_obj):
    content = requests.get(url_obj)
    data = content.json()
    return data


# check indicator is valid or not
def check_invalid_indicator(indicator_id):
    invalid_info = [{'message': [{'id': '120', 'key': 'Invalid value', 'value': 'The provided parameter value is not valid'}]}]
    test_url = 'http://api.worldbank.org/v2/countries/all/indicators/' + str(indicator_id) + '?date=2012:2017&format=json'
    # print(test_url)
    r = requests.get(test_url)
    if r.json() == invalid_info:
        return True
    else:
        return False


original_url = 'http://api.worldbank.org/v2'
# http://api.worldbank.org/v2/indicators?format=json&per_page=2000
# indicators_url = original_url + '/indicators?format=json&per_page=100'
mongo_url = 'mongodb://admin0:admin0@ds163842.mlab.com:63842/ass2'

parser = reqparse.RequestParser()
parser.add_argument('query', location=['json', 'args'])

app = Flask(__name__)
api = Api(app,
          default="Economic Indicators",
          title="World Bank Economic Indicators",
          description="This is a Data Service for World Bank Economic Indicators.")

# The following is th e schema of Economic Indicators
indicator_model = api.model('indicator', {
    'indicator_id': fields.String,
})


@api.route('/economic_indicators')
class Q13(Resource):
    # 1 - Import a collection from the data service
    @api.response(200, 'OK')
    @api.response(201, 'Created')
    @api.response(404, 'Not found')
    @api.doc(description='Import a collection from the data service')
    @api.expect(indicator_model, validate=True)
    def post(self):
        # get input indicator
        payload_content = request.json
        indicator = payload_content['indicator_id']

        # new a collection
        client = MongoClient(mongo_url)
        db = client.get_database()
        collection = db['economic_indicators']

        # if indicator is not in indicator list, return 404 Not found
        if check_invalid_indicator(indicator):
            message = "'" + indicator + "'" + ' is invalid.'
            return {'message': message}, 404

        if list(collection.find({'collection_id': indicator})):
            message = "'" + indicator + "'" + 'has been imported already.'
            return {'message': message}, 200

        # generate indicator url and get data from it
        indicator_url = original_url + '/countries/all/indicators/' + indicator + '?date=2012:2017&format=json&per_page=100'
        url_content = get_json_from_url(indicator_url)

        # convert url content to inserting data
        insert_data = dict()
        entries = list()
        for data in url_content[1]:
            converted_data = dict()
            converted_data['country'] = data['country']['value']
            converted_data['date'] = data['date']
            converted_data['value'] = data['value']
            entries.append(converted_data)
        insert_data['collection_id'] = url_content[1][0]['indicator']['id']
        insert_data['indicator'] = url_content[1][0]['indicator']['id']
        insert_data['indicator_value'] = url_content[1][0]['indicator']['value']
        ISOTIMEFORMAT = '%Y-%m-%d %H;%M;%S'
        insert_data['creation_time'] = datetime.datetime.now().strftime(ISOTIMEFORMAT)
        insert_data['entries'] = entries
        collection.insert_one(insert_data)
        # response message
        message = {"location": "economic_indicators/" + indicator,
                   "collection_id": indicator,
                   "creation_time": insert_data['creation_time'],
                   "indicator": indicator}
        return message, 201

    # 3 - Retrieve the list of available collections
    @api.response(200, 'OK')
    @api.doc(description='Retrieve the list of available collections')
    def get(self):
        client = MongoClient(mongo_url)
        db = client.get_database()
        collection = db['economic_indicators']
        content = list()
        for data in collection.find({}, {"_id": 0, 'collection_id': 1, 'creation_time': 1, 'indicator': 1}):
            temp = dict()
            temp['location'] = '/economic_indicators/' + data['collection_id']
            temp['collection_id'] = data['collection_id']
            temp['creation_time'] = data['creation_time']
            temp['indicator'] = data['indicator']
            content.append(temp)
        return content, 200


@api.route('/economic_indicators/<string:collection_id>')
@api.param('collection_id', 'ID of data')
class Q24(Resource):
    # 2 - Deleting a collection with the data service
    @api.response(200, 'OK')
    @api.response(404, 'Not found')
    @api.doc(description='Deleting a collection with the data service')
    def delete(self, collection_id):
        client = MongoClient(mongo_url)
        db = client.get_database()
        collection = db['economic_indicators']
        if not list(collection.find({'collection_id':collection_id})):
            message = "'" + collection_id + "'" + ' does not exist in database.'
            return {'message': message}, 404
        else:
            collection.delete_one({'collection_id': collection_id})
            message = "'" + collection_id + "'" + ' is removed from database.'
            return {'message': message}, 200

    # 4 - Retrieve a collection
    @api.response(200, 'OK')
    @api.response(404, 'Not found')
    @api.doc(description='Retrieve a collection')
    def get(self, collection_id):
        client = MongoClient(mongo_url)
        db = client.get_database()
        collection = db['economic_indicators']
        if not list(collection.find({'collection_id':collection_id})):
            message = "'" + collection_id + "'" + ' does not exist in database.'
            return {'message': message}, 404
        else:
            for data in collection.find({'collection_id': collection_id}):
                message = data
                del message['_id']
            return message, 200


@api.route('/economic_indicators/<string:collection_id>/<int:year>/<string:country>')
@api.param('collection_id', 'ID of data')
@api.param('year', 'Date of data')
@api.param('country', 'Country of data')
class Q5(Resource):
    # 5 - Retrieve economic indicator value for given country and a year
    @api.response(200, 'OK')
    @api.response(404, 'Not found')
    @api.doc(description=' Retrieve economic indicator value for given country and a year')
    def get(self, collection_id, year, country):
        client = MongoClient(mongo_url)
        db = client.get_database()
        collection = db['economic_indicators']
        value = 'null'
        check = False
        for doc in collection.find({'collection_id': collection_id}):
            entry = doc['entries']
            for data in entry:
                a = int(data['date'])
                if a == year and data['country'] == country:
                    value = data['value']
                    check = True
                    break
        if check:
            message = {'collection_id': collection_id, 'indicator': collection_id, 'country': country, 'year': year, 'value': value}
            return message, 200
        if not check:
            message = 'Cannot get the value.'
            return message, 404


@api.route('/economic_indicators/<string:collection_id>/<int:year>')
@api.param('collection_id', 'ID of data')
@api.param('year', 'Date of data')
@api.param('query', 'Searching method')
class Q6(Resource):
    # 6 - Retrieve top/bottom economic indicator values for a given year
    @api.response(200, 'OK')
    @api.response(404, 'Not found')
    @api.doc(description='Retrieve top/bottom economic indicator values for a given year')
    def get(self, collection_id, year):
        query = request.args.get('query')
        client = MongoClient(mongo_url)
        db = client.get_database()
        collection = db['economic_indicators']
        entry_set = []
        entry_none = []
        for doc in collection.find({'collection_id': collection_id}):
            for data in doc['entries']:
                a = int(data['date'])
                if a == year:
                    if data['value'] is None:
                        entry_none.append(data)
                    else:
                        entry_set.append(data)
        entry_set = sorted(entry_set, key=lambda x: x['value'], reverse=True)
        entry_none = sorted(entry_none, key=lambda x: x['country'])
        entry_set.extend(entry_none)

        if query[0:3] == 'top':
            message = dict()
            message['indicator'] = doc['indicator']
            message['indicator_value'] = doc['indicator_value']
            if len(entry_set) >= int(query[3:]):
                message['entries'] = entry_set[0:int(query[3:])]
            else:
                entry_set.insert(0, 'Cannot display ' + query[3:] +
                                 ' records, due to the max of query is ' + str(len(entry_set)))
                message['entries'] = entry_set[:]

        elif query[0:6] == 'bottom':
            message = dict()
            message['indicator'] = doc['indicator']
            message['indicator_value'] = doc['indicator_value']
            if len(entry_set) >= int(query[6:]):
                message['entries'] = entry_set[0 - int(query[6:])]
            else:
                entry_set.insert(0, 'Cannot display ' + query[6:] +
                                 ' records, due to the max of query is ' + str(len(entry_set)))
                message['entries'] = entry_set[:]

        else:
            message = 'Option can be only top<N> or bottom<N>.'
        return message, 200

        pass


if __name__ == '__main__':
    app.run(debug=True)


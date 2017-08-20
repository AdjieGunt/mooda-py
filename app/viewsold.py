from flask import Blueprint, request, jsonify, make_response
from app.users.models import Users, Clicks, Magrib_in_jkt, UsersSchema, ClicksSchema, MagribSchema, db
from flask_restful import Api, Resource

 
from sqlalchemy.exc import SQLAlchemyError
from marshmallow import ValidationError

import re, datetime
from datetime import date

users = Blueprint('users', __name__)
topten = Blueprint('topten', __name__)

# http://marshmallow.readthedocs.org/en/latest/quickstart.html#declaring-schemas
#https://github.com/marshmallow-code/marshmallow-jsonapi

click_schema = ClicksSchema()
magrib_schema = MagribSchema()
schema = UsersSchema()
api = Api(users)
top_tenapi = Api(topten)


# click trace
class ClicksList(Resource):
    """http://jsonapi.org/format/#fetching
    A server MUST respond to a successful request to fetch an individual resource or resource collection with a 200 OK response.
    A server MUST respond with 404 Not Found when processing a request to fetch a single resource that does not exist, except when the request warrants a 200 OK response with null as the primary data (as described above)
    a self link as part of the top-level links object"""

    def get(self):
        clicks_query = Clicks.query.all()
        results = click_schema.dump(clicks_query, many=True).data
        #return results

    """http://jsonapi.org/format/#crud
    A resource can be created by sending a POST request to a URL that represents a collection of resources. The request MUST include a single resource object as primary data. The resource object MUST contain at least a type member.
    If a POST request did not include a Client-Generated ID and the requested resource has been created successfully, the server MUST return a 201 Created status code"""

    def post(self):

        # print request
        raw_dict = request.get_json(force=True)
        #print raw_dict

        uid = raw_dict['data']['attributes']['user_id']

        # now time
        now = datetime.datetime.now()
        now_hour = now.hour
        now_minutes = now.minute
        now_sec = now.second
        now_date = '-'.join((str(now.year), str(now.month), str(now.day)))
        now_time = ':'.join((str(now.hour), str(now.minute), str(now.second)))

        total_sec_now_time = (datetime.timedelta(hours=now_hour, minutes=now_minutes, seconds=now_sec)).total_seconds()

        # ramadhan date
        ramadhan_date = date(2017, 05, 18)
        now_date_split = now_date.split('-')
        nowDate = date(int(now_date_split[0]), int(now_date_split[1]), int(now_date_split[2]))

        delta = nowDate - ramadhan_date
        serial_date = delta.days
        #serial_date = 1
        # print 'serial date : ' + str(serial_date)
        # magrib time
        magrib_query = Magrib_in_jkt.query.all()
        magrib_res = magrib_schema.dump(magrib_query, many=True).data
        #print magrib_res
        
        try:
            magrib_data = magrib_res['data'][serial_date]
        except Exception as e:
            print e
            pass


        #print magrib_data
        magrib_time = magrib_data['attributes']['time']

        #magrib_time = '17:38:00'
        # #print magrib_time
        h, m, s = re.split(':', magrib_time)
        total_sec_magrib_time = int(datetime.timedelta(hours=int(h), minutes=int(m), seconds=int(s)).total_seconds())
        gap_in_sec = total_sec_now_time - total_sec_magrib_time

        # print total_sec_magrib_time
        # print total_sec_now_time
        # print now_date
        # print now_time
        # print gap_in_sec
        # select data from db by uid
        user_has_click = Clicks.query.filter_by(user_id=str(uid), date=now_date).first()
        #print not user_has_click


        # validation
        time_validate = True
        err_msg = ""

        if total_sec_now_time <= total_sec_magrib_time: # before 'berbuka' click is disable
            time_validate = False
            err_msg = "Kamu baru dapat melakukan check in pada saat atau setelah waktu berbuka!"
        elif user_has_click: # and if user has click,
            time_validate = False
            err_msg = "Maaf, kamu sudah check in!"

        #print raw_dict

        if time_validate:
            raw_dict['data']['attributes']['date'] = now_date
            raw_dict['data']['attributes']['time'] = now_time
            raw_dict['data']['attributes']['serial_date'] = serial_date
            raw_dict['data']['attributes']['gap_in_sec'] = gap_in_sec
            try:
                click_schema.validate(raw_dict)
                click_dict = raw_dict['data']['attributes']
                click = Clicks(click_dict['user_id'], str(click_dict['date']),  click_dict['time'], click_dict['serial_date'], click_dict['gap_in_sec'])
                click.add(click)
                query = Clicks.query.get(click.id)
                #results = click_schema.dump(query).data
                resp = jsonify({'success' : True})
                resp.status_code =  201
                return resp

            except ValidationError as err:
                resp = jsonify({"error": err.messages})
                resp.status_code = 403
                return resp

            except SQLAlchemyError as e:
                db.session.rollback()
                resp = jsonify({"error": str(e)})
                resp.status_code = 403
                return resp
        else:
            e = err_msg
            resp = jsonify({"status" : False, "error": e})
            resp.status_code = 403
            return resp

class ClickById(Resource):
    def get(self, user_id):
        clicks_query = Clicks.query.filter_by(user_id=user_id).all()
        results = click_schema.dump(clicks_query, many=True).data
        return results

class Magrib_in_Jkt(Resource):
    def get(self):
        magrib_query = Magrib_in_jkt.query.all()
        clicks_query = Clicks.query.all()
        #results = MagribSchema.dump(magrib_query, many=True).data
        return magrib

class top(Resource):
    def get(self):

        #print results['data']
        user_ids = []
        avg_indicator = 7
        total = 10

        # now time
        now = datetime.datetime.now()
        now_hour = now.hour
        now_minutes = now.minute
        now_sec = now.second
        now_date = '-'.join((str(now.year), str(now.month), str(now.day)))
        now_time = ':'.join((str(now.hour), str(now.minute), str(now.second)))

        # ramadhan date
        ramadhan_date = date(2017, 05, 18)
        now_date_split = now_date.split('-')
        nowDate = date(int(now_date_split[0]), int(now_date_split[1]), int(now_date_split[2]))
        delta = nowDate - ramadhan_date
        serial_date = delta.days
        #serial_date = 1 # comment before deploy <--------
        one_week_ago = str(now - datetime.timedelta(7)).split(' ')[0]
        one_week_ago = now_date # comment before deploy <--------
        clicks_query = Clicks.query.filter(date>=one_week_ago)
        results = click_schema.dump(clicks_query, many=True).data
        if serial_date <= avg_indicator:
            avg_indicator = serial_date
        x = 0
        while x < len(results['data']):
            uid = int(results['data'][x]['attributes']['user_id'])
            if uid not in user_ids:
                user_ids.append(uid)
                #print uid
                #print user_ids
            x += 1

        x = 0
        top_ten = []
        while x < len(user_ids):
            y = 0
            counter = 0
            gap_in_sec = 0
            while y < len(results['data']):
                uid = int(results['data'][y]['attributes']['user_id'])

                if uid == user_ids[x]:
                    gap_in_sec += int(results['data'][x]['attributes']['gap_in_sec'])
                    counter += 1
                y +=1
            #if counter >= avg_indicator:
            top_ten.append((gap_in_sec / counter, str(user_ids[x]), counter))

            x += 1
        results = sorted(top_ten)

        temp_result = []
        if len(results) <= total or total > len(results):
            total = len(results)

        x = 0
        while x < total:
            temp_result.append({ "rank" : x + 1, "total_seconds" : results[x][0], "user_id" : results[x][1], "total_absen" : results[x][2] })
            x += 1
        result = temp_result

        return result


api.add_resource(ClicksList, '/clicks')
api.add_resource(ClickById, '/clicks/<string:user_id>')
top_tenapi.add_resource(top, '/top10')


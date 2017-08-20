from flask import Blueprint, request, jsonify, make_response
from app.users.models import Clicks, Clicks_staging, Magrib_in_jkt, Shopee_users, Shopee_users_schema,UsersSchema, ClicksSchema, MagribSchema, TopClicksSchema, CointsSchema, db
from flask_restful import Api, Resource

from sqlalchemy import func
from sqlalchemy.exc import SQLAlchemyError
from marshmallow import ValidationError

import re, datetime
from datetime import date

import random 

users = Blueprint('users', __name__)
topten = Blueprint('topten', __name__)

# http://marshmallow.readthedocs.org/en/latest/quickstart.html#declaring-schemas
#https://github.com/marshmallow-code/marshmallow-jsonapi

click_schema = ClicksSchema()
magrib_schema = MagribSchema()
userschema = Shopee_users_schema()
top_schema = TopClicksSchema()
coin_schema = CointsSchema()
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
        ramadhan_date = date(2017, 05, 26)
        now_date_split = now_date.split('-')
        nowDate = date(int(now_date_split[0]), int(now_date_split[1]), int(now_date_split[2]))

        delta = nowDate - ramadhan_date
        serial_date = delta.days
        #serial_date = 26
	print serial_date
        # serial_week
        serial_week = 1
        if serial_date >= 8:
            serial_week = 2
        if serial_date >= 15 :
            serial_week = 3
        if serial_date >= 22:
            serial_week = 4
        if serial_date >= 29:
            serial_week = 5
        #serial_date = 1

        print "serial week : " + str(serial_week)

            
            

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

        
        #magrib_time = '12:40:00'
        # #print magrib_time
        h, m, s = re.split(':', magrib_time)
        total_sec_magrib_time = int(datetime.timedelta(hours=int(h), minutes=int(m), seconds=int(s)).total_seconds())

        mgb_split = magrib_time.split(':')
        magrib_time = datetime.datetime(now.year, now.month, now.day, int(h), int(m))

        #print magrib_time
        #print now
        
        deltaaa = now - magrib_time


        print deltaaa.total_seconds()



        gap_in_sec = deltaaa.total_seconds()
        

        #Points
        total_pts = 600

        pts_res = total_pts - (gap_in_sec)

        if pts_res < 0:
            pts_res = 0


        # print "total seconds now : " + str(total_sec_now_time)
        # print "total seconds mgb : " + str(total_sec_magrib_time)
        # print "total gap in seconds : " + str(gap_in_sec)
        # print "total point(s) : " + str(pts_res)
        
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
            err_msg = "Check-in hanya bisa dilakukan saat waktu berbuka puasa (Maghrib)"
        elif user_has_click: # and if user has click,
            time_validate = False
            err_msg = "Maaf, kamu sudah check in!"
	elif serial_date <= 0: # and if user has click,
            time_validate = False
            err_msg = "Maaf, kamu belum bisa check in!"


        #print raw_dict

        if time_validate:
            raw_dict['data']['attributes']['date'] = now_date
            raw_dict['data']['attributes']['time'] = now_time
            raw_dict['data']['attributes']['serial_date'] = serial_date
            raw_dict['data']['attributes']['gap_in_sec'] = gap_in_sec * 1000
            raw_dict['data']['attributes']['points'] = pts_res
            raw_dict['data']['attributes']['serial_week'] = serial_week
            
            try:
                click_schema.validate(raw_dict)
                click_dict = raw_dict['data']['attributes']
                click = Clicks(click_dict['user_id'], str(click_dict['date']),  click_dict['time'], click_dict['serial_date'], click_dict['gap_in_sec'], click_dict['points'], click_dict['serial_week'])
                click.add(click)
                query = Clicks.query.get(click.id)
                #results = click_schema.dump(query).data
                resp = jsonify({'status' : 'true'})
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
            resp.status_code = 201
            return resp

class ClickById(Resource):
    def get(self, user_id):
        clicks_query = Clicks.query.filter_by(user_id=user_id).all()
        results = click_schema.dump(clicks_query, many=True).data
        return results



class Magrib_in_Jkt(Resource):
    def get(self, serial_date):
        magrib_query = Magrib_in_jkt.query.filter_by(serial_date=serial_date)
        print magrib_query
        results = magrib_schema.dump(magrib_query, many=True).data
        return results

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
        ramadhan_date = date(2017, 05, 26)
        now_date_split = now_date.split('-')
        nowDate = date(int(now_date_split[0]), int(now_date_split[1]), int(now_date_split[2]))
        delta = nowDate - ramadhan_date
        serial_date = delta.days
        #serial_date = 1 # comment before deploy <--------
        one_week_ago = str(now - datetime.timedelta(6)).split(' ')[0]
        #one_week_ago = now_date # comment before deploy <--------

          # serial_week
        serial_week = 1
        if serial_date >= 7:
            serial_week = 2
        if serial_date >= 13: #and serial_date <= 18:
            serial_week = 3
        if serial_date >= 19: #and serial_date <= 24:
            serial_week = 4
        if serial_date >= 25:
            serial_week = 5
        
        clicks_query = Clicks.query.filter(Clicks.serial_week==serial_week).filter(Clicks.points>0).order_by(Clicks.gap_in_sec.asc()).limit(1000)
	#clicks_query = Clicks.query.filter_by(serial_week=serial_week).order_by(Clicks.gap_in_sec.asc()).limit(100)

        #clicks_query = Clicks.query.filter_by(serial_week=serial_week).order_by(Clicks.points.desc())
        results = click_schema.dump(clicks_query, many=True).data
        #print results
        result2 = results

        


        if serial_date <= avg_indicator:
            avg_indicator = serial_date

        x = 0
        while x < len(results['data']):
            uid = results['data'][x]['attributes']['user_id']
            #print str(x) + " - " + str(uid)
            if uid not in user_ids:
                user_ids.append(uid)
                #print uid
                #print user_ids
            x += 1

        x = 0
        top_ten = []
        #week = 1
        #total_day_in_week = [2, 7, 7, 7, 7]

        print len(user_ids)
        print len(results['data'])
        while x < len(user_ids):
            y = 0
            counter = 0
            gap_in_sec = 0
            points = 0  
            #print str(points) + " AADAS "          
            while y < len(results['data']):
                uid = results['data'][y]['attributes']['user_id']
                sweek = results['data'][y]['attributes']['serial_week']
                
                #print str(uid) + "<>" + str(user_ids[x])

                if uid == user_ids[x]:
                    gap_in_sec += int(results['data'][y]['attributes']['gap_in_sec'])
                    points += int(results['data'][y]['attributes']['points'])
                    # get username by userid
                    username_query = Shopee_users.query.filter_by(user_id=uid)
                    username_res = userschema.dump(username_query, many=True).data
                    #print username_res
                    try:
                        username = username_res['data'][0]['attributes']['username']
                    except IndexError:
                        username = uid
                    #print "ttasd"
                    #print username
                    #print points
                    
                    counter += 1
                y +=1
            #if counter >= avg_indicator:
            top_ten.append((gap_in_sec / counter, str(user_ids[x]), counter, points, username))

            x += 1
        results = top_ten

        temp_result = []
        if len(results) <= total or total > len(results):
            total = len(results)

        x = 0
        while x < total:
            temp_result.append({ "rank" : x + 1, "total_seconds" : results[x][0], "user_id" : results[x][1], "username" : results[x][4], "total_absen" : results[x][2], "points" : results[x][3] })
            x += 1
        result = temp_result

        return result

class top_ten_by_week(Resource):
    def get(self, week):

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
        one_week_ago = str(now - datetime.timedelta(6)).split(' ')[0]
        #one_week_ago = now_date # comment before deploy <--------

        # serial_week
        serial_week = week
        # if serial_date >= 7 and serial_date < 13:
        #     serial_week = 2
        # if serial_date >= 13 and serial_date < 19:
        #     serial_week = 3
        # if serial_date >= 19 and serial_date < 25:
        #     serial_week = 4
        # if serial_date >= 25:
        #     serial_week = 5
        
        clicks_query = Clicks.query.filter_by(serial_week=serial_week).order_by(Clicks.points.desc())
        #clicks_query = Clicks.query.filter_by(serial_week=serial_week).order_by(Clicks.points.desc())
        results = click_schema.dump(clicks_query, many=True).data
        print results
        result2 = results

        


        if serial_date <= avg_indicator:
            avg_indicator = serial_date

        x = 0
        while x < len(results['data']):
            uid = results['data'][x]['attributes']['user_id']
            print str(x) + " - " + str(uid)
            if uid not in user_ids:
                user_ids.append(uid)
                #print uid
                #print user_ids
            x += 1

        x = 0
        top_ten = []
        #week = 1
        #total_day_in_week = [2, 7, 7, 7, 7]

        print len(user_ids)
        print len(results['data'])
        while x < len(user_ids):
            y = 0
            counter = 0
            gap_in_sec = 0
            points = 0  
            print str(points) + " AADAS "          
            while y < len(results['data']):
                uid = results['data'][y]['attributes']['user_id']
                sweek = results['data'][y]['attributes']['serial_week']
                
                print str(uid) + "<>" + str(user_ids[x])

                if uid == user_ids[x]:
                    gap_in_sec += int(results['data'][y]['attributes']['gap_in_sec'])
                    points += int(results['data'][y]['attributes']['points'])
                    # get username by userid
                    username_query = Shopee_users.query.filter_by(user_id=uid)
                    username_res = userschema.dump(username_query, many=True).data
                    print username_res
                    try:
                        username = username_res['data'][0]['attributes']['username']
                    except IndexError:
                        username = uid
                    print "ttasd"
                    print username
                    print points
                    
                    counter += 1
                y +=1
            #if counter >= avg_indicator:
            top_ten.append((gap_in_sec / counter, str(user_ids[x]), counter, points, username))

            x += 1
        results = top_ten

        temp_result = []
        if len(results) <= total or total > len(results):
            total = len(results)

        x = 0
        while x < total:
            temp_result.append({ "rank" : x + 1, "total_seconds" : results[x][0], "user_id" : results[x][1], "username" : results[x][4], "total_absen" : results[x][2], "points" : results[x][3] })
            x += 1
        result = temp_result

        return result

class top2(Resource):
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
        one_week_ago = str(now - datetime.timedelta(6)).split(' ')[0]
        #one_week_ago = now_date # comment before deploy <--------

        # serial_week
        serial_week = 1
        if serial_date >= 7 and serial_date <= 12:
            serial_week = 2
        if serial_date >= 13 and serial_date <= 18:
            serial_week = 3
        if serial_date >= 19 and serial_date <= 24:
            serial_week = 4
        if serial_date >= 25:
            serial_week = 5
        
        clicks_query = Clicks.query.filter(date>=one_week_ago).order_by(Clicks.points.desc())
        #clicks_query = Clicks.query.filter_by(serial_week=serial_week).order_by(Clicks.points.desc())
        results = click_schema.dump(clicks_query, many=True).data
        print results
        result2 = results

        


        if serial_date <= avg_indicator:
            avg_indicator = serial_date

        x = 0
        while x < len(results['data']):
            uid = results['data'][x]['attributes']['user_id']
            print str(x) + " - " + str(uid)
            if uid not in user_ids:
                user_ids.append(uid)
                #print uid
                #print user_ids
            x += 1

        x = 0
        top_ten = []
        #week = 1
        #total_day_in_week = [2, 7, 7, 7, 7]

        print len(user_ids)
        print len(results['data'])

        while x < len(user_ids):
            y = 0
            counter = 0
            gap_in_sec = 0
            points = 0  
            #print str(points) + " INITIAL POINTS"
            #print "Search .. " + str(x) + ' ' + user_ids[x]          
            while y < len(results['data']):
                uid = results['data'][y]['attributes']['user_id']
                sweek = results['data'][y]['attributes']['serial_week']
                # print str(uid) + "<>" + str(user_ids[x])
                points = 0
                #print ' y ' + str(y)
                #print 'poin : ' + str(points)
                if uid == user_ids[x]:
                    gap_in_sec += int(results['data'][y]['attributes']['gap_in_sec'])
                    points = int(results['data'][y]['attributes']['points'])
                    print user_ids[x]
                    print points
                    # get username by userid
                    # username_query = Shopee_users.query.filter_by(user_id=uid)
                    # username_res = userschema.dump(username_query, many=True).data
                    # try:
                    #     username = username_res['data'][0]['attributes']['username']
                    # except IndexError:
                    #     username = uid
                    # print "ttasd"
                    # print username
                    # print points
                    counter += 1
                y +=1
            #if counter >= avg_indicator:
            #top_ten.append((gap_in_sec / counter, str(user_ids[x]), counter, points, username))

            x += 1
        results = top_ten

        temp_result = []
        if len(results) <= total or total > len(results):
            total = len(results)

        x = 0
        while x < total:
            temp_result.append({ "rank" : x + 1, "total_seconds" : results[x][0], "user_id" : results[x][1], "username" : results[x][4], "total_absen" : results[x][2], "points" : results[x][3] })
            x += 1
        result = temp_result

        return result



class topv2(Resource):
    def get(self):
        # now time
        now = datetime.datetime.now()
        now_hour = now.hour
        now_minutes = now.minute
        now_sec = now.second
        now_date = '-'.join((str(now.year), str(now.month), str(now.day)))
        now_time = ':'.join((str(now.hour), str(now.minute), str(now.second)))

        # ramadhan date
        ramadhan_date = date(2017, 05, 26)
        now_date_split = now_date.split('-')
        nowDate = date(int(now_date_split[0]), int(now_date_split[1]), int(now_date_split[2]))
        delta = nowDate - ramadhan_date
        serial_date = delta.days
        #serial_date = 1 # comment before deploy <--------
        one_week_ago = str(now - datetime.timedelta(6)).split(' ')[0]
        #one_week_ago = now_date # comment before deploy <--------

        # serial_week
        serial_week = 1
        if serial_date >= 8:
            serial_week = 2
        if serial_date >= 15 :
            serial_week = 3
        if serial_date >= 22:
            serial_week = 4
        if serial_date >= 29:
            serial_week = 5
        #serial_date = 1
        
	print serial_week
        top_ten_query = db.session.query(func.count(Clicks.user_id).label('total_absen'),\
        Clicks.user_id,func.sum(Clicks.gap_in_sec).label('gap_in_sec'),func.sum(Clicks.points).label('points')).\
        filter_by(serial_week=serial_week).group_by(Clicks.user_id).order_by(func.sum(Clicks.points).desc()).order_by(func.count(Clicks.user_id).desc()).order_by(func.sum(Clicks.gap_in_sec).asc()).limit(100)


        res = top_schema.dump(top_ten_query, many=True).data

        top_ten = []
        x = 0
        print len(res['data'])

        while x < len(res['data']):
            uid = res['data'][x]['attributes']['user_id']
            username_query = Shopee_users.query.filter_by(user_id=uid)
            username_res = userschema.dump(username_query, many=True).data
            #print username_res
            try:
                username = username_res['data'][0]['attributes']['username']
            except IndexError:
                username = uid
            #print username

            total_absen = res['data'][x]['attributes']['total_absen']
            points = res['data'][x]['attributes']['points']
            total_seconds = res['data'][x]['attributes']['gap_in_sec']
            
            
            
            top_ten.append({'rank':x + 1, 'total_absen' : total_absen, 'total_seconds':total_seconds, 'points':points, 'user_id':uid, 'username':username})
            x += 1

        return top_ten

class topv2_week(Resource):
    def get(self, week):
        # now time
        now = datetime.datetime.now()
        now_hour = now.hour
        now_minutes = now.minute
        now_sec = now.second
        now_date = '-'.join((str(now.year), str(now.month), str(now.day)))
        now_time = ':'.join((str(now.hour), str(now.minute), str(now.second)))

        # ramadhan date
        ramadhan_date = date(2017, 05, 26)
        now_date_split = now_date.split('-')
        nowDate = date(int(now_date_split[0]), int(now_date_split[1]), int(now_date_split[2]))
        delta = nowDate - ramadhan_date
        serial_date = delta.days
        #serial_date = 1 # comment before deploy <--------
        one_week_ago = str(now - datetime.timedelta(6)).split(' ')[0]
        #one_week_ago = now_date # comment before deploy <--------

        # serial_week
        serial_week = week

        #print serial_week
        top_ten_query = db.session.query(func.count(Clicks.user_id).label('total_absen'),\
        Clicks.user_id,func.sum(Clicks.gap_in_sec).label('gap_in_sec'),func.sum(Clicks.points).label('points')).\
        filter_by(serial_week=serial_week).group_by(Clicks.user_id).order_by(func.sum(Clicks.points).desc()).order_by(func.count(Clicks.user_id).desc()).order_by(func.sum(Clicks.gap_in_sec).asc()).limit(100)

        res = top_schema.dump(top_ten_query, many=True).data

        top_ten = []
        x = 0
        #print len(res['data'])

        while x < len(res['data']):
            uid = res['data'][x]['attributes']['user_id']
            username_query = Shopee_users.query.filter_by(user_id=uid)
            username_res = userschema.dump(username_query, many=True).data
            #print username_res
            try:
                username = username_res['data'][0]['attributes']['username']
            except IndexError:
                username = uid
            #print username

            total_absen = res['data'][x]['attributes']['total_absen']
            points = res['data'][x]['attributes']['points']
            total_seconds = res['data'][x]['attributes']['gap_in_sec']
            
            
            
            top_ten.append({'rank':x + 1, 'total_absen' : total_absen, 'total_seconds':total_seconds, 'points':points, 'user_id':uid, 'username':username})
            x += 1

        return top_ten

class get_coins_by_userid(Resource):
    def get(self, user_id):
        # now time
        now = datetime.datetime.now()
        now_hour = now.hour
        now_minutes = now.minute
        now_sec = now.second
        now_date = '-'.join((str(now.year), str(now.month), str(now.day)))
        now_time = ':'.join((str(now.hour), str(now.minute), str(now.second)))

        # ramadhan date
        ramadhan_date = date(2017, 05, 26)
        now_date_split = now_date.split('-')
        nowDate = date(int(now_date_split[0]), int(now_date_split[1]), int(now_date_split[2]))
        delta = nowDate - ramadhan_date
        serial_date = delta.days
        #serial_date = 1 # comment before deploy <--------
        one_week_ago = str(now - datetime.timedelta(6)).split(' ')[0]
        #one_week_ago = now_date # comment before deploy <--------

        # serial_week
        serial_week = 1
        if serial_date >= 7 :
            serial_week = 2
        if serial_date >= 13 and serial_date < 19:
            serial_week = 3
        if serial_date >= 19 and serial_date < 25:
            serial_week = 4
        if serial_date >= 25:
            serial_week = 5

        # Query    
        # SELECT count(user_id) as count_user_id, user_id, count(points) as total_coins WHERE serial_week=serial_week GROUP BY user_id;
        get_query = db.session.query(func.count(Clicks.user_id).label('total_absen'),\
        func.sum(Clicks.points).label('points'), Clicks.user_id).filter(Clicks.serial_week==serial_week, Clicks.user_id==user_id).group_by(Clicks.user_id)

        res = coin_schema.dump(get_query, many=True).data
        results = []
        x = 0
        while x < len(res['data']):
            uid = res['data'][x]['attributes']['user_id']
            username_query = Shopee_users.query.filter_by(user_id=uid)
            username_res = userschema.dump(username_query, many=True).data
            #print username_res
            try:
                username = username_res['data'][0]['attributes']['username']
            except IndexError:
                username = uid
            #print username

            total_absen = res['data'][x]['attributes']['total_absen']
            points = res['data'][x]['attributes']['points']
            
            
            
            results.append({'total_absen' : total_absen, 'coins':points, 'user_id':uid, 'username':username})
            x += 1

        return results

class ClicksList2(Resource):
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
        ramadhan_date = date(2017, 05, 26)
        now_date_split = now_date.split('-')
        nowDate = date(int(now_date_split[0]), int(now_date_split[1]), int(now_date_split[2]))

        delta = nowDate - ramadhan_date
        serial_date = delta.days
        #serial_date = 26

        # serial_week
        serial_week = 1
        if serial_date > 7:
            serial_week = 2
        if serial_date > 14:
            serial_week = 3
        if serial_date > 21:
            serial_week = 4
        if serial_date > 28:
            serial_week = 5
        
        # Now Time (total_seconds)
        now_sec             = total_sec_now_time
        

        # Sahur = 02:00 - 05:00
        sahur_time_start    = (datetime.timedelta(hours=2, minutes=0, seconds=0)).total_seconds()
        sahur_time_end      = (datetime.timedelta(hours=5, minutes=0, seconds=0)).total_seconds()
        
        # Berbuka = 16:00 - 19:00
        magrib_time_start    = (datetime.timedelta(hours=16, minutes=0, seconds=0)).total_seconds()
        magrib_time_end      = (datetime.timedelta(hours=19, minutes=0, seconds=0)).total_seconds()
        
        #Points a.k Coins
        total_pts = 10

        # select data from db by uid
        user_has_click = Clicks.query.filter_by(user_id=str(uid), date=now_date).first()
        print now_sec
        print magrib_time_start
        # validation
        time_validate = False
	sahur = 'false'
        err_msg = "Check-in hanya bisa dilakukan saat waktu sahur atau waktu berbuka puasa"

        if now_sec > sahur_time_start and now_sec < sahur_time_end: # before 'sahur' click is disable
            time_validate = True
	    sahur = 'true'
        if now_sec > magrib_time_start and now_sec < magrib_time_end: # before 'berbuka' click is disable
            time_validate = True
        if user_has_click: # and if user has click,
            time_validate = False
            err_msg = "Kamu sudah check-in hari ini"

        #print raw_dict

        if time_validate:
            raw_dict['data']['attributes']['date'] = now_date
            raw_dict['data']['attributes']['time'] = now_time
            raw_dict['data']['attributes']['serial_date'] = serial_date
            raw_dict['data']['attributes']['gap_in_sec'] = 0
            raw_dict['data']['attributes']['points'] = total_pts
            raw_dict['data']['attributes']['serial_week'] = serial_week
            
            try:
                click_schema.validate(raw_dict)
                click_dict = raw_dict['data']['attributes']
                click = Clicks(click_dict['user_id'], str(click_dict['date']),  click_dict['time'], click_dict['serial_date'], click_dict['gap_in_sec'], click_dict['points'], click_dict['serial_week'])
                click.add(click)
                query = Clicks.query.get(click.id)
                #results = click_schema.dump(query).data
                resp = jsonify({'status' : 'true', 'sahur':sahur})
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
            resp.status_code = 201
            return resp



class get_coins_by_userid(Resource):
    def get(self, user_id):
        # now time
        now = datetime.datetime.now()
        now_hour = now.hour
        now_minutes = now.minute
        now_sec = now.second
        now_date = '-'.join((str(now.year), str(now.month), str(now.day)))
        now_time = ':'.join((str(now.hour), str(now.minute), str(now.second)))

        # ramadhan date
        ramadhan_date = date(2017, 05, 26)
        now_date_split = now_date.split('-')
        nowDate = date(int(now_date_split[0]), int(now_date_split[1]), int(now_date_split[2]))
        delta = nowDate - ramadhan_date
        serial_date = delta.days
        #serial_date = 1 # comment before deploy <--------
        one_week_ago = str(now - datetime.timedelta(6)).split(' ')[0]
        #one_week_ago = now_date # comment before deploy <--------

        # serial_week
        serial_week = 1
        if serial_date >= 8:
            serial_week = 2
        if serial_date >= 15 :
            serial_week = 3
        if serial_date >= 22:
            serial_week = 4
        if serial_date >= 29:
            serial_week = 5

	#Clicks = Clicks_staging
        # Query    
        # SELECT count(user_id) as count_user_id, user_id, count(points) as total_coins WHERE serial_week=serial_week GROUP BY user_id;
        get_query = db.session.query(func.count(Clicks.user_id).label('total_absen'),\
        func.sum(Clicks.points).label('points'), Clicks.user_id).filter(Clicks.serial_week==serial_week, Clicks.user_id==user_id).group_by(Clicks.user_id)

        res = coin_schema.dump(get_query, many=True).data
        results = []
        x = 0
        while x < len(res['data']):
            uid = res['data'][x]['attributes']['user_id']
            username_query = Shopee_users.query.filter_by(user_id=uid)
            username_res = userschema.dump(username_query, many=True).data
            #print username_res
            try:
                username = username_res['data'][0]['attributes']['username']
            except IndexError:
                username = uid
            #print username

            total_absen = res['data'][x]['attributes']['total_absen']
            points = res['data'][x]['attributes']['points']
            
            
            
            results.append({'total_absen' : total_absen, 'coins':points, 'user_id':uid, 'username':username})
            x += 1

        return results
class ClicksList2_staging(Resource):
    """http://jsonapi.org/format/#fetching
    A server MUST respond to a successful request to fetch an individual resource or resource collection with a 200 OK response.
    A server MUST respond with 404 Not Found when processing a request to fetch a single resource that does not exist, except when the request warrants a 200 OK response with null as the primary data (as described above)
    a self link as part of the top-level links object"""

    def get(self):
        clicks_query = Clicks_staging.query.all()
        results = click_schema.dump(clicks_query, many=True).data
        #return results

    """http://jsonapi.org/format/#crud
    A resource can be created by sending a POST request to a URL that represents a collection of resources. The request MUST include a single resource object as primary data. The resource object MUST contain at least a type member.
    If a POST request did not include a Client-Generated ID and the requested resource has been created successfully, the server MUST return a 201 Created status code"""

    def post(self):
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
        ramadhan_date = date(2017, 05, 26)
        now_date_split = now_date.split('-')
        nowDate = date(int(now_date_split[0]), int(now_date_split[1]), int(now_date_split[2]))

        delta = nowDate - ramadhan_date
        serial_date = delta.days
        #serial_date = 26

        # serial_week
        serial_week = 1
        if serial_date > 7:
            serial_week = 2
        if serial_date > 14:
            serial_week = 3
        if serial_date > 21:
            serial_week = 4
        if serial_date > 28:
            serial_week = 5
        
        # Now Time (total_seconds)
        now_sec             = total_sec_now_time
        

        # Sahur = 02:00 - 05:00
        sahur_time_start    = (datetime.timedelta(hours=2, minutes=0, seconds=0)).total_seconds()
        sahur_time_end      = (datetime.timedelta(hours=5, minutes=0, seconds=0)).total_seconds()
        
        # Berbuka = 16:00 - 19:00
        magrib_time_start    = (datetime.timedelta(hours=16, minutes=0, seconds=0)).total_seconds()
        magrib_time_end      = (datetime.timedelta(hours=19, minutes=0, seconds=0)).total_seconds()
        
        #Points a.k Coins
        total_pts = 10

        # select data from db by uid
        user_has_click = Clicks_staging.query.filter_by(user_id=str(uid), date=now_date).first()
        print now_sec
        print magrib_time_start
        # validation
        time_validate = False
        sahur = 'false'
        err_msg = "Check-in hanya bisa dilakukan saat waktu sahur atau waktu berbuka puasa"

        if now_sec > sahur_time_start and now_sec < sahur_time_end: # before 'sahur' click is disable
            time_validate = True
	    sahur = 'true'
        if now_sec > magrib_time_start and now_sec < magrib_time_end: # before 'berbuka' click is disable
            time_validate = True
        if user_has_click: # and if user has click,
            time_validate = False
            err_msg = "Kamu sudah check-in hari ini"

        #print raw_dict

        if time_validate:
            raw_dict['data']['attributes']['date'] = now_date
            raw_dict['data']['attributes']['time'] = now_time
            raw_dict['data']['attributes']['serial_date'] = serial_date
            raw_dict['data']['attributes']['gap_in_sec'] = 0
            raw_dict['data']['attributes']['points'] = total_pts
            raw_dict['data']['attributes']['serial_week'] = serial_week
            
            try:
                click_schema.validate(raw_dict)
                click_dict = raw_dict['data']['attributes']
                click = Clicks_staging(click_dict['user_id'], str(click_dict['date']),  click_dict['time'], click_dict['serial_date'], click_dict['gap_in_sec'], click_dict['points'], click_dict['serial_week'])
                click.add(click)
                query = Clicks_staging.query.get(click.id)
                #results = click_schema.dump(query).data
                resp = jsonify({'status' : 'true', 'sahur':sahur})
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
            resp.status_code = 201
            return resp

class ClickById2(Resource):
    def get(self, user_id):
        clicks_query = Clicks_staging.query.filter_by(user_id=user_id).all()
        results = click_schema.dump(clicks_query, many=True).data
        return results

class cek_time_sahur_n_mgb(Resource):
    def get(self):
	# now time
        now = datetime.datetime.now()
        now_hour = now.hour
        now_minutes = now.minute
        now_sec = now.second
        now_date = '-'.join((str(now.year), str(now.month), str(now.day)))
        now_time = ':'.join((str(now.hour), str(now.minute), str(now.second)))

        total_sec_now_time = (datetime.timedelta(hours=now_hour, minutes=now_minutes, seconds=now_sec)).total_seconds()

        open = 'false'
        
        # Now Time (total_seconds)
        now_sec             = total_sec_now_time
        
        # Sahur = 02:00 - 05:00
        sahur_time_start    = (datetime.timedelta(hours=2, minutes=0, seconds=0)).total_seconds()
        sahur_time_end      = (datetime.timedelta(hours=5, minutes=0, seconds=0)).total_seconds()
        
        # Berbuka = 16:00 - 19:00
        magrib_time_start    = (datetime.timedelta(hours=13, minutes=0, seconds=0)).total_seconds()
        magrib_time_end      = (datetime.timedelta(hours=19, minutes=0, seconds=0)).total_seconds()

        if now_sec > sahur_time_start and now_sec < sahur_time_end: # before 'sahur' click is disable
	        open = 'true'
        if now_sec > magrib_time_start and now_sec < magrib_time_end: # before 'berbuka' click is disable
            open = 'true'

        resp = jsonify({'status' : open})
        return resp

class ClicksList3_staging(Resource):
    """http://jsonapi.org/format/#fetching
    A server MUST respond to a successful request to fetch an individual resource or resource collection with a 200 OK response.
    A server MUST respond with 404 Not Found when processing a request to fetch a single resource that does not exist, except when the request warrants a 200 OK response with null as the primary data (as described above)
    a self link as part of the top-level links object"""

    def get(self):
        clicks_query = Clicks_staging.query.all()
        results = click_schema.dump(clicks_query, many=True).data
        #return results

    """http://jsonapi.org/format/#crud
    A resource can be created by sending a POST request to a URL that represents a collection of resources. The request MUST include a single resource object as primary data. The resource object MUST contain at least a type member.
    If a POST request did not include a Client-Generated ID and the requested resource has been created successfully, the server MUST return a 201 Created status code"""

    def post(self):
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
        ramadhan_date = date(2017, 05, 26)
        now_date_split = now_date.split('-')
        nowDate = date(int(now_date_split[0]), int(now_date_split[1]), int(now_date_split[2]))

        delta = nowDate - ramadhan_date
        serial_date = delta.days
        #serial_date = 26

        # serial_week
        serial_week = 1
        if serial_date > 7:
            serial_week = 2
        if serial_date > 14:
            serial_week = 3
        if serial_date > 21:
            serial_week = 4
        if serial_date > 28:
            serial_week = 5
        
        # Now Time (total_seconds)
        now_sec             = total_sec_now_time
        

        # Sahur = 02:00 - 05:00
        sahur_time_start    = (datetime.timedelta(hours=2, minutes=0, seconds=0)).total_seconds()
        sahur_time_end      = (datetime.timedelta(hours=5, minutes=0, seconds=0)).total_seconds()
        
        # Berbuka = 16:00 - 19:00
        magrib_time_start    = (datetime.timedelta(hours=10, minutes=0, seconds=0)).total_seconds()
        magrib_time_end      = (datetime.timedelta(hours=21, minutes=0, seconds=0)).total_seconds()
        
        #Points a.k Coins
        total_pts = 0

        # Base Coins
        day_1 = [25, 25, 25]
        day_2 = [25, 50, 100]
        day_3 = [50, 100, 200]
        day_4 = [100, 200, 400]
        day_5 = [250, 500, 1000]
        day_6 = [500, 1000, 2000]
        day_7 = [2000, 5000, 10000]

        base_coin = {
            1 : day_1,
            2 : day_2,
            3 : day_3,
            4 : day_4,
            5 : day_5,
            6 : day_6,
            7 : day_7
        }

        #count_absen = 1
        count_absen_query = Clicks_staging.query.filter_by(user_id=str(uid), serial_week=serial_week)
        res = coin_schema.dump(count_absen_query, many=True).data
        #print res
        count_absen = len(res['data'])
        #print len(res['data'])
        seq = base_coin[count_absen + 1]
        total_pts = random.choice(seq)
        
        

        # select data from db by uid
        user_has_click = Clicks_staging.query.filter_by(user_id=str(uid), date=now_date).first()
        print now_sec
        print magrib_time_start
        # validation
        time_validate = False
        sahur = 'false'
        err_msg = "Check-in hanya bisa dilakukan saat waktu sahur atau waktu berbuka puasa"

        if now_sec > sahur_time_start and now_sec < sahur_time_end: # before 'sahur' click is disable
            time_validate = True
	    sahur = 'true'
        if now_sec > magrib_time_start and now_sec < magrib_time_end: # before 'berbuka' click is disable
            time_validate = True
        if user_has_click: # and if user has click,
            time_validate = False
            err_msg = "Kamu sudah check-in hari ini"

        #print raw_dict

        if time_validate:
            raw_dict['data']['attributes']['date'] = now_date
            raw_dict['data']['attributes']['time'] = now_time
            raw_dict['data']['attributes']['serial_date'] = serial_date
            raw_dict['data']['attributes']['gap_in_sec'] = 0
            raw_dict['data']['attributes']['points'] = total_pts
            raw_dict['data']['attributes']['serial_week'] = serial_week
            
            try:
                click_schema.validate(raw_dict)
                click_dict = raw_dict['data']['attributes']
                click = Clicks_staging(click_dict['user_id'], str(click_dict['date']),  click_dict['time'], click_dict['serial_date'], click_dict['gap_in_sec'], click_dict['points'], click_dict['serial_week'])
                click.add(click)
                query = Clicks_staging.query.get(click.id)
                #results = click_schema.dump(query).data
                resp = jsonify({'status' : 'true', 'sahur':sahur, 'points':total_pts})
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
            resp.status_code = 201
            return resp

class get_coins_by_userid2(Resource):
    def get(self, user_id):
        # now time
        now = datetime.datetime.now()
        now_hour = now.hour
        now_minutes = now.minute
        now_sec = now.second
        now_date = '-'.join((str(now.year), str(now.month), str(now.day)))
        now_time = ':'.join((str(now.hour), str(now.minute), str(now.second)))

        # ramadhan date
        ramadhan_date = date(2017, 05, 26)
        now_date_split = now_date.split('-')
        nowDate = date(int(now_date_split[0]), int(now_date_split[1]), int(now_date_split[2]))
        delta = nowDate - ramadhan_date
        serial_date = delta.days
        #serial_date = 1 # comment before deploy <--------
        one_week_ago = str(now - datetime.timedelta(6)).split(' ')[0]
        #one_week_ago = now_date # comment before deploy <--------

        # serial_week
        serial_week = 1
        if serial_date >= 8:
            serial_week = 2
        if serial_date >= 15 :
            serial_week = 3
        if serial_date >= 22:
            serial_week = 4
        if serial_date >= 29:
            serial_week = 5

        # Query    
        # SELECT count(user_id) as count_user_id, user_id, count(points) as total_coins WHERE serial_week=serial_week GROUP BY user_id;
        get_query = db.session.query(func.count(Clicks_staging.user_id).label('total_absen'),\
        func.sum(Clicks_staging.points).label('points'), Clicks_staging.user_id).filter(Clicks_staging.serial_week==serial_week, Clicks_staging.user_id==user_id).group_by(Clicks_staging.user_id)

        res = coin_schema.dump(get_query, many=True).data
        results = []
        x = 0
        while x < len(res['data']):
            uid = res['data'][x]['attributes']['user_id']
            username_query = Shopee_users.query.filter_by(user_id=uid)
            username_res = userschema.dump(username_query, many=True).data
            #print username_res
            try:
                username = username_res['data'][0]['attributes']['username']
            except IndexError:
                username = uid
            #print username

            total_absen = res['data'][x]['attributes']['total_absen']
            points = res['data'][x]['attributes']['points']
            
            
            
            results.append({'total_absen' : total_absen, 'coins':points, 'user_id':uid, 'username':username})
            x += 1

        return results

api.add_resource(ClicksList, '/clicks') #Just Post
api.add_resource(ClickById, '/clicks/<string:user_id>')
api.add_resource(ClickById2, '/clicks2/<string:user_id>')
top_tenapi.add_resource(Magrib_in_Jkt,'/magrib/<int:serial_date>')
#top_tenapi.add_resource(top, '/top10')
#top_tenapi.add_resource(top_ten_by_week, '/top10/week/<int:week>')

api.add_resource(ClicksList2, '/clicks2') #Just Post
api.add_resource(ClicksList3_staging, '/clicks3_staging') #Just Post

top_tenapi.add_resource(top2, '/top102')
top_tenapi.add_resource(topv2, '/top10')
top_tenapi.add_resource(topv2_week, '/top10/week/<int:week>')

top_tenapi.add_resource(get_coins_by_userid2, '/coins2/<user_id>')
top_tenapi.add_resource(get_coins_by_userid, '/coins/<user_id>')
top_tenapi.add_resource(cek_time_sahur_n_mgb, '/cek')



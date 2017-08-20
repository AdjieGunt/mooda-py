
class chaces_by_userid(Resource):
    def get(self, user_id):

        #initial
        
        user_id = user_id
        total_chances = 0
        tcu_result = 0
        chance_used = 0
        result = 0

         # date_time (Now)
        now = datetime.datetime.now()
        now_hour = now.hour
        now_minutes = now.minute
        now_sec = now.second
        now_date = '-'.join((str(now.year), str(now.month), str(now.day)))
        now_time = ':'.join((str(now.hour), str(now.minute), str(now.second)))

        started_date = date(2017, 07, 05)
        now_date_split = now_date.split('-')
        nowDate = date(int(now_date_split[0]), int(now_date_split[1]), int(now_date_split[2]))
        delta = nowDate - started_date
        serial_date = delta.days
        #serial_date = 1 # comment before deploy <--------
        one_week_ago = str(now - datetime.timedelta(6)).split(' ')[0]
        #one_week_ago = now_date # comment before deploy <--------

        print serial_date

        # serial_week
        serial_week = 1
        if serial_date >= 6:
            serial_week = 2
        if serial_date >= 12 :
            serial_week = 3
        if serial_date >= 19:
            serial_week = 4

        # total_chances = Select chance from chances where user_id;
        #tc_query = Chances.query.filter_by(user_id=user_id)
        tc_query = db.session.query(Chances.user_id, func.sum(Chances.chance).label('chance')).group_by(Chances.user_id).filter_by(user_id=user_id)        
        tc_result = chance_schema.dump(tc_query, many=True).data
        print tc_result
        

        # total_chaces_used = Select user_id, count(*) as chance_used, SUM(result) as result from usage Group BY user_id
        tcu_query = db.session.query(Usage.user_id,\
        func.count(Usage.user_id).label('chance_used'),\
        func.sum(Usage.result).label('result'))\
        .group_by(Usage.user_id).filter_by(user_id=user_id)

        # total 'kesempatan' minggu ini:
        chances_this_week = db.session.query(Usage.user_id,\
        func.count(Usage.user_id).label('chance_used'),\
        func.sum(Usage.result).label('result'))\
        .group_by(Usage.user_id).filter(Usage.user_id==user_id, Usage.serial_week==serial_week)

        res_ctw = total_chance_schema().dump(chances_this_week, many=True).data

        print res_ctw
        
        #tcu_query = Usage.query.filter_by(user_id=user_id)
        #print tcu_query
        tcu_result = total_chance_schema().dump(tcu_query, many=True).data

        #real result
        try:
            total_chances = tc_result['data'][0]['attributes']['chance']
        except:
            total_chances = 0
        
        try:
            chance_used = tcu_result['data'][0]['attributes']['chance_used']
            result = tcu_result['data'][0]['attributes']['result']
        except:
            chance_used = 0
            result = 0

        try:
            chances_this_week = res_ctw['data'][0]['attributes']['result']
        except:
            chances_this_week = 0

        current_chances = int(total_chances) - int(chance_used)
        print tcu_result
        print user_id
        print total_chances
        print chance_used


        result = jsonify({'user_id':user_id, 'chances_used' : chance_used, 'total_chances':total_chances, 'current_chances':current_chances, 'result':chances_this_week})

        return result

class chances(Resource):
    def post(self):
        # post data
        raw_dict = request.get_json(force=True)

        # user_id
        user_id = raw_dict['data']['attributes']['user_id']
        # result
        result = raw_dict['data']['attributes']['result']
        # date_time (Now)
        now = datetime.datetime.now()
        now_hour = now.hour
        now_minutes = now.minute
        now_sec = now.second
        now_date = '-'.join((str(now.year), str(now.month), str(now.day)))
        now_time = ':'.join((str(now.hour), str(now.minute), str(now.second)))

        started_date = date(2017, 07, 05)
        now_date_split = now_date.split('-')
        nowDate = date(int(now_date_split[0]), int(now_date_split[1]), int(now_date_split[2]))
        delta = nowDate - started_date
        serial_date = delta.days
        #serial_date = 1 # comment before deploy <--------
        one_week_ago = str(now - datetime.timedelta(6)).split(' ')[0]
        #one_week_ago = now_date # comment before deploy <--------

        

        # serial_week
        serial_week = 1
        if serial_date >= 6:
            serial_week = 2
        if serial_date >= 12 :
            serial_week = 3
        if serial_date >= 19:
            serial_week = 4
        # print serial_date, serial_week
        total_chances = 0
         # total_chances = Select chance from chances where user_id;
        #tc_query = Chances.query.filter_by(user_id=user_id)
        tc_query = db.session.query(Chances.user_id, func.sum(Chances.chance).label('chance')).group_by(Chances.user_id).filter_by(user_id=str(user_id))        
        tc_result = chance_schema.dump(tc_query, many=True).data
        # print tc_result

        try:
            total_chances = tc_result['data'][0]['attributes']['chance']
        except:
            total_chances = 0

        

        # total 'kesempatan' minggu ini:
        chances_this_week = db.session.query(Usage.user_id,\
        func.count(Usage.user_id).label('chance_used'),\
        func.sum(Usage.result).label('result'))\
        .group_by(Usage.user_id).filter_by(user_id=str(user_id)).filter_by(serial_week=serial_week)

        res_ctw = total_chance_schema().dump(chances_this_week, many=True).data
        # print res_ctw

        try:
            chances_this_week = res_ctw['data'][0]['attributes']['chance_used']
        except:
            chances_this_week = 0

        # total seluruh  kesempatan
        chances_total = db.session.query(Usage.user_id,\
        func.count(Usage.user_id).label('chance_used'),\
        func.sum(Usage.result).label('result'))\
        .group_by(Usage.user_id).filter_by(user_id=str(user_id))

        res_ctotal_used = total_chance_schema().dump(chances_total, many=True).data
        # print res_ctotal_used

        try:
            chances_used_total = res_ctotal_used['data'][0]['attributes']['chance_used']
        except:
            chances_used_total = 0

        

        raw_dict['data']['attributes']['date_used'] = now_date
        raw_dict['data']['attributes']['time_used'] = now_time        
        raw_dict['data']['attributes']['user_id'] = user_id
        raw_dict['data']['attributes']['serial_week'] = serial_week       
        raw_dict['data']['attributes']['result'] = result
        # print raw_dict
        # print chances_this_week, total_chances
        try:
            if int(total_chances) > int(chances_used_total):
                usage_schema.validate(raw_dict)
                usage_dict = raw_dict['data']['attributes']
                usage = Usage(usage_dict['user_id'], usage_dict['date_used'], str(usage_dict['time_used']), usage_dict['serial_week'], usage_dict['result'])
                usage.add(usage)
                status = 'true'
            else:
                status = 'false'
            resp = jsonify({'status' : status})
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
class check_user(Resource):
    def get(self):
	string = request.headers.get('User-Agent')
	status = False
	user_agent = request.user_agent.platform
	if 'Shopee' in string:
		status = True
	elif 'shopee' in string:
		status = True
	resp = jsonify({'from_shopee_app' : status, 'user_agent' : string, 'user_agent_data':user_agent})
        return resp

class check_last_update(Resource):
    def get(self):
        last_update_query = db.session.query(func.max(Chances.time_added).label('date'))
        print last_update_query
        result = last_update_schema().dump(last_update_query, many=True).data
        res_date = result['data'][0]['attributes']['date']
        print res_date
        res_date = dateutil.parser.parse(res_date)
        res_date = res_date.strftime("%Y-%m-%d %H:%M:%S")
        result = jsonify({'last_updated': res_date})
        return result


api.add_resource(chances, '/bid')
api.add_resource(chaces_by_userid, '/bid/<user_id>')
api.add_resource(check_user, '/cek_user')
api.add_resource(check_last_update, '/cek_last_update')
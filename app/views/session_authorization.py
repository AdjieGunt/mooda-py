import jwt
from functools import wraps
from flask import request
from config import SECRET_KEY
from app.models.m_users import tbl_users

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        #set value null token
        token = None

        if 'token-moodaid-acc' in request.headers:           #jika token di header = token-moodaid-access maka jalankan
            token = request.headers['token-moodaid-acc']
    
        if not token:                                           #jika token tidak ada
            resp = {'msg':'Token is missing', 'status':'Error 401'}, 401
            return resp

        try:
            data = jwt.decode(token, SECRET_KEY)                                    #decode token dan secret_key
            # print data
            current_user = tbl_users.query.filter_by(id = data['userid']).first()   #filter isi data toke yg sesuai dg data token yg sudah di encode sebelumnya
        except:
            resp = {'msg':'Token is invalid !', 'status':'Error 401'}, 401
            return resp
        
        return f(current_user, *args, **kwargs)
    return decorated
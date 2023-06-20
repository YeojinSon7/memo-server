from flask_restful import Resource
from flask import request
import mysql.connector
from mysql.connector import Error
from mysql_connection import get_connection
from utils import check_password, hash_password
from email_validator import validate_email,EmailNotValidError 
from flask_jwt_extended import create_access_token, get_jwt, jwt_required
import datetime

# 로그아웃된 토큰을 저장할 set을 만든다.
jwt_blocklist = set()

class UserLogoutResource(Resource):
    @jwt_required() # 중요한 키워드!!
    def delete(self):
        
        jti = get_jwt()['jti'] # 헤더로 보낸 인증토큰 가져와서
        print(jti)
        jwt_blocklist.add(jti)   # blocklist에 넣어라

    
        return {'result':'success'}


class UserLoginResource(Resource):
    def post(self):
        # 1. 클라이언트로부터 데이터를 받아온다.
        data = request.get_json()
        # 2. 이메일 주소로, DB에 select 한다.
        try:
            connection = get_connection()
            query = '''select *
                    from user
                    where email = %s;'''
            record = (data['email'],)
            cursor = connection.cursor(dictionary=True)
            cursor.execute(query,record)

            result_list = cursor.fetchall()
            
            cursor.close()
            connection.close()

        except Error as e:
            print(e)
            return{'result':'fail','error':str(e)},500

        if len(result_list) == 0 :
                return {'result':'fail','error':'회원가입한 사람 아님'},400
        # 3. 비밀번호가 일치하는지 확인한다.
        # 암호화된 비밀번호가 일치하는지 확인해야함.
        print(result_list)
        check = check_password(data['password'],result_list[0]['password'])
        if check == False :
            return {'result':'fail','error':'비번 틀렸음'},400
        # 4. 클라이언트에게 데이터를 보내준다.
        access_token = create_access_token(result_list[0]['id'])
        return {'result':'success','access_token':access_token}


class UserRegisterResource(Resource) :
    def post(self):
#     {
#     "email" : "ccc@naver.com",
#     "password" : "1234", 
#     "nickname" : "toto"
#     }   
        # 1. 클라이언트로부터 데이터를 받는다.
        data = request.get_json()

        #2. 이메일 주소형식이 올바른지 확인한다.
        try:
            validate_email(data['email'])
        # 에러가 안나면 무사통과 아니면 에러 발생
        except EmailNotValidError as e:
            print(e) # 디버깅 할 때 필요하다
            return {'result':'fail','error':str(e)},400
        
        #3. 비밀번호 길이가 유용한지 체크한다.
        # 만약, 비번이 4자리 이상, 12자리 이하라고 한다면,
        if len(data['password'])< 4 or len(data['password']) > 12:
            return{'result':'fail','error':'비번 길이 에러'},400
        
        # 4. 비밀번호를 암호화 한다.
        hashed_password = hash_password(data['password'])
        print(hashed_password)

        #5. DB에 이미 회원 정보가 있는지 확인한다.
        try:
            connection = get_connection()
            query = '''select * from user
                    where email = %s;'''
            record = (data['email'],)
            cursor = connection.cursor(dictionary=True)
            cursor.execute(query,record)

            result_list = cursor.fetchall()

            print(result_list)

            if len(result_list) == 1:
                return {'result':'fail','error':'이미 회원가입 한 사람'},400
            # 회원이 아니므로 회원가입 코드 작성
            # DB에 저장
            query = '''insert into user
                    (email,password,nickname)
                    values
                    (%s,%s,%s);'''
            record = (data['email'],hashed_password,data['nickname'])
            cursor = connection.cursor()
            cursor.execute(query,record)

            connection.commit()

            ### DB에 데이터를 insert 함 후에, 그 인서트된 행의 아이디 가져오는 코드!
            user_id = cursor.lastrowid

            cursor.close()
            connection.close()

        except Error as e:
            print(e)
            return {'result':'fail','error': str(e)}, 500
        access_token = create_access_token(user_id)
        return {'result' :'success','access_token': access_token}
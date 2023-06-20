from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_restful import Resource
from flask import request
import mysql.connector
from mysql.connector import Error

from mysql_connection import get_connection

class FollowMemoListResource(Resource):
    @jwt_required()
    def get(self):
        # 1. 클라이언트로부터 데이터 받아오기
        # print(request.args.get('offset'))
        # get() 딕셔너리 값 가져오는 함수다 / 없는 값을 쓰면 None나온다
        # print(request.args['offset'])
        # args는 딕셔너리이다 / 없는 값을 쓰면 에러난다 그래서 서버에서는 get()함수 사용한다
        # query params는, 딕셔너리로 받아오고, 없는 키값을 엑세스해도 에러 발생하지 않도록 get()함수 사용한다

        offset = request.args.get('offset')
        limit = request.args.get('limit')
        user_id = get_jwt_identity()

        try:
            connection = get_connection()
            query = '''select m.*, u.nickname
                    from follow f
                    join memo m
                        on f.followeeId = m.userId
                    join user u
                        on m.userId = u.id
                    where followerId = %s
                    order by date desc
                    limit '''+offset+''','''+limit+''';''' # 문자열로 취급해서 + 쓴다
            record =(user_id,)
            cursor = connection.cursor(dictionary=True)
            cursor.execute(query,record)
            #connection.commit() # 저장할 때 쓰는거라 가져오는거에는 안쓴다!

            result_list = cursor.fetchall()

            cursor.close()
            connection.close()

        except Error as e:
            print(e)
            return {'result':'fail','error':str(e)},500
        i = 0
        for row in result_list :
        # row는 딕셔너리 형태
            result_list[i]['createdAt']=row['createdAt'].isoformat() # 문자열로 만드는 것
            result_list[i]['updatedAt']=row['updatedAt'].isoformat()
            result_list[i]['date']=row['date'].isoformat()
            i = i + 1
        # 센스있는 코드
        return {'result':'success',
                'count':len(result_list),
                'items':result_list}
        

# 조회, 생성
class MemoResource(Resource):
    @jwt_required()
    def get(self):
        user_id = get_jwt_identity()

        try:
            connection = get_connection()
            query = '''select *
                    from memo
                    where userId = %s
                    order by date desc;'''
            record =(user_id,)
            cursor = connection.cursor(dictionary=True)
            cursor.execute(query,record)
            #connection.commit() # 저장할 때 쓰는거라 가져오는거에는 안쓴다!

            result_list = cursor.fetchall()
            cursor.close()
            connection.close()

        except Error as e:
            print(e)
            return {'result':'fail','error':str(e)},500
        i = 0
        for row in result_list :
        # row는 딕셔너리 형태
            result_list[i]['createdAt']=row['createdAt'].isoformat() # 문자열로 만드는 것
            result_list[i]['updatedAt']=row['updatedAt'].isoformat()
            result_list[i]['date']=row['date'].isoformat()
            i = i + 1
        # 센스있는 코드
        return {'result':'success',
                'count':len(result_list),
                'items':result_list}
    
    @jwt_required()
    def post(self):
        # 포스트로 요청한 것을 처리하는 코드 작성을 우리가!
        # 1. 클라이언트가 보낸 데이터를 받아온다.
        data = request.get_json()
        # 1-1. 헤더에 담긴 JWT 토큰 받아온다.
        user_id = get_jwt_identity() # 헤더토큰에서 user_id 뽑아준다
        print(data)
        # 2. DB에 저장한다.
        try:
            # 2-1. 데이터베이스를 연결한다.
            connection = get_connection()

            # 2-2. 쿼리문 만든다
            ###### 중요! 컬럼과 매칭되는 데이터만 %s로 바꿔준다.
            query = '''insert into memo
                    (userId,title,date,content)
                    values
                    (%s,%s,%s,%s);'''
            #2-3. 쿼리에 매칭되는 변수 처리! 중요! 튜플로 처리해준다!(튜프은 데이터변경이 안되니까?)
            # 위의 %s부분을 만들어주는거다
            record = (user_id,data['title'],data['date'], data['content'])
            #2-4 커서를 가져온다
            cursor = connection.cursor()
            #2-5 쿼리문을,커서로 실행한다.
            cursor.execute(query,record)
            #2-6 DB 반영 완료하라는, commit 해줘야한다.
            connection.commit()
            #2-7. 자원해제
            cursor.close()
            connection.close()

        except Error as e :
            print(e)
            return {'result':'fail','error': str(e)}, 500
            # 상태코드 에러에 맞게 내가 설계한다
        return{'result': 'success'} 

# 수정, 삭제    
class MemoListResource(Resource):
    @jwt_required()
    def put(self,memo_id):
        #body에 있는 json 데이터를 받아온다.
        data = request.get_json()
        # 1. 클라이언트로부터 데이터 받아온다
        print(memo_id)
        user_id = get_jwt_identity()
        #2. 데이터베이스에 update한다.
        try :
            connection = get_connection()
            query = '''update memo
                    set title = %s , date = %s, content = %s
                    where id = %s and userId = %s;''' 
            record = (data['title'],data['date'],data['content'],memo_id,user_id) 
            cursor= connection.cursor()
            cursor.execute(query,record)
            connection.commit()

            cursor.close()
            connection.close()

        except Error as e:
            print(e)
            return {'result': 'fail','error': str(e)},500
        
        return {'result': 'success'}
    
    @jwt_required()
    def delete(selt,memo_id):
        # 1. 클라이언트로부터 데이터 받아온다
        print(memo_id)
        user_id = get_jwt_identity()
        # 2. DB에서 삭제한다
        try:
            connection = get_connection()
            query = '''delete from memo
                    where user_id =%s and id =%s;'''
            record = (user_id,memo_id)
            cursor = connection.cursor()
            cursor.execute(query,record)
            connection.commit()

            cursor.close()
            connection.close()
        except Error as e:
            print(e)
            return {'result': 'success','error':str(e) }
        return {'result': 'success'}
# 데이터베이스 관련 정보 저장
class Config :
    
    # DB 관련 정보
    HOST = 'yhdb.cup7gd2obx5q.ap-northeast-2.rds.amazonaws.com'
    DATABASE = 'memo_db'
    DB_USER = 'memo_db_user'
    DB_PASSWORD = '1234'
    
    # 비번 암호화
    SALT = '0417helloqkqh' # 비번에 붙일 문자열

    # JWT 환경 변수 셋팅
    JWT_SECRET_KEY = 'hello!richtoto'
    JWT_ACCESS_TOKEN_EXPIRES = False
    PROPAGATE_EXCEPTIONS = True
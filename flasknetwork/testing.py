from itsdangerous import URLSafeTimedSerializer as Serializer
import time

s = Serializer('secret')
token = s.dumps({'user_id': 123})
print(token)

time.sleep(1)
print("just woke up again haha")

data = s.loads(token, max_age=10)
print(data)  # {'user_id': 123} 
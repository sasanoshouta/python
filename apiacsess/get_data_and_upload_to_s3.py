#!/usr/bin/env python3
import requests
import json
from datetime import datetime as dt
import datetime
import boto3
import os
import user

client = boto3.client('s3')
bucket = 'my_bucket'
users = user.user_list

headers = {
        "Content-Type": "application/json; charset=UTF-8",
        "Authorization": "Token hogehogehoge"
        }
dt1 = dt.now()
dt2 = dt1 - datetime.timedelta(minutes=3)
# bandlist_response = requests.get('webAPI_URL', headers=headers)
vital_response = requests.get('webAPI_URL/?ts={}'.format(int(dt2.timestamp())), headers=headers)

# bandlist_data = json.loads(bandlist_response.text)
vital_data = json.loads(vital_response.text)

# print("バンドリストのレスポンス確認（json形式）")
# print(bandlist_data)

print("バイタルデータのレスポンス確認(json形式)")
print(vital_data)

date = dt.now() + datetime.timedelta(hours=9)
DAY = date.strftime("%Y-%m-%d")
TIME = date.strftime("%H-%M-%S")
file_path = "dirpath"

user_data = dict()
for user in user.user_list:
    for record in vital_data["data_list"]:
        if user == record['device_user']:
            user_data[user] = record
        else:
            pass

    pref = 'vital_data/{}/{}/'.format(DAY, user)
    file_name = "{}.json".format(TIME)

    with open(file_path+file_name, "w") as outfile:
        json.dump(user_data, outfile)

    client.upload_file(file_path+file_name, bucket, pref+file_name)
    os.remove(file_path+file_name)
    user_data = dict()

    print(user, "json dump ok")

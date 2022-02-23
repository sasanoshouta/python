import streamlit as st
import boto3
import json
from datetime import datetime as dt
import datetime
import os

# 必要な値の準備
s3 = boto3.client('s3')
bucket = 'bucket_name'
client = boto3.client('sagemaker-runtime', region_name='my_region')
ENDPOINT_NAME = 'my_model_endpoint_name'
content_type = 'text/csv'
option_names = [" ", "使えると思う", "候補になり得る", "的外れ"]
gen_name = ["gen0_ja", "gen1_ja", "gen2_ja", "gen3_ja", "gen4_ja", "gen5_ja", "gen6_ja", "gen7_ja", "gen8_ja", "gen9_ja"]
gen_name_en = ["gen0_en", "gen1_en", "gen2_en", "gen3_en", "gen4_en", "gen4_en", "gen5_en", "gen6_en", "gen7_en", "gen8_en", "gen9_en"]
file_path = "/home/ec2-user/streamlit/"
review_dict = dict()
translate = boto3.client("translate", region_name='us-east-2')

for item in zip(gen_name, gen_name_en):
    if item[0] not in st.session_state:
        st.session_state[item[0]] = " "
    if item[1] not in st.session_state:
        st.session_state[item[1]] = " "

# 以下webページ本体
st.title('試験項目生成補助アプリ')
input_text = st.text_input('試験項目を作らせたい文章を入力してください(英語のみ)', ' ', key='input_text')
send = st.button('送信', key="send")
# 送信ボタン押された時の挙動
if send:
    state = st.empty()
    state.write("試験項目を生成しています...")
    response = client.invoke_endpoint(EndpointName=ENDPOINT_NAME, Body=st.session_state['input_text'])
    tmp = response["Body"].read().decode()
    json_result = json.loads(tmp)
    # st.write(json_result[str(i)])
    for i in range(len(json_result)):
        translate_result = translate.translate_text(Text=json_result[str(i)], SourceLanguageCode="en", TargetLanguageCode="ja")
        st.session_state["gen{}_en".format(i)] = json_result[str(i)]
        st.session_state["gen{}_ja".format(i)] = translate_result["TranslatedText"]
    state.write("試験項目生成が完了しました！")

st.write("入力された文章：")
st.write(st.session_state["input_text"])
for num, item in enumerate(zip(gen_name, gen_name_en)):
    st.write("{}/10番目の試験項目：".format(num+1))
    # 生成文章の表示、それに対する評価入力受付箇所
    st.write("英語  : ", st.session_state[item[1]])
    st.write("日本語: ", st.session_state[item[0]])
    option = st.selectbox("生成文章の評価に近いものを選んでください。", option_names, key="option{}".format(num))
    if st.session_state["option{}".format(num)] == "的外れ":
        text = st.text_input("的外れだと思う箇所を記述してください。", ' ', key="text{}".format(num))
# サイドバー表示
st.sidebar.title('モデル一覧')
selector = st.sidebar.selectbox('利用したいモデルを選んでください',
        ('network', 'suiikei', 'general'))

result = st.button("評価送信")
if result:
    final_state = st.empty()
    final_state.write("評価を送信しています...")
    date = dt.now() + datetime.timedelta(hours=9)
    DATE = date.strftime("%Y-%m-%d_%H-%M-%S")
    file_name = "review_{}.json".format(DATE)
    for item in st.session_state.keys():
        review_dict[item] = st.session_state[item]

    with open(file_path+file_name, "w") as outfile:
        json.dump(review_dict, outfile)
    s3.upload_file(file_path+file_name, bucket, file_name)
    os.remove(file_path+file_name)
    review_dict = dict()
    for item in st.session_state.keys():
        del st.session_state[item]
    final_state.write("ご協力ありがとうございます。")

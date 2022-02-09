import streamlit as st
# import requests
# import requests
#
# headers_v = {
#     'User-Agent': "Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1"
# }
#
# v_l = 'http://v26.douyinvod.com/3b193e13907823a6c5e36d96324b4f99/62028447/video/tos/cn/tos-cn-ve-15-alinc2/c1a6e2dd3ef647c5ac77e4dba7ce089c/?a=1128&br=1009&bt=1009&cd=0%7C0%7C0%7C0&ch=96&cr=0&cs=0&0&ds=3&er=&ft=.AAiiIIL7O2WH6BhmS1vLo&l=202202082154540102120451000110F4D3&lr=all&mime_type=video_mp4&net=0&pl=0&qs=0&rc=ang5Zjk6ZjN3OzMzNGkzM0ApaDk4OTUzOmU3Nzc0OTRlNGcpaHV2fWVuZDFwekAtL2tocjRnYy1gLS1kLS9zc18xXl4yY15jMTNfYS5iM2I6Y29zYlxmK2BtYmJeYA%3D%3D&vl=&vr='
#
#
# response = requests.get(v_l, headers=headers_v)
#
#
# # link = 'https://www.runoob.com/wp-content/themes/runoob/assets/images/qrcode.png'
# # r = requests.get(link).content
# # r_v = requests.get(v_l)
#
# reditList = response.history
# print(reditList)
# print(reditList[len(reditList)-1].headers["location"])
# r = requests.get(reditList[len(reditList)-1].headers["location"]).content
#
# # with open('f.mp4', 'wb') as f:
# #     f.write(r_v)
# # with open('f.mp4', 'rb') as f:
# #     v_l = f.read()
#
# # st.image(r)
# st.video(r)


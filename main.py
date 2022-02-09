import datetime
import json
import time

import pandas as pd
import requests
import streamlit as st
from st_aggrid import AgGrid, JsCode
from st_aggrid.grid_options_builder import GridOptionsBuilder
from st_aggrid.shared import GridUpdateMode, DataReturnMode
# from streamlit import session_state
from function_page import millify_w


# 写入ss防止ag-grid刷新时重新获取数据
# if 'video_data' not in session_state:
#     with st.spinner('重新获取数据中...'):
#         with open('data_cache/data.json', 'r') as f:
#             session_state['video_data'] = json.load(f)


# 绝招分割线
def hr_line_skill():
    st.markdown('''
    <style type="text/css" media="all">
    .hrLine{
         vertical-align:middle; display:inline-block;
    }</style>
    <div style=" width:100%; text-align:left; margin-left:15px; margin-right:15px;">
    <hr class='hrLine' style="width:40%;background-color:#00f5f5;"/>
    <font color=#00f5f5>
            <b>视频详情</b>
    </font>
    <hr class="hrLine" style="width:40%;background-color:#00f5f5;"/></div>''',
                unsafe_allow_html=True)


# ag获取数据
with open('data_cache/data.json', 'r') as f:
    all_data = json.load(f)

# all_data = session_state.video_data

play_urls = [v['播放链接'] for v in all_data['video_list']]
data_videos_link = [v['抖音链接'] for v in all_data['video_list']]
user_info = all_data['user_info']
data_videos = []
for i in all_data['video_list']:
    dict_a = {'视频名称': i['视频名'],
              '发布时间': datetime.datetime.fromtimestamp(i['发布时间']).strftime("%Y-%m-%d %H:%M:%S"),
              '分享数': i['流量属性']['分享数'],
              '点赞数': i['流量属性']['点赞数'],
              '评论数': i['流量属性']['评论数'],
              }
    data_videos.append(dict_a)

# 前端

st.set_page_config(page_title='%sの抖音数据小站' % user_info['昵称'],
                   page_icon='🦊',  # logo
                   layout='wide',
                   initial_sidebar_state="expanded",
                   menu_items={'About': '作者: 江大桥'})

# todo 头像大小设置
st.markdown('''<style>
#root > div:nth-child(1) > div > div > div > div > section > div > div:nth-child(1) > div > div:nth-child(1) > div
{
    background-color: lightblue;
}
</style>''', unsafe_allow_html=True)
#        white-space: nowrap;

col_1, col_2, col_a, col_b, col_c = st.columns([1, 1, 1, 1, 1])
with open('ico.jpg', 'rb') as f:
    col_1.image(f.read(),
                use_column_width=False,
                width=200)

# 用户信息展示
col_2.write('')
col_a.markdown('<br><br>', unsafe_allow_html=True)
col_b.markdown('<br><br>', unsafe_allow_html=True)
col_c.markdown('<br><br>', unsafe_allow_html=True)

col_a.metric('作品数', user_info['视频数'])
col_b.metric('总获赞', millify_w(user_info['总获赞']))
col_c.metric('粉丝数', millify_w(user_info['粉丝数']))

# 标题栏
st.header('%sの抖音数据小站' % user_info['昵称'])
# todo 导语，预计将改为上涨最快的视频的title
guide_text_default = '你已经是个带主播啦，没事刷刷自己的数据浅装一下吧~'
st.write('"%s"' % guide_text_default)

# 构建df并合理化index
df = pd.DataFrame(data_videos)
df.index += 1

# 构建ag_options
gb = GridOptionsBuilder.from_dataframe(df)
# js设置单元格格式
# JsCode方式
cell_js = JsCode('''
function(params) {
    function GetDateDiff(startDate)
    {
        var startTime = new Date(Date.parse(startDate.replace(/-/g, "/"))).getTime();
        var endTime = new Date();
        var dates = Math.abs((startTime - endTime))/(1000*60*60);
        return dates;
    }
    if (GetDateDiff(params.value) < 24) {
        return {
            'color': 'black',
            'backgroundColor': '#CCFF99'
        }
    }
};
''')
# # GridOption方式
# cell_js_gb = '''--x_x--0_0--
# function(params) { function GetDateDiff(startDate) { var startTime = new Date(Date.parse(startDate.replace(/-/g, "/"))).getTime(); var endTime = new Date(); var dates = Math.abs((startTime - endTime))/(1000*60*60); return dates; } if (GetDateDiff(params.value) < 24) { return { 'color': 'black', 'backgroundColor': '#CCFF99' } } else { return { 'color': 'black', 'backgroundColor': 'white' } } };
# --x_x--0_0--'''
# 设置选择模式
gb.configure_selection(selection_mode="single", use_checkbox=False)
# 设置发布时间单元格样式
gb.configure_column("发布时间", cellStyle=cell_js)
gridOptions = gb.build()
for i in gridOptions['columnDefs']:
    index_i = gridOptions['columnDefs'].index(i)
    # 设定4列数据列列宽固定
    if i['headerName'] == '点赞数':
        gridOptions['columnDefs'][index_i]['width'] = 70
    if i['headerName'] == '评论数':
        gridOptions['columnDefs'][index_i]['width'] = 70
    if i['headerName'] == '分享数':
        gridOptions['columnDefs'][index_i]['width'] = 70
    if i['headerName'] == '发布时间':
        gridOptions['columnDefs'][index_i]['width'] = 100
        # gridOptions['columnDefs'][index_i][
        #     'cellStyle'] = cell_js_gb
    # 似乎无效
    if i['headerName'] == '视频链接':
        gridOptions['columnDefs'][index_i]['visible'] = False

# 构建ag-grid
MyGrid = AgGrid(
    df,
    gridOptions=gridOptions,
    height=500,
    width='100%',
    allow_unsafe_jscode=True,
    fit_columns_on_grid_load=True,
    data_return_mode=DataReturnMode.FILTERED,
    # enable_enterprise_modules=True,
    update_mode=GridUpdateMode.MODEL_CHANGED
)

hr_line_skill()

# 获取ag-grid回传数据
new_df = MyGrid['data']
# video_info_button = st.button('查看视频详情')
# try:

# selected获取选中数据，如果没有选中则pass
try:
    selected = MyGrid['selected_rows'][0]
    selected_index = data_videos.index(selected)
    # st.write(play_urls[selected_index])
    # st.video(play_urls[selected_index], format='video/mp4')
    # if video_info_button:
    col_img, col_video = st.columns(2)
    # st.write('视频文件没下载全，浅等我补补咯:P')
    cover_file = open('cover_download_list/%s.jpg' % all_data['video_list'][selected_index]['视频id'], 'rb')
    c_b = cover_file.read()
    col_img.subheader(data_videos[selected_index]['视频名称'])
    col_img.markdown('**发布时间**：%s ' %
                     (data_videos[selected_index]['发布时间'],))
    col_img.markdown('**分享数**：%s  **点赞数**：%s  **评论数**：%s' % (
        data_videos[selected_index]['分享数'],
        data_videos[selected_index]['点赞数'],
        data_videos[selected_index]['评论数'],))
    col_img.image(c_b)
    #         st.markdown('''
    #         <video width="320" height="240" controls>
    #   <source src="%s"  type="video/mp4">
    # </video>''' % play_urls[selected_index], unsafe_allow_html=True)
    col_video.markdown('视频链接：' + data_videos_link[selected_index])

    try:
        print('开始读取视频缓存')
        # print(play_urls[selected_index])
        video_file = open('video_download_list/%s.mp4' % all_data['video_list'][selected_index]['视频id'], 'rb')
        r_v = video_file.read()
        print('本地缓存读取成功')
    except FileNotFoundError:
        headers_v = {
            'User-Agent': "Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1"
        }
        print('开始网络读取视频%s' % play_urls[selected_index])
        downloading_info = col_video.info('正在下载抖音视频，请稍等...')
        r = requests.get(play_urls[selected_index], headers=headers_v)
        # 判断是否重定向
        reditList = r.history
        if reditList:
            r_v = requests.get(reditList[len(reditList) - 1].headers["location"]).content
        else:
            r_v = requests.get(play_urls[selected_index], headers_v).content
        # 顺手缓存
        with open('video_download_list/' + all_data['video_list'][selected_index]['视频id'] + '.mp4', 'wb') as f:
            f.write(r.content)
            f.close()
        downloading_info = col_video.success('视频缓存成功')
        time.sleep(1)
    col_video.video(r_v)
    # st.video('你选中的视频链接：' + data_videos_link[selected_index])

    # st.write(gridOptions)

except IndexError:
    pass

with st.expander('查看版本更新日志-点击右侧加号/减号以展开/收起'):
    st.markdown('''# [银河の抖音数据小站](http://101.35.20.145:2300/)

_——守护全世界最好的大彪，助你的普信更上一层楼_

# dev 版 v0.1

**发布时间**：2022-02-08 10:30:00

### 基本功能

1.顶端个人数据栏可显示自己当前的粉丝数、获赞数和作品总数，后期正式版本上线将增加涨粉/掉粉等变化监控功能。

2.左上角及标题栏的「银河」及头像，会随抖音更改而更改。请放心地换头像或改名。~~反正逃不出我代码的手掌心~~

3.主界面为所有视频标题、发布时间、各项数据展示的表格，其中“**发布时间**”列中，会用**浅绿色**标出发布时间距现在不超过**24 小时**的新视频。表格的首行可以**点击排序**。

4.表格内的所有行均可以鼠标单击（或手机屏幕轻触）以选中一个视频，在表格下方查看视频的详细内容，如**封面预览**、**视频内容**等。

5.更多功能等待正式版开发中……
''', unsafe_allow_html=True)

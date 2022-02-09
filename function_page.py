import random
import time
import requests
import json
from urllib import parse

headers = {
    'User-Agent': "Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1"}
# 用户主页的url
user_info_url = 'https://www.iesdouyin.com/web/api/v2/user/info/?sec_uid=MS4wLjABAAAArW_lNsiTMGuUd3jCrCZO8oRN2BaPM0qchnXZs1D0ymbg8HTvPhuWOYCAJzBabkOa'

# 抖音视频的URL : Request URL:
url = "https://www.iesdouyin.com/web/api/v2/aweme/post/?sec_uid=MS4wLjABAAAArW_lNsiTMGuUd3jCrCZO8oRN2BaPM0qchnXZs1D0ymbg8HTvPhuWOYCAJzBabkOa&count=21&max_cursor=0&aid=1128&_signature=R6Ub1QAAJ-gQklOOeJfpTEelG8&dytk="

# 获取时间接口（备用）
url_time = 'https://www.iesdouyin.com/web/api/v2/aweme/iteminfo/?item_ids='


def get_time_2(item_id):
    r = requests.get(url_time + item_id, headers, stream=True).json()['item_list'][0]
    t = r['create_time']
    return t


# 针对抖音以w为单位显示，重构的millify
def millify_w(num):
    num_str = str(num)
    if len(num_str) > 4:
        num_str = round(int(num_str) / 10000, 1)

        str_w = str(num_str) + 'w'
    else:
        str_w = str(num)
    return str_w


def cycle_add_list_data(
        data_json_param,
        video_list_func,
):
    # 爬取发布时间的url

    # 获取当前时间戳
    # time_stamp_now = data_json_param['extra']['now']

    for i in range(len(data_json_param['aweme_list'])):
        # 获取单个视频数据
        single_video_data = data_json_param['aweme_list'][i]

        title = single_video_data['desc']
        tag_position_list = [(pos['start'], pos['end']) for pos in single_video_data['text_extra']]
        # 去除tag获取纯title
        clip_list = [title[c[0]:c[1]] for c in tag_position_list]
        for c in clip_list:
            title = title.replace(c, '')
        # print(random.choice(single_video_data['video']['cover']['url_list']))

        # 尝试直接获取时间
        try:
            creat_time = int(single_video_data['video']['origin_cover']['uri'][-10:])
        except ValueError:
            creat_time = get_time_2(single_video_data['aweme_id'])
        json_down = {
            "视频id": single_video_data['aweme_id'],
            "视频名": title,
            "标签": [text_extra['hashtag_name'] for text_extra in single_video_data['text_extra']],
            "抖音链接": "https://www.douyin.com/video/%s" % single_video_data['aweme_id'],
            # 随机抽取以尝试使用多个镜像
            "播放链接": random.choice(single_video_data['video']['play_addr']['url_list']),
            "封面": random.choice(single_video_data['video']['cover']['url_list']),
            "发布时间": creat_time,
            # "当前时间": time_stamp_now,
            "流量属性":
                {
                    "分享数": single_video_data['statistics']['share_count'],
                    "点赞数": single_video_data['statistics']['digg_count'],
                    "评论数": single_video_data['statistics']['comment_count']
                }
        }

        # data_param = dict_1
        # play_param = data_json_param['aweme_list'][i]['video']['play_addr']['url_list'][0]
        # url_param = 'https://www.douyin.com/video/' + single_video_data['aweme_id']

        # 逐个保存json

        video_list_func.append(json_down)
        # play_list_func.append(play_param)
        # url_list_func.append(url_param)


def get_user_data():
    try:
        with open('data_cache/data.json', 'r') as f:
            a = json.load(f)

    except FileNotFoundError:
        pass

    video_list = []

    # play_list = []
    # url_list = []

    # 调用requests中的get获取抖音作者主页的网页链接
    r = requests.get(url=url, headers=headers, stream=True)
    # 输出访问状态，如为<200>即为访问成功
    print("用户视频数据初始访问状态:", r)
    # 使用json解析获取的网页内容
    data_json = json.loads(r.text)

    has_more = data_json['has_more']
    max_cursor = data_json['max_cursor']

    # 接下来使用循环来解决我们之前所提到的“隐藏内容”问题
    # 判断hasmore是否为true，如果为真则还有隐藏的内容，如果要继续显示剩下的内容
    # name需要根据max_cursor 这个字段来进行分页读取
    # url上次返回的结果中的max_cursor 就是下一次url需要替换的分页数
    while has_more:
        # date_time = re.findall("(202.[0-9]{10})", r.text)[0]
        # print(date_time)
        url_parsed = parse.urlparse(url)  # 打散url连接
        bits = list(url_parsed)  # 将url连接区分开来

        qs = parse.parse_qs(bits[4])  # 选择第四个元素

        qs['max_cursor'] = max_cursor  # 替换掉这个字段的值
        bits[4] = parse.urlencode(qs, True)  # 将替换的字段拼接起来,并且url拼接时不转义
        url_new = parse.urlunparse(bits)  # 重新拼接整个url

        cycle_add_list_data(data_json, video_list)

        # 只要hasmore是否为true，则反复访问作者主页链接，直到成功返回这个为false
        r = requests.get(url=url_new, headers=headers, stream=True)
        data_json = json.loads(r.text)
        has_more = data_json['has_more']  # 重置hasmore直到返回为false则退出循环
        max_cursor = data_json['max_cursor']  # 每次重置这个页数，继续替换url中下一页页码进行访问

    # 补充循环最后一次的视频数据
    cycle_add_list_data(data_json, video_list)

    # info接口视频数获取错误，用aweme接口获取到的视频长度代替
    # 接口获取用户信息
    r_user = requests.get(url=user_info_url, headers=headers, stream=True)
    print("用户信息数据访问状态:", r_user)
    user_info_raw = r_user.json()['user_info']

    user_info = {
        '昵称': user_info_raw['nickname'],
        '签名': user_info_raw['signature'],
        '抖音号': user_info_raw['unique_id'],
        '收藏数': user_info_raw['favoriting_count'],
        '视频数': len(video_list),
        '总获赞': user_info_raw['total_favorited'],
        '粉丝数': user_info_raw['follower_count'],
        '关注数': user_info_raw['following_count'],
        '头像': random.choice(user_info_raw['avatar_larger']['url_list']),
    }

    json_dump_data = {
        'video_list': video_list,
        'user_info': user_info
    }
    # 写入缓存以供st.ss rerun
    with open('data_cache/data.json', 'w') as f:
        json.dump(json_dump_data, f)

    # 写入历史数据以供查找
    file_timestamp = str(int(time.time()))
    with open('data_history/%s.json' % file_timestamp, 'w') as f:
        json.dump(json_dump_data, f)
    print('数据获取完成')
    return video_list, user_info


if __name__ == '__main__':
    while True:
        get_user_data()
        time.sleep(60*5)

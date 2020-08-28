import pandas as pd
import numpy as np
from math import exp


def set_test_data():
    critics = {'Lisa Rose': {'Lady in the Water': 2.5, 'Snakes on a Plane': 3.5,
                             'Just My Luck': 3.0, 'Superman Returns': 3.5, 'You, Me and Dupree': 2.5,
                             'The Night Listener': 3.0},
               'Gene Seymour': {'Lady in the Water': 3.0, 'Snakes on a Plane': 3.5,
                                'Just My Luck': 1.5, 'Superman Returns': 5.0, 'The Night Listener': 3.0,
                                'You, Me and Dupree': 3.5},
               'Michael Phillips': {'Lady in the Water': 2.5, 'Snakes on a Plane': 3.0,
                                    'Superman Returns': 3.5, 'The Night Listener': 4.0},
               'Claudia Puig': {'Snakes on a Plane': 3.5, 'Just My Luck': 3.0,
                                'The Night Listener': 4.5, 'Superman Returns': 4.0,
                                'You, Me and Dupree': 2.5},
               'Mick LaSalle': {'Lady in the Water': 3.0, 'Snakes on a Plane': 4.0,
                                'Just My Luck': 2.0, 'Superman Returns': 3.0, 'The Night Listener': 3.0,
                                'You, Me and Dupree': 2.0},
               'Jack Matthews': {'Lady in the Water': 3.0, 'Snakes on a Plane': 4.0,
                                 'The Night Listener': 3.0, 'Superman Returns': 5.0, 'You, Me and Dupree': 3.5},
               'Toby': {'Snakes on a Plane': 4.5, 'You, Me and Dupree': 1.0, 'Superman Returns': 4.0}}
    critics_df = pd.DataFrame(critics).stack()
    critics_df = pd.DataFrame(
        [critics_df.index.get_level_values(1), critics_df.index.get_level_values(0), critics_df.values],
        index=['user', 'movies', 'rating']).T
    # print(critics_df)
    return critics_df


def get_positive_item(df, user_name):
    positiveItemList = list(df[df['user'] == user_name]['movies'].values)
    print(positiveItemList)
    return positiveItemList


def get_negative_item(df, user_name):
    # 获取用户负反馈物品：热门但是用户没有进行过评分 与正反馈数量相等
    # :param df: 数据集
    # :param user_name:用户
    # :return: 负反馈物品
    user_item_list = list(set(df[df['user'] == user_name]['movies']))  # 用户评分过的物品
    other_item_list = [item for item in set(df['movies'].values) if item not in user_item_list]  # 用户没有评分的物品
    itemCount = [len(df[df['movies'] == item]['user']) for item in other_item_list]  # 物品热门程度
    series = pd.Series(itemCount, index=other_item_list)  # 物品热门程度记录
    series = series.sort_values(ascending=False)[:len(user_item_list)]  # 获取正反馈物品相同数量的负反馈物品
    negativeItemList = list(series.index)
    print(negativeItemList)
    return negativeItemList

# 初始化用户正负反馈物品,正反馈标签为1,负反馈为0
def init_user_item(df, user_list):
    0



if __name__ == '__main__':
    df_critics = set_test_data()
    get_positive_item(df_critics, 'Toby')
    get_negative_item(df_critics, 'Toby')

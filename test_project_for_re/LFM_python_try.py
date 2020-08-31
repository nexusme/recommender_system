import pandas as pd
import numpy as np
from math import exp


# eg from https://blog.csdn.net/a1272899331/article/details/105159964/

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
    # positiveItemList = list(df[df['user'] == user_name]['movies'].values)

    # print(positiveItemList)
    return list(df[df['user'] == user_name]['movies'].values)


def get_negative_item(df, user_name):
    # 获取用户负反馈物品：热门但是用户没有进行过评分 与正反馈数量相等
    # :param df: 数据集
    # :param user_name:用户
    # :return: 负反馈物品
    user_item_list = list(set(df[df['user'] == user_name]['movies']))  # 用户评分过的物品
    other_item_list = [item for item in set(df['movies'].values) if item not in user_item_list]  # 用户没有评分的物品
    itemCount = [len(df[df['movies'] == item]['user']) for item in other_item_list]  # 物品热门程度
    series = pd.Series(itemCount, index=other_item_list)  # 物品热门程度记录
    # negativeItemList = list(series.sort_values(ascending=False)[:len(user_item_list)].index)
    # negativeItemList = list(series.index)
    # print(negativeItemList)
    return list(series.sort_values(ascending=False)[:len(user_item_list)].index)  # 获取正反馈物品相同数量的负反馈物品


# 初始化用户正负反馈物品,正反馈标签为1,负反馈为0
def init_user_item(df, user_list):
    # :param df: ratings数据
    # :param user_list: 用户集
    # :return user_item: 正负反馈物品字典
    user_item = {}
    for user in user_list:
        positive_item = get_positive_item(df, user)
        negative_item = get_negative_item(df, user)
        itemDict = {}
        for item in positive_item:
            itemDict[item] = 1
        for item in negative_item:
            itemDict[item] = 0
        user_item[user] = itemDict
    # for row in user_item:
    #     print(row, user_item[row])
    return user_item


# 初始化参数q,p矩阵, 采用随机初始化的方式，将p和q取值在[0,1]之间
def init_para(user_list, item_list, class_num):
    # :param user_list: 用户集
    # :param item_list: 物品集
    # :param class_num: 隐类数量
    # :return: 参数p, q
    array_p = np.random.rand(len(user_list), class_num)
    array_q = np.random.rand(class_num, len(item_list))
    p = pd.DataFrame(array_p, columns=range(0, class_num), index=user_list)
    q = pd.DataFrame(array_q, columns=item_list, index=range(0, class_num))
    return p, q


# 初始化模型：参数p,q,样本数据
def init_model(df, class_num):
    # :param df: 源数据
    # :param class_num: 隐类数量
    # :return:
    # user_list = list(set(df['user'].values))
    # item_list = list(set(df['movies'].values))
    p_out, q_out = init_para(list(set(df['user'].values)), list(set(df['movies'].values)), class_num)
    user_item_out = init_user_item(df, list(set(df['user'].values)))
    return p_out, q_out, user_item_out


def sigmoid(x):
    return 1.0 / (1 + np.exp(-x))


def lfm_predict(pp, qq, user, item):
    # 利用参数p,q预测目标用户对目标物品的兴趣度
    # :param p: 用户兴趣和隐类的关系
    # :param q: 隐类和物品的关系
    # :param user: 目标用户
    # :param item: 目标物品
    # :return: 预测兴趣度
    pp_manage = np.mat(pp.loc[user].values)
    qq_manage = np.mat(qq.loc[:, item].values).T
    r = (pp_manage * qq_manage).sum()
    r = sigmoid(r)
    return r


# 用梯度下降法计算较优的隐语义模型计算参数p, q
def latent_factor_model(df, class_count, iter_count, alpha, lambda_in):
    # :param df: 源数据
    # :param class_count: 隐类数量
    # :param iterCount: 迭代次数
    # :param alpha: 步长，学习率
    # :param lambda_in: 正则化参数
    # :return: 参数p_result,q_result
    p_result, q_result, user_item = init_model(df, iter_count)

    # 迭代次数
    for step in range(0, iter_count):

        # 循环每个user
        for user in user_item:
            # 循环该user相关的标签和反馈
            for item, rui in user_item[user].items():
                pred = lfm_predict(p_result, q_result, user, item)
                eui = rui - pred
                # 隐类数量
                for f in range(0, class_count):
                    # print('step %d user %s class %d' % (step, user, f))
                    p_result[f][user] += alpha * (eui * q_result[item][f] - lambda_in * p_result[f][user])
                    q_result[item][f] += alpha * (eui * p_result[f][user] - lambda_in * q_result[item][f])
        alpha *= 0.9
    # print(p_result)
    # print(q_result)
    return p_result, q_result


def recommend(df, user_name, p, q, TopN=5):
    # 推荐TopN个物品给目标用户
    # :param frame: 源数据
    # :param user: 目标用户
    # :param p: 用户兴趣和隐类的关系
    # :param q: 隐类和物品的关系
    # :param TopN: 推荐数量
    # :return: 推荐物品
    user_item_list = list(set(df[df['user'] == user_name]['movies']))
    other_item_list = [item for item in set(df['movies'].values) if item not in user_item_list]
    predictList = [lfm_predict(p, q, user, item) for item in other_item_list]  # 对无评分物品的兴趣度预测
    series = pd.Series(predictList, index=other_item_list)
    series = series.sort_values(ascending=False)[:TopN]
    if len(series) == 0:
        print('Recommendation for user *%s*: has not set. \t\n' % user)
    else:
        print('Recommendations for user *%s*:  \t\n' % user, series)

    return series


if __name__ == '__main__':
    i = 0
    df_critics = set_test_data()
    # get_positive_item(df_critics, 'Toby')
    # get_negative_item(df_critics, 'Toby')
    # 初始化用户正负反馈物品,正反馈标签为1,负反馈为0
    init_user_item(df_critics, set(df_critics['user']))
    init_para(set(df_critics['user']), set(df_critics['movies']), 3)
    # p_result, q_result, user_item = initModel(df_critics, 3)
    # result_r = lfm_predict(p_result, q_result, 'Toby', 'You, Me and Dupree')
    para_p, para_q = latent_factor_model(df_critics, 3, 10, 0.02, 0.01)

    dict_save = []
    for user in set(df_critics['user']):
        result_series = recommend(df_critics, user, para_p, para_q)
        dict_save.append([user, result_series.index, result_series.values])


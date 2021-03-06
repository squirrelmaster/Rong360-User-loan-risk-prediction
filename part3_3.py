# -*- coding: utf-8 -*-
# 导入所需的python库
import numpy as np
import pandas as pd
from pandas import Series
from pandas import DataFrame
import csv
import os
import pickle
import cPickle
from math import ceil
import pandas as pd
from sklearn.cross_validation import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report

# -----------------------------------------------------------*- user_info -*--------------------------------------------------------------------
'''第一步处理数据'''
# 读取数据集
print('user_info')
user_info_train = pd.read_csv('../data/train/user_info_train_3_3.csv')
user_info_test = pd.read_csv('../data/test/user_info_test_3_3.csv')
# 合并train、test
user_info = pd.concat([user_info_train, user_info_test]) # 将 user_info_train user_info_test 两个文件行连接
# 5列特征进行 one-hot 编码
dummy_sex = pd.get_dummies(user_info['sex'],prefix='sex')
user_info = pd.concat([user_info , dummy_sex] , axis=1)
user_info.drop(['sex'] , axis = 1 , inplace = True)
dummy_occupation = pd.get_dummies(user_info['occupation'],prefix='occupation')
user_info = pd.concat([user_info , dummy_occupation] , axis=1)
user_info.drop(['occupation'] , axis = 1 , inplace = True)
dummy_education = pd.get_dummies(user_info['education'],prefix='education')
user_info = pd.concat([user_info , dummy_education] , axis=1)
user_info.drop(['education'] , axis = 1 , inplace = True)
dummy_marrige_state = pd.get_dummies(user_info['marrige_state'],prefix='marrige_state')
user_info = pd.concat([user_info , dummy_marrige_state] , axis=1)
user_info.drop(['marrige_state'] , axis = 1 , inplace = True)
dummy_marital = pd.get_dummies(user_info['marital'],prefix='marital')
user_info = pd.concat([user_info , dummy_marital] , axis=1)
user_info.drop(['marital'] , axis = 1 , inplace = True)

user_info.to_csv('../data/part3_3/data1.csv' , index = False , encoding="utf-8" , mode='a')

# -----------------------------------------------------------*- loan_time -*--------------------------------------------------------------------
print('loan_time')
loan_time_train = pd.read_csv('../data/train/loan_time_train.csv' , header = None)
loan_time_test = pd.read_csv('../data/test/loan_time_test.csv' , header = None)
loan_time = pd.concat([loan_time_train, loan_time_test])
loan_time.columns = ['user_id', 'loan_time']

# 将 user_info和 loan_time meger 起来（添加进来的这一列 不能当做特征 最后肯定是要删除掉的）
user_info = pd.merge(user_info , loan_time , on='user_id' , how='inner')

user_info.to_csv('../data/part3_3/data2.csv' , index = False , encoding="utf-8" , mode='a')

# -----------------------------------------------------------*- bank_detail -*--------------------------------------------------------------------
bank_detail_train = pd.read_csv('../data/train/bank_detail_train.csv' , header = None)
bank_detail_test = pd.read_csv('../data/test/bank_detail_test.csv' , header = None)
col_names = ['user_id', 'timestamp', 'trans_type', 'amount', 'salary_label']
bank_detail_train.columns = col_names
bank_detail_test.columns = col_names
bank_detail = pd.concat([bank_detail_train, bank_detail_test])

'''这个文件做出来的所有特征'''
# 1：借款时间之前（前缀是：bef_loan_）
#  1：交易类型有几种(前缀是：trans)
#  2：交易类型为0，有几条交易数据(a) trans_0_num？交易总金额有多少(b) trans_0_money？b/a多少 trans_0_div
#     交易类型为1，有几条交易数据(a) trans_1_num？交易总金额有多少(b) trans_1_money？b/a多少 trans_1_div
#  3：工资收入标记有几种(label)
#  4：工资收入为0时，有几条交易数据(a) label_0_num？交易总金额有多少(b) label_0_money？b/a多少 label_0_div
#     工资收入为1时，有几条交易数据(a) label_1_num？交易总金额有多少(b) label_1_money？b/a多少 label_1_div
#  5：交易类型 与 工资收入标记 相同的个数 -- 'bef_loan_equal'
#  6：交易类型 与 工资收入标记 不相同的个数 -- 'bef_loan_not_equal'
# 2：借款时间之后（前缀是：aft_loan_）
#  1：交易类型有几种
#  2：交易类型为0，有几条交易数据(a)？交易总金额有多少(b)？b/a多少
#     交易类型为1，有几条交易数据(a)？交易总金额有多少(b)？b/a多少
#  3：工资收入标记有几种
#  4：工资收入为0时，有几条交易数据(a)？交易总金额有多少(b)？b/a多少
#     工资收入为1时，有几条交易数据(a)？交易总金额有多少(b)？b/a多少
#  5：交易类型 与 工资收入标记 相同的个数 -- 'aft_loan_equal'
#  6：交易类型 与 工资收入标记 不相同的个数 -- 'aft_loan_not_equal'

# 第一步：将上面的所有特征全部添加到 user_info 中，初始化先全部置0
bank_fea = ['bef_loan_trans','bef_loan_trans_0_num','bef_loan_trans_0_money','bef_loan_trans_0_div','bef_loan_trans_1_num','bef_loan_trans_1_money','bef_loan_trans_1_div',\
            'bef_loan_label','bef_loan_label_0_num','bef_loan_label_0_money','bef_loan_label_0_div','bef_loan_label_1_num','bef_loan_label_1_money','bef_loan_label_1_div',\
            'bef_loan_equal','bef_loan_not_equal',\
            'aft_loan_trans','aft_loan_trans_0_num','aft_loan_trans_0_money','aft_loan_trans_0_div','aft_loan_trans_1_num','aft_loan_trans_1_money','aft_loan_trans_1_div',\
            'aft_loan_label','aft_loan_label_0_num','aft_loan_label_0_money','aft_loan_label_0_div','aft_loan_label_1_num','aft_loan_label_1_money','aft_loan_label_1_div',\
            'aft_loan_equal','aft_loan_not_equal']
for i in bank_fea:
    user_info[i] = 0
# 第二步：用程序的方法将上面这些初始化为0的特征列，全部赋为正确值
for i in user_info['user_id'].unique():
    print(i) 
    data = bank_detail[bank_detail['user_id'] == i]
    # 将data数据分成两部分，划分依据是 时间戳timestamp 是否 大于 借款时间 loan_time
    time_1 = user_info[user_info['user_id'] == i]['loan_time'][user_info[user_info['user_id'] == i]['loan_time'].index[0]] # 这个用户的借款时间
    '''先来做 大于 借款时间（借款之后）'''
    data_1 = data[data['timestamp'] >= time_1]
    if(len(data_1) > 0):
        user_info.loc[user_info['user_id'] == i,'aft_loan_trans'] = len(data_1['trans_type'].unique())
        user_info.loc[user_info['user_id'] == i,'aft_loan_trans_0_num'] = len(data_1[data_1['trans_type'] == 0])
        user_info.loc[user_info['user_id'] == i,'aft_loan_trans_0_money'] = data_1[data_1['trans_type'] == 0]['amount'].sum()
        if(len(data_1[data_1['trans_type'] == 0]) != 0):
            user_info.loc[user_info['user_id'] == i,'aft_loan_trans_0_div'] = data_1[data_1['trans_type'] == 0]['amount'].sum() / len(data_1[data_1['trans_type'] == 0])
        else:
            user_info.loc[user_info['user_id'] == i,'aft_loan_trans_0_div'] = 99
        user_info.loc[user_info['user_id'] == i,'aft_loan_trans_1_num'] = len(data_1[data_1['trans_type'] == 1])
        user_info.loc[user_info['user_id'] == i,'aft_loan_trans_1_money'] = data_1[data_1['trans_type'] == 1]['amount'].sum()
        if(len(data_1[data_1['trans_type'] == 0]) != 0):
            user_info.loc[user_info['user_id'] == i,'aft_loan_trans_1_div'] = data_1[data_1['trans_type'] == 1]['amount'].sum() / len(data_1[data_1['trans_type'] == 0])
        else:
            user_info.loc[user_info['user_id'] == i,'aft_loan_trans_1_div'] = 99
        
        user_info.loc[user_info['user_id'] == i,'aft_loan_label'] = len(data_1['salary_label'].unique())
        user_info.loc[user_info['user_id'] == i,'aft_loan_label_0_num'] = len(data_1[data_1['salary_label'] == 0])
        user_info.loc[user_info['user_id'] == i,'aft_loan_label_0_money'] = data_1[data_1['salary_label'] == 0]['amount'].sum()
        if(len(data_1[data_1['salary_label'] == 0]) != 0):
            user_info.loc[user_info['user_id'] == i,'aft_loan_label_0_div'] = data_1[data_1['salary_label'] == 0]['amount'].sum() / len(data_1[data_1['salary_label'] == 0])
        else:
            user_info.loc[user_info['user_id'] == i,'aft_loan_label_0_div'] = 99
        user_info.loc[user_info['user_id'] == i,'aft_loan_label_1_num'] = len(data_1[data_1['salary_label'] == 1])
        user_info.loc[user_info['user_id'] == i,'aft_loan_label_1_money'] = data_1[data_1['salary_label'] == 1]['amount'].sum()
        if(len(data_1[data_1['salary_label'] == 0]) != 0):
            user_info.loc[user_info['user_id'] == i,'aft_loan_label_1_div'] = data_1[data_1['salary_label'] == 1]['amount'].sum() / len(data_1[data_1['salary_label'] == 0])
        else:
            user_info.loc[user_info['user_id'] == i,'aft_loan_label_1_div'] = 99
    
        user_info.loc[user_info['user_id'] == i,'aft_loan_equal'] = len(data_1[data_1['trans_type'] != data_1['salary_label']])
        user_info.loc[user_info['user_id'] == i,'aft_loan_not_equal'] = len(data_1[data_1['trans_type'] == data_1['salary_label']])
        
    
    '''再来做 小于 借款时间（借款之前）'''
    data_2 = data[data['timestamp'] < time_1]
    if(len(data_2) > 0):
        user_info.loc[user_info['user_id'] == i,'bef_loan_trans'] = len(data_2['trans_type'].unique())
        user_info.loc[user_info['user_id'] == i,'bef_loan_trans_0_num'] = len(data_2[data_2['trans_type'] == 0])
        user_info.loc[user_info['user_id'] == i,'bef_loan_trans_0_money'] = data_2[data_2['trans_type'] == 0]['amount'].sum()
        if(len(data_2[data_2['trans_type'] == 0]) != 0):
            user_info.loc[user_info['user_id'] == i,'bef_loan_trans_0_div'] = data_2[data_2['trans_type'] == 0]['amount'].sum() / len(data_2[data_2['trans_type'] == 0])
        else:
            user_info.loc[user_info['user_id'] == i,'bef_loan_trans_0_div'] = 0
        user_info.loc[user_info['user_id'] == i,'bef_loan_trans_1_num'] = len(data_2[data_2['trans_type'] == 1])
        user_info.loc[user_info['user_id'] == i,'bef_loan_trans_1_money'] = data_2[data_2['trans_type'] == 1]['amount'].sum()
        if(len(data_2[data_2['trans_type'] == 0]) != 0):
            user_info.loc[user_info['user_id'] == i,'bef_loan_trans_1_div'] = data_2[data_2['trans_type'] == 1]['amount'].sum() / len(data_2[data_2['trans_type'] == 0])
        else:
            user_info.loc[user_info['user_id'] == i,'bef_loan_trans_1_div'] = 99
    
        user_info.loc[user_info['user_id'] == i,'bef_loan_label'] = len(data_2['salary_label'].unique())
        user_info.loc[user_info['user_id'] == i,'bef_loan_label_0_num'] = len(data_2[data_2['salary_label'] == 0])
        user_info.loc[user_info['user_id'] == i,'bef_loan_label_0_money'] = data_2[data_2['salary_label'] == 0]['amount'].sum()
        if(len(data_2[data_2['salary_label'] == 0]) != 0):
            user_info.loc[user_info['user_id'] == i,'bef_loan_label_0_div'] = data_2[data_2['salary_label'] == 0]['amount'].sum() / len(data_2[data_2['salary_label'] == 0])
        else:
            user_info.loc[user_info['user_id'] == i,'bef_loan_label_0_div'] = 99
        user_info.loc[user_info['user_id'] == i,'bef_loan_label_1_num'] = len(data_2[data_2['salary_label'] == 1])
        user_info.loc[user_info['user_id'] == i,'bef_loan_label_1_money'] = data_2[data_2['salary_label'] == 1]['amount'].sum()
        if(len(data_2[data_2['salary_label'] == 0]) != 0):
            user_info.loc[user_info['user_id'] == i,'bef_loan_label_1_div'] = data_2[data_2['salary_label'] == 1]['amount'].sum() / len(data_2[data_2['salary_label'] == 0])
        else:
            user_info.loc[user_info['user_id'] == i,'bef_loan_label_1_div'] = 99
    
        user_info.loc[user_info['user_id'] == i,'bef_loan_equal'] = len(data_2[data_2['trans_type'] != data_2['salary_label']])
        user_info.loc[user_info['user_id'] == i,'bef_loan_not_equal'] = len(data_2[data_2['trans_type'] == data_2['salary_label']])
    
user_info.to_csv('../data/part3_3/data3.csv' , index = False , encoding="utf-8" , mode='a')
    
# -----------------------------------------------------------*- overdue_train -*--------------------------------------------------------------------
print('overdue_train')
target = pd.read_csv('../data/train/overdue_train.csv' , header = None)
target.columns = ['user_id', 'label']

user_info = pd.merge(user_info , target , on='user_id' , how='inner')
print(user_info.head(20))
user_info.to_csv('../data/part3_3/train.csv' , index = False , encoding="utf-8" , mode='a') # data6.csv是这一部分用户的训练集（在这个程序里面一块做出来）



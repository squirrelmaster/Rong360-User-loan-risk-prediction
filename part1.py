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
user_info_train = pd.read_csv('../data/train/user_info_train_1.csv')
user_info_test = pd.read_csv('../data/test/user_info_test_1.csv')
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

user_info.to_csv('../data/part1/data1.csv' , index = False , encoding="utf-8" , mode='a')

# -----------------------------------------------------------*- loan_time -*--------------------------------------------------------------------
print('loan_time')
loan_time_train = pd.read_csv('../data/train/loan_time_train.csv' , header = None)
loan_time_test = pd.read_csv('../data/test/loan_time_test.csv' , header = None)
loan_time = pd.concat([loan_time_train, loan_time_test])
loan_time.columns = ['user_id', 'loan_time']

# 将 user_info和 loan_time meger 起来（添加进来的这一列 不能当做特征 最后肯定是要删除掉的）
user_info = pd.merge(user_info , loan_time , on='user_id' , how='inner')

user_info.to_csv('../data/part1/data2.csv' , index = False , encoding="utf-8" , mode='a')

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
    
user_info.to_csv('../data/part1/data3.csv' , index = False , encoding="utf-8" , mode='a')
    
# -----------------------------------------------------------*- browse_history -*--------------------------------------------------------------------
print('browse_history')
browse_history_train = pd.read_csv('../data/train/browse_history_train.csv' , header = None)
browse_history_test = pd.read_csv('../data/test/browse_history_test.csv' , header = None)
col_names = ['user_id', 'timestamp', 'browse_data', 'child_numbers']
browse_history_train.columns = col_names
browse_history_test.columns = col_names
browse_history = pd.concat([browse_history_train, browse_history_test])

# 1：借款时间之前 （前缀是：bef_loan_）
#  1：“浏览行为数据”有多少条（bef_loan_borwse_num1）？多少种(unique)（bef_loan_borwse_num2）
#  2：每一种“浏览行为数据”有多少条（）
#  3：“浏览子行为编号”有多少条（bef_loan_borwse_num4）？多少种(unique)（bef_loan_borwse_num5）
#  4：每一种“浏览子行为编号”有多少条（）
# 2：借款时间之后 aft_loan_
#  1：“浏览行为数据”有多少条（aft_loan_borwse_num1）？多少种(unique)（aft_loan_borwse_num2）
#  2：每一种“浏览行为数据”有多少条（）
#  3：“浏览子行为编号”有多少条（aft_loan_borwse_num4）？多少种(unique)（aft_loan_borwse_num5）
#  4：每一种“浏览子行为编号”有多少条（）

# 将上面的特征分成 两部分，这是第一部分
print('the first_part feature')
browse_fea = ['bef_loan_borwse_num1' , 'bef_loan_borwse_num2' , 'bef_loan_borwse_num4' , 'bef_loan_borwse_num5' ,\
              'aft_loan_borwse_num1' , 'aft_loan_borwse_num2' , 'aft_loan_borwse_num4' , 'aft_loan_borwse_num5']
for i in browse_fea: # 添加8个特征
    user_info[i] = 0
for i in user_info['user_id'].unique():
    print(i) 
    data = browse_history[browse_history['user_id'] == i]
    # 将data数据分成两部分，划分依据是 时间戳timestamp 是否 大于 借款时间 loan_time
    time_1 = user_info[user_info['user_id'] == i]['loan_time'][user_info[user_info['user_id'] == i]['loan_time'].index[0]]
    '''先来做 大于 借款时间（借款之后）'''
    data_1 = data[data['timestamp'] >= time_1]
    if(len(data_1) > 0):
        user_info.loc[user_info['user_id'] == i,'aft_loan_borwse_num1'] = len(data_1)
        user_info.loc[user_info['user_id'] == i,'aft_loan_borwse_num2'] = len(data_1['browse_data'].unique())
        user_info.loc[user_info['user_id'] == i,'aft_loan_borwse_num4'] = len(data_1)
        user_info.loc[user_info['user_id'] == i,'aft_loan_borwse_num5'] = len(data_1['child_numbers'].unique())
    '''再来做 小于 借款时间（借款之前）'''
    data_2 = data[data['timestamp'] < time_1]
    if(len(data_2) > 0):
        user_info.loc[user_info['user_id'] == i,'bef_loan_borwse_num1'] = len(data_2)
        user_info.loc[user_info['user_id'] == i,'bef_loan_borwse_num2'] = len(data_2['browse_data'].unique())
        user_info.loc[user_info['user_id'] == i,'bef_loan_borwse_num4'] = len(data_2)
        user_info.loc[user_info['user_id'] == i,'bef_loan_borwse_num5'] = len(data_2['child_numbers'].unique())
        
# 下来是第二部分，先添加这些特征列，全部初始化成0
print('the second_part feature')
for i in browse_history['browse_data'].unique(): # 添加特征列（借款之前）
    user_info['bef_loan_browse_data_' + str(i)] = 0
for i in browse_history['child_numbers'].unique():
    user_info['bef_loan_child_numbers_' + str(i)] = 0

for i in browse_history['browse_data'].unique(): # 添加特征列（借款之后）
    user_info['aft_loan_browse_data_' + str(i)] = 0
for i in browse_history['child_numbers'].unique():
    user_info['aft_loan_child_numbers_' + str(i)] = 0
# 用程序的方法，将其赋成正确的值   
for i in user_info['user_id'].unique():
    print(i)
    data = browse_history[browse_history['user_id'] == i]
    # 将data数据分成两部分，划分依据是 时间戳timestamp 是否 大于 借款时间 loan_time
    time_1 = user_info[user_info['user_id'] == i]['loan_time'][user_info[user_info['user_id'] == i]['loan_time'].index[0]]
    '''先来做 大于 借款时间（借款之后）'''
    data_1 = data[data['timestamp'] >= time_1]
    for j in data_1['browse_data']:
        user_info.loc[user_info['user_id'] == i , 'aft_loan_browse_data_' + str(j)] += 1
    for j in data_1['child_numbers']:
        user_info.loc[user_info['user_id'] == i , 'aft_loan_child_numbers_' + str(j)] += 1
        
    '''再来做 小于 借款时间（借款之前）'''
    data_2 = data[data['timestamp'] < time_1]
    for j in data_2['browse_data']:
        user_info.loc[user_info['user_id'] == i , 'bef_loan_browse_data_' + str(j)] += 1
    for j in data_2['child_numbers']:
        user_info.loc[user_info['user_id'] == i , 'bef_loan_child_numbers_' + str(j)] += 1
               
user_info.to_csv('../data/part1/data4.csv' , index = False , encoding="utf-8" , mode='a')

# -----------------------------------------------------------*- bill_detail -*--------------------------------------------------------------------
print('bill_detail')    
bill_detail_train = pd.read_csv('../data/train/bill_detail_train.csv' , header = None)
bill_detail_test = pd.read_csv('../data/test/bill_detail_test.csv' , header = None)
col_names = ['user_id', 'timestamp', 'bank_id', 'shang_bill', 'shang_repay',\
             'credit_amount', 'current_bill_sheng', 'current_bill_lowest', 'consume_pen', 'current_bill_amount',\
             'adjust_amount', 'circu_interest', 'avail_balance', 'cash_yujie', 'repay_state']
bill_detail_train.columns = col_names
bill_detail_test.columns = col_names
bill_detail = pd.concat([bill_detail_train, bill_detail_test])

'''这个文件的特征分为3类，每一类都是先添加特征（加初始化），再用程序的方法进行赋值'''
# 先是第一部分（一共是3个特征，但因为要分借款前后，所以就是6个）
# 1：每一个用户有多少张账单
# 2：每一个用户在每一个银行中有几条记录（unique）
# 3：每一个用户还款状态有几种 (unique)
print('the first part features')
part_1 = ['bef_loan_bill_num' , 'bef_loan_bank_num' , 'bef_loan_state_num' , 'aft_loan_bill_num' , 'aft_loan_bank_num' , 'aft_loan_state_num']
for i in part_1: # 添加特征 + 初始化为0
    user_info[i] = 0
for i in user_info['user_id'].unique(): # 赋值特征
    print(i)
    data = bill_detail[bill_detail['user_id'] == i]
    # 将data数据分成两部分，划分依据是 时间戳timestamp 是否 大于 借款时间 loan_time
    time_1 = user_info[user_info['user_id'] == i]['loan_time'][user_info[user_info['user_id'] == i]['loan_time'].index[0]]
    '''先来做 大于 借款时间（借款之后）'''
    data_1 = data[data['timestamp'] >= time_1]
    user_info.loc[user_info['user_id'] == i , 'aft_loan_bill_num'] = len(data_1)
    user_info.loc[user_info['user_id'] == i , 'aft_loan_bank_num'] = len(data_1['bank_id'].unique())
    user_info.loc[user_info['user_id'] == i , 'aft_loan_state_num'] = len(data_1['repay_state'].unique())    
    
    '''先来做 小于 借款时间（借款之前）'''
    data_2 = data[data['timestamp'] < time_1]
    user_info.loc[user_info['user_id'] == i , 'bef_loan_bill_num'] = len(data_2)
    user_info.loc[user_info['user_id'] == i , 'bef_loan_bank_num'] = len(data_2['bank_id'].unique())
    user_info.loc[user_info['user_id'] == i , 'bef_loan_state_num'] = len(data_2['repay_state'].unique())        

# 再是第二部分
# 1：每一个银行有几张账单
# 2：每一种还款状态各有几种
print('the second part features')
for i in bill_detail['bank_id'].unique(): # 借款之前
    user_info['bef_loan_bank_' + str(i)] = 0
for i in bill_detail['repay_state'].unique():
    user_info['bef_loan_repay_state_' + str(i)] = 0

for i in bill_detail['bank_id'].unique(): # 借款之后
    user_info['aft_loan_bank_' + str(i)] = 0
for i in bill_detail['repay_state'].unique():
    user_info['aft_loan_repay_state_' + str(i)] = 0

for i in user_info['user_id'].unique():
    print(i)
    data = bill_detail[bill_detail['user_id'] == i]
    # 将data数据分成两部分，划分依据是 时间戳timestamp 是否 大于 借款时间 loan_time
    time_1 = user_info[user_info['user_id'] == i]['loan_time'][user_info[user_info['user_id'] == i]['loan_time'].index[0]]
    '''先来做 大于 借款时间（借款之后）'''
    data_1 = data[data['timestamp'] >= time_1]
    for j in data_1['bank_id']:
        user_info.loc[user_info['user_id'] == i , 'aft_loan_bank_' + str(j)] += 1
    for j in data_1['repay_state']:
        user_info.loc[user_info['user_id'] == i , 'aft_loan_repay_state_' + str(j)] += 1
        
    '''先来做 小于 借款时间（借款之前）'''
    data_2 = data[data['timestamp'] < time_1]
    for j in data_2['bank_id']:
        user_info.loc[user_info['user_id'] == i , 'bef_loan_bank_' + str(j)] += 1
    for j in data_2['repay_state']:
        user_info.loc[user_info['user_id'] == i , 'bef_loan_repay_state_' + str(j)] += 1 

# 再是第三部分
# 1：上期账单总金额 + 均值（就是除以 len(data)） bef_loan_shang_bill bef_loan_shang_bill_mean aft_loan_shang_bill aft_loan_shang_bill_mean
# 2：上期还款总金额 + 均值        bef_loan_shang_repay bef_loan_shang_repay_mean aft_loan_shang_repay aft_loan_shang_repay_mean
# 3：信用卡额度 + 均值       bef_loan_credit_amount bef_loan_credit_amount_mean aft_loan_credit_amount aft_loan_credit_amount_mean
# 4：本期账单余额 + 均值    bef_loan_current_bill_sheng bef_loan_current_bill_sheng_mean aft_loan_current_bill_sheng aft_loan_current_bill_sheng_mean
# 5：本期账单最低还款额 + 均值   bef_loan_current_bill_lowest bef_loan_current_bill_lowest_mean aft_loan_current_bill_lowest aft_loan_current_bill_lowest_mean
# 6：消费笔数（总笔数） + 均值   bef_loan_consume_pen bef_loan_consume_pen_mean aft_loan_consume_pen aft_loan_consume_pen_mean
# 7：本期账单余额 + 均值   bef_loan_current_bill_amount bef_loan_current_bill_amount_mean aft_loan_current_bill_amount aft_loan_current_bill_amount_mean
# 8：调整金额 + 均值   bef_loan_adjust_amount bef_loan_adjust_amount_mean aft_loan_adjust_amount aft_loan_adjust_amount_mean
# 9：循环利息 + 均值   bef_loan_circu_interest bef_loan_circu_interest_mean aft_loan_circu_interest aft_loan_circu_interest_mean
# 10：可用余额 + 均值  bef_loan_avail_balance bef_loan_avail_balance_mean aft_loan_avail_balance aft_loan_avail_balance_mean
# 11：预借现金额度 + 均值   bef_loan_cash_yujie bef_loan_cash_yujie_mean aft_loan_cash_yujie aft_loan_cash_yujie_mean

# 添加所有列
list_bill = ['bef_loan_shang_bill' , 'bef_loan_shang_bill_mean' , 'aft_loan_shang_bill' , 'aft_loan_shang_bill_mean',\
        'bef_loan_shang_repay' , 'bef_loan_shang_repay_mean' , 'aft_loan_shang_repay' , 'aft_loan_shang_repay_mean',\
        'bef_loan_credit_amount' , 'bef_loan_credit_amount_mean' , 'aft_loan_credit_amount' , 'aft_loan_credit_amount_mean',\
        'bef_loan_current_bill_sheng' , 'bef_loan_current_bill_sheng_mean' , 'aft_loan_current_bill_sheng' , 'aft_loan_current_bill_sheng_mean',\
        'bef_loan_current_bill_lowest' , 'bef_loan_current_bill_lowest_mean' , 'aft_loan_current_bill_lowest' , 'aft_loan_current_bill_lowest_mean',\
        'bef_loan_consume_pen' , 'bef_loan_consume_pen_mean' , 'aft_loan_consume_pen' , 'aft_loan_consume_pen_mean',\
        'bef_loan_current_bill_amount' , 'bef_loan_current_bill_amount_mean' , 'aft_loan_current_bill_amount' , 'aft_loan_current_bill_amount_mean',\
        'bef_loan_adjust_amount' , 'bef_loan_adjust_amount_mean' , 'aft_loan_adjust_amount' , 'aft_loan_adjust_amount_mean',\
        'bef_loan_circu_interest' , 'bef_loan_circu_interest_mean' , 'aft_loan_circu_interest' , 'aft_loan_circu_interest_mean',\
        'bef_loan_avail_balance' , 'bef_loan_avail_balance_mean' , 'aft_loan_avail_balance' , 'aft_loan_avail_balance_mean',\
        'bef_loan_cash_yujie' , 'bef_loan_cash_yujie_mean' , 'aft_loan_cash_yujie' , 'aft_loan_cash_yujie_mean'
]
for i in list_bill: # 添加特征 + 初始化为0
    user_info[i] = 0

# 赋新值
print('the third part features') 
for i in user_info['user_id'].unique():
    print(i)
    data = bill_detail[bill_detail['user_id'] == i]
    # 将data数据分成两部分，划分依据是 时间戳timestamp 是否 大于 借款时间 loan_time
    time_1 = user_info[user_info['user_id'] == i]['loan_time'][user_info[user_info['user_id'] == i]['loan_time'].index[0]]
    '''先来做 大于 借款时间（借款之后）'''
    data_1 = data[data['timestamp'] >= time_1]
    a = len(data_1)
    if(a > 0):
        user_info.loc[user_info['user_id'] == i , 'aft_loan_shang_bill'] = data_1['shang_bill'].sum()
        user_info.loc[user_info['user_id'] == i , 'aft_loan_shang_bill_mean'] = data_1['shang_bill'].sum() / a
        user_info.loc[user_info['user_id'] == i , 'aft_loan_shang_repay'] = data_1['shang_repay'].sum()
        user_info.loc[user_info['user_id'] == i , 'aft_loan_shang_repay_mean'] = data_1['shang_repay'].sum() / a
        user_info.loc[user_info['user_id'] == i , 'aft_loan_credit_amount'] = data_1['credit_amount'].sum()
        user_info.loc[user_info['user_id'] == i , 'aft_loan_credit_amount_mean'] = data_1['credit_amount'].sum() / a   
        user_info.loc[user_info['user_id'] == i , 'aft_loan_current_bill_sheng'] = data_1['current_bill_sheng'].sum()
        user_info.loc[user_info['user_id'] == i , 'aft_loan_current_bill_sheng_mean'] = data_1['current_bill_sheng'].sum() / a  
        user_info.loc[user_info['user_id'] == i , 'aft_loan_current_bill_lowest'] = data_1['current_bill_lowest'].sum()
        user_info.loc[user_info['user_id'] == i , 'aft_loan_current_bill_lowest_mean'] = data_1['current_bill_lowest'].sum() / a
        user_info.loc[user_info['user_id'] == i , 'aft_loan_consume_pen'] = data_1['consume_pen'].sum()
        user_info.loc[user_info['user_id'] == i , 'aft_loan_consume_pen_mean'] = data_1['consume_pen'].sum() / a
        user_info.loc[user_info['user_id'] == i , 'aft_loan_current_bill_amount'] = data_1['current_bill_amount'].sum()
        user_info.loc[user_info['user_id'] == i , 'aft_loan_current_bill_amount_mean'] = data_1['current_bill_amount'].sum() / a
        user_info.loc[user_info['user_id'] == i , 'aft_loan_adjust_amount'] = data_1['adjust_amount'].sum()
        user_info.loc[user_info['user_id'] == i , 'aft_loan_adjust_amount_mean'] = data_1['adjust_amount'].sum() / a
        user_info.loc[user_info['user_id'] == i , 'aft_loan_circu_interest'] = data_1['circu_interest'].sum()
        user_info.loc[user_info['user_id'] == i , 'aft_loan_circu_interest_mean'] = data_1['circu_interest'].sum() / a
        user_info.loc[user_info['user_id'] == i , 'aft_loan_avail_balance'] = data_1['avail_balance'].sum()
        user_info.loc[user_info['user_id'] == i , 'aft_loan_avail_balance_mean'] = data_1['avail_balance'].sum() / a
        user_info.loc[user_info['user_id'] == i , 'aft_loan_cash_yujie'] = data_1['cash_yujie'].sum()
        user_info.loc[user_info['user_id'] == i , 'aft_loan_cash_yujie_mean'] = data_1['cash_yujie'].sum() / a
        
    '''先来做 小于 借款时间（借款之前）'''
    data_2 = data[data['timestamp'] < time_1]
    b = len(data_2)
    if(b > 0):
        user_info.loc[user_info['user_id'] == i , 'bef_loan_shang_bill'] = data_2['shang_bill'].sum()
        user_info.loc[user_info['user_id'] == i , 'bef_loan_shang_bill_mean'] = data_2['shang_bill'].sum() / b
        user_info.loc[user_info['user_id'] == i , 'bef_loan_shang_repay'] = data_2['shang_repay'].sum()
        user_info.loc[user_info['user_id'] == i , 'bef_loan_shang_repay_mean'] = data_2['shang_repay'].sum() / b
        user_info.loc[user_info['user_id'] == i , 'bef_loan_credit_amount'] = data_2['credit_amount'].sum()
        user_info.loc[user_info['user_id'] == i , 'bef_loan_credit_amount_mean'] = data_2['credit_amount'].sum() / b   
        user_info.loc[user_info['user_id'] == i , 'bef_loan_current_bill_sheng'] = data_2['current_bill_sheng'].sum()
        user_info.loc[user_info['user_id'] == i , 'bef_loan_current_bill_sheng_mean'] = data_2['current_bill_sheng'].sum() / b  
        user_info.loc[user_info['user_id'] == i , 'bef_loan_current_bill_lowest'] = data_2['current_bill_lowest'].sum()
        user_info.loc[user_info['user_id'] == i , 'bef_loan_current_bill_lowest_mean'] = data_2['current_bill_lowest'].sum() / b
        user_info.loc[user_info['user_id'] == i , 'bef_loan_consume_pen'] = data_2['consume_pen'].sum()
        user_info.loc[user_info['user_id'] == i , 'bef_loan_consume_pen_mean'] = data_2['consume_pen'].sum() / b
        user_info.loc[user_info['user_id'] == i , 'bef_loan_current_bill_amount'] = data_2['current_bill_amount'].sum()
        user_info.loc[user_info['user_id'] == i , 'bef_loan_current_bill_amount_mean'] = data_2['current_bill_amount'].sum() / b
        user_info.loc[user_info['user_id'] == i , 'bef_loan_adjust_amount'] = data_2['adjust_amount'].sum()
        user_info.loc[user_info['user_id'] == i , 'bef_loan_adjust_amount_mean'] = data_2['adjust_amount'].sum() / b
        user_info.loc[user_info['user_id'] == i , 'bef_loan_circu_interest'] = data_2['circu_interest'].sum()
        user_info.loc[user_info['user_id'] == i , 'bef_loan_circu_interest_mean'] = data_2['circu_interest'].sum() / b
        user_info.loc[user_info['user_id'] == i , 'bef_loan_avail_balance'] = data_2['avail_balance'].sum()
        user_info.loc[user_info['user_id'] == i , 'bef_loan_avail_balance_mean'] = data_2['avail_balance'].sum() / b
        user_info.loc[user_info['user_id'] == i , 'bef_loan_cash_yujie'] = data_2['cash_yujie'].sum()
        user_info.loc[user_info['user_id'] == i , 'bef_loan_cash_yujie_mean'] = data_2['cash_yujie'].sum() / b

user_info.to_csv('../data/part1/data5.csv' , index = False , encoding="utf-8" , mode='a')

# -----------------------------------------------------------*- overdue_train -*--------------------------------------------------------------------
print('overdue_train')
target = pd.read_csv('../data/train/overdue_train.csv' , header = None)
target.columns = ['user_id', 'label']

user_info = pd.merge(user_info , target , on='user_id' , how='inner')
print(user_info.head(20))
user_info.to_csv('../data/part1/data6.csv' , index = False , encoding="utf-8" , mode='a') # data6.csv是这一部分用户的训练集（在这个程序里面一块做出来）























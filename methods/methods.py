# -*- coding:utf-8 -*-
'''
目的：提供一些文件操作 和 数据处理的方法

方法：
    ----------功能 ------------ 方法 ---------------
    * RGB颜色与HEX颜色互转 - hex2rgb 与 rgb2hex
    * 读取文件较大的csv - read_csv
    * 获取当前目录下所有子目录 - get_subdirs
    * 获取当前目录下所有该类型的文件名 - get_files
    * 获取当前目录和所有子目录下所有该类型的文件名 - get_files_all
    * 数据表随机长度的抽样 - random_dataframe_sample
    * 计算概率密度分布 - distribution_pdf
    * 计算累计概率密度分布 - distribution_cdf
    * 计算频率分布 - distribution_fre
    * 数据归一化到某个区间 - normlize

备注：
    * 2017.10.16 - dataframe_filter方法还需要修改
    * 2018.4.12 - 修改完善，oh yeah!

'''

import os
import random
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


def hex2rgb(hexcolor):
    '''
    把十六进制颜色转化为RGB

    如 #6F1958,返回[111, 25, 88]

    :param hexcolor: 以#开头，例如: #6F1958
    :return: list
    '''
    hexcolor = hexcolor[1:] if '#' in hexcolor else hexcolor[:]
    hexcolor = int('0x' + hexcolor, base=16)

    rgb = [(hexcolor >> 16) & 0xff,
           (hexcolor >> 8) & 0xff,
           hexcolor & 0xff]
    return rgb

def rgb2hex(rgb):
    '''
    把RGB颜色转化为十六进制颜色
    例如：[111, 25, 88] 返回 #6F1958

    :param rgb: list
    :return: str, hex
    '''
    hexcolor = '#'
    for each in rgb:
        hex_each = hex(each)[2:].upper()
        if len(hex_each) < 2:
            hex_each += '0'
        hexcolor += hex_each
    return hexcolor

def read_csv(readpath,**kwargs):
    '''
    分块读取大文件的 csv
    :param readpath: filepath
    :return: pd.DataFrame
    '''
    print(' - - start to read - - %s'%readpath)
    reader = pd.read_csv(readpath,iterator=True,**kwargs)
    loop = True
    chunkSize = 100000
    chunks = []
    while loop:
        try:
            chunk = reader.get_chunk(chunkSize)
            chunks.append(chunk)
        except StopIteration:
            loop = False
    data = pd.concat(chunks,ignore_index=True)
    return data

def get_files(filedir, filetype='.csv', return_type='abspath'):
    '''
    返回当前目录下的所有该类型文件名或地址

    :param filedir: str,目录
    :param filetype: str,文件格式
    :param return_type: 只是文件名 或 绝对地址
    :return: list
    '''
    files = []
    for filename in os.listdir(filedir):
        if os.path.splitext(filename)[1] == filetype:
            files.append(os.path.splitext(filename)[0])
    if return_type == 'name':
        return files
    elif return_type == 'abspath':
        files = [os.path.join(dir, each + filetype) for each in files]
        return files
    return files

def get_files_all(filedir,filetype='.csv'):
    '''
    返回目录和子目录下所以该类型的文件列表
    :param filedir: str,目录
    :param filetype: str,文件格式
    :return: list
    '''
    files = []
    for each in os.walk(filedir):
        if len(each[-1]) >= 1:
            for file_i in each[-1]:
                if os.path.splitext(file_i)[1] == filetype:
                    files.append(os.path.join(each[0], file_i))
    return files

def get_subdir(sup_dir):
    sub_dirs = []
    for subdir in os.listdir(sup_dir):
        abs_path = os.path.join(sup_dir,subdir)
        if os.path.isdir(abs_path):
            sub_dirs.append(abs_path)
    return sub_dirs

def random_dataframe_sample(df, sample_num):
    '''
    返回dataframe的随机数量的样本，不放回。

    如果出现KeyError的话，把下面的 df.ix 改成 df.loc 试试 !

    :param df: Dataframe,数据
    :param sample_num: 样本数量，也可以是比例，例如 0.2
    :return: Dataframe
    '''
    length = len(df)

    if sample_num < 1:
        sample_num = int(length * sample_num)

    inds = list(df.index)
    if sample_num <= length:
        ind_sample = random.sample(inds, sample_num)
        df_sample = df.ix[ind_sample, :]
    else:
        df_sample = df
    return df_sample

def distribution_fre(data):
    '''
        计算数据的频率密度分布,最后的概率值加起来都等于1
        :param data: list 或者 pandas.Series.
        :return: pandas.Series
        '''
    if data is None:
        return None
    if not isinstance(data, pd.Series):
        data = pd.Series(data)
    data_count = data.value_counts().sort_index()
    data_p = data_count / data_count.sum()
    return data_p

def distribution_pdf(data, bins=None):
    '''
    用频率密度直方图来估计概率密度分布
    :param data: 数据
    :return: data_pdf，pandas.Series
    '''
    if data is None:
        return None
    if bins is None:
        bins = 200
    if isinstance(data,pd.Series):
        data = data.values
    density, xdata = np.histogram(data, bins=bins, density=True)
    xdata = (xdata + np.roll(xdata, -1))[:-1] / 2.0
    data_pdf = pd.Series(density, index=xdata)
    return data_pdf

def distribution_cdf(data, bins=None):
    pdf = distribution_pdf(data, bins)
    cdf = []
    for ind in pdf.index:
        cdf.append(pdf[:ind].sum())
    cdf = pd.Series(cdf, index=pdf.index)
    cdf = cdf / cdf.max()
    return cdf

def plot_distribution(data, subplot=2, data_norm=False, cmp=False, grid=True):
    '''
    :param data: Series数据
    :param subplot: 绘制原始的，log 和 log-log
    :param data_norm: 数据是否归一化，例如normlized degree
    :param cmp: 是否绘制累计密度概率
    :param grid: 网格线是否显示
    :return: None
    '''

    if data_norm:
        data_normed = normlize(data.values,0,1)
        name = 'Normlized'+ str(data.name)
        data = pd.Series(data_normed,name=name)

    ylabel = 'Prob'

    if cmp:
        data = distribution_cdf(data)
        ylabel = 'CCDF'
    else:
        data = distribution_pdf(data)

    fg = plt.figure()
    ax1 = []
    for i in range(subplot):
        ax1.append(fg.add_subplot(1,subplot,i+1))

    data.plot(ax=ax1[0], style='*-')
    ax1[0].set_title('Distribution')

    if subplot>=2:
        data.plot(ax=ax1[1], style='*', logy=True, logx=True)
        ax1[1].set_title('log-log')
        #ax1[1].set_xlim([0, 50])

    if subplot>=3:
        data.plot(ax=ax1[2], style='*-', logy=True)
        ax1[2].set_title('semi-log')

    for i in range(subplot):
        ax1[i].set_ylabel(ylabel)
        ax1[i].set_xlabel(data.name)
        ax1[i].set_xlim([0, max(data.index)*1.1])
        ax1[i].grid(grid, alpha=0.8)

def normlize(data,lower=0,upper=1):
    '''
    将数据规范化到某个区间
    :param data: 可以是list，array, ndarray等
    :param lower: 规范化的下界
    :param upper: 规范化的上界
    :return: 规范化的数据
    '''
    xmax = np.max(data)
    xmin = np.min(data)
    data_new = (upper - lower) * (data - xmin) / (xmax - xmin) + lower
    return data_new

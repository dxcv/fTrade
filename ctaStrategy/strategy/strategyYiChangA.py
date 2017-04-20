# -*- coding: utf-8 -*-
"""
Created on Thu Apr 20 16:20:17 2017

@author: freefrom

易昌A策略：
1. 日内策略
2. 统计开盘一个小时的最高和最低价格，构成一个价格区间
3. 突破最高价买开，突破最低价卖开
4. 止损止盈的幅度为开盘一个小时的价格区间
5. 收盘前3分钟清仓

"""

from ctaBase import *
from ctaTemplate import CtaTemplate

import datetime as dt


########################################################################
class YiChangAStrategy(CtaTemplate):
    """易昌A策略"""
    className = 'YiChangAStrategy'
    author = 'freefrom'

    # 策略参数
    minuteOpen  = 60    # 开盘分钟数，用于区间统计
    minuteClose = 3     # 收盘分钟数，用于清仓触发
    rangeRatio  = 1.0   # 区间比例，用于控制止盈止损幅度

    # 策略变量
    rangeHigh = EMPTY_FLOAT     # 区间最高价
    rangeLow  = EMPTY_FLOAT     # 区间最低价

    # 参数列表，保存了参数的名称
    paramList = ['name',
                 'className',
                 'author',
                 'vtSymbol',
                 'minuteOpen',
                 'minuteClose',
                 'rangeRatio']    

    # 变量列表，保存了变量的名称
    varList = ['inited',
               'trading',
               'pos',
               'rangeHigh',
               'rangeLow']  

    #----------------------------------------------------------------------
    def __init__(self, ctaEngine, setting):
        """Constructor"""
        super(YiChangAStrategy, self).__init__(ctaEngine, setting)

        # 注意策略类中的可变对象属性（通常是list和dict等），在策略初始化时需要重新创建，
        # 否则会出现多个策略实例之间数据共享的情况，有可能导致潜在的策略逻辑错误风险，
        # 策略类中的这些可变对象属性可以选择不写，全都放在__init__下面，写主要是为了阅读
        # 策略时方便（更多是个编程习惯的选择）
        self.minuteOpen  = 60    # 开盘分钟数，用于区间统计
        self.minuteClose = 3     # 收盘分钟数，用于清仓触发
        self.rangeRatio  = 1.0   # 区间比例，用于控制止盈止损幅度

    #----------------------------------------------------------------------
    def onInit(self):
        """初始化策略（必须由用户继承实现）"""
        self.writeCtaLog(u'易昌A策略初始化')
        self.putEvent()

    #----------------------------------------------------------------------
    def onStart(self):
        """启动策略（必须由用户继承实现）"""
        self.writeCtaLog(u'易昌A策略启动')
        self.putEvent()

    #----------------------------------------------------------------------
    def onStop(self):
        """停止策略（必须由用户继承实现）"""
        self.writeCtaLog(u'易昌A策略停止')
        self.putEvent()

    #----------------------------------------------------------------------
    def onTick(self, tick):
        """收到行情TICK推送（必须由用户继承实现）"""
        # 计算控制变量
        today = dt.date.today()
        openTime  = dt.datetime(today.year, today.month, today.day,  9, 0, 0, 0) # Today, 09:00:00
        closeTime = dt.datetime(today.year, today.month, today.day, 15, 0, 0, 0) # Today, 15:00:00
        openDeltaTime  = dt.timedelta(minutes=self.minuteOpen)
        closeDeltaTime = dt.timedelta(minutes=-self.minuteClose)
        rangeTime = openTime + openDeltaTime
        clearTime = closeTime + closeDeltaTime
        tickTime = tick.datetime

        # 设置订单参数
        price = tick.lastPrice
        volume = 1
        stop = True

        # 更新区间高低点 
        if tickTime < rangeTime:
            if rangeHigh == EMPTY_FLOAT or rangeHigh < tick.lastPrice:
                rangeHigh = tick.lastPrice
            if rangeLow == EMPTY_FLOAT or rangeLow > tick.lastPrice:
                rangeLow = tick.lastPrice
        # 开始交易
        elif tickTime < clearTime:
            if self.pos == 0: # 开仓
                if tick.lastPrice > rangeHigh:
                    self.sendOrder(CTAORDER_BUY, price, volume, stop)
                elif tick.lastPrice < rangeLow:
                    self.sendOrder(CTAORDER_SHORT, price, volume, stop)
            else: # 平仓
                if abs(tick.lastPrice - price) > abs(rangeHigh - rangeLow) * self.rangeRatio:
                    if self.pos < 0:
                        self.sendOrder(CTAORDER_COVER, price, volume, stop)
                    elif sel.pos > 0:
                        self.sendOrder(CTAORDER_SELL, price, volume, stop)
        # 清仓
        else:
            if self.pos < 0:
                self.sendOrder(CTAORDER_COVER, price, volume, stop)
            elif self.pos > 0:
                self.sendOrder(CTAORDER_SELL, price, volume, stop)

        # 发出状态更新事件
        self.putEvent()

    #----------------------------------------------------------------------
    def onBar(self, bar):
        """收到Bar推送（必须由用户继承实现）"""

        # 发出状态更新事件
        self.putEvent()

    #----------------------------------------------------------------------
    def onOrder(self, order):
        """收到委托变化推送（必须由用户继承实现）"""
        # 对于无需做细粒度委托控制的策略，可以忽略onOrder
        pass

    #----------------------------------------------------------------------
    def onTrade(self, trade):
        """收到成交推送（必须由用户继承实现）"""
        # 对于无需做细粒度成交控制的策略，可以忽略onTrade
        pass
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
from vtConstant import *
from ctaTemplate import CtaTemplate

import datetime as dt


########################################################################
class YiChangAStrategy(CtaTemplate):
    """易昌A策略"""
    className = 'YiChangAStrategy'
    author = 'freefrom'

    # 策略参数
    minuteOpen  = 30    # 开盘分钟数，用于区间统计
    minuteClose = 3     # 收盘分钟数，用于清仓触发
    secondCheck = 10    # 检查委托是否成交的时间限制
    rangeRatio  = 1.0   # 区间比例，用于控制止盈止损幅度

    # 策略变量
    rangeHigh = EMPTY_FLOAT     # 区间最高价
    rangeLow  = EMPTY_FLOAT     # 区间最低价
    tradeReady = False          # 是否可以交易
    orderSent = False           # 是否已经发送当前委托
    orderID = ''                # 当前委托号
    orderTime = None            # 当前委托确认成交截止时间
    orderTraded = False         # 是否当前委托已经成交
    traded = False              # 当日是否开过仓
    tradeDate = None            # 当前交易日期

    # 参数列表，保存了参数的名称
    paramList = ['name',
                 'className',
                 'author',
                 'vtSymbol',
                 'minuteOpen',
                 'minuteClose',
                 'secondCheck',
                 'rangeRatio']    

    # 变量列表，保存了变量的名称
    varList = ['inited',
               'trading',
               'pos',
               'rangeHigh',
               'rangeLow',
               'tradeReady',
               'orderSent',
               'orderID',
               'orderTime',
               'orderTraded',
               'traded',
               'tradeDate']

    #----------------------------------------------------------------------
    def __init__(self, ctaEngine, setting):
        """Constructor"""
        super(YiChangAStrategy, self).__init__(ctaEngine, setting)

        # 注意策略类中的可变对象属性（通常是list和dict等），在策略初始化时需要重新创建，
        # 否则会出现多个策略实例之间数据共享的情况，有可能导致潜在的策略逻辑错误风险，
        # 策略类中的这些可变对象属性可以选择不写，全都放在__init__下面，写主要是为了阅读
        # 策略时方便（更多是个编程习惯的选择）
        self.initParameters()
        self.initVariables()

    #----------------------------------------------------------------------
    def initParameters(self):
        """初始化策略所使用的参数"""
        self.minuteOpen  = 30    # 开盘分钟数，用于区间统计
        self.minuteClose = 3     # 收盘分钟数，用于清仓触发
        self.secondCheck = 10    # 检查委托是否成交的时间限制
        self.rangeRatio  = 1.0   # 区间比例，用于控制止盈止损幅度

    #----------------------------------------------------------------------
    def initVariables(self):
        """初始化策略所使用的变量"""
        self.rangeHigh = EMPTY_FLOAT     # 区间最高价
        self.rangeLow  = EMPTY_FLOAT     # 区间最低价
        self.tradeReady = False          # 是否可以交易
        self.initOrderVariables()        # 初始化委托相关变量
        self.traded = False              # 当日是否开过仓
        self.tradeDate = None            # 当前交易日期

    #----------------------------------------------------------------------
    def initOrderVariables(self):
        """初始化策略所使用的委托相关的变量"""
        self.orderSent = False
        self.orderID = ''
        self.orderTime = None
        self.orderTraded = False

    #----------------------------------------------------------------------
    def onInit(self):
        """初始化策略（必须由用户继承实现）"""
        self.initVariables()
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
    def checkOrderStatus(self):
        """检查当前委托是否完成"""
        if self.orderTime != None and (dt.datetime.now() < self.orderTime):
            order = self.ctaEngine.mainEngine.getOrder(self.orderID) # 查询委托对象
            if order != None: # 如果查询成功
                self.writeCtaLog(u'当前委托查询成功：%s' % self.orderID)
                orderFinished = (order.status==STATUS_ALLTRADED)
                if orderFinished: # 委托完成
                    self.orderTraded = True # 当前委托交易完成
                    self.writeCtaLog(u'当前委托已经完成：%s' % self.orderID)
                    if not self.traded: # 当日还未开过仓
                        self.traded = True # 当日已经开过仓
                        self.writeCtaLog(u'当日已经开仓交易：%s' % self.orderID)
                    self.initOrderVariables()
                else: # 委托失败，需要重新发送
                    self.writeCtaLog(u'当前委托失败，需要根据最新情况决定是否再次发送：%s' % self.orderID)
                    self.initOrderVariables()
            else:
                self.writeCtaLog(u'当前委托查询失败：%s' % self.orderID)
        else: # Time Out
            self.writeCtaLog(u'当前委托确认超时，需要根据最新情况决定是否再次发送：%s' % self.orderID)
            self.initOrderVariables()

    #----------------------------------------------------------------------
    def onTick(self, tick):
        """收到行情TICK推送（必须由用户继承实现）"""
        # 检查策略实例是否已经启动
        if not self.trading:
            return

        # 计算控制变量
        today = dt.date.today()
        if self.tradeDate != today:     # 新的一个交易日，开始初始化
            self.initVariables()
            self.writeCtaLog(u'新的交易日开始，重新初始化：%s to %s' % (str(self.tradeDate), str(today)))
            self.tradeDate = today      # 更新交易日期，确保每天初始化一次
        openTime  = dt.datetime(today.year, today.month, today.day,  9, 0, 0, 0) # Today, 09:00:00
        closeTime = dt.datetime(today.year, today.month, today.day, 15, 0, 0, 0) # Today, 15:00:00
        openDeltaTime  = dt.timedelta(minutes=self.minuteOpen)
        closeDeltaTime = dt.timedelta(minutes=-self.minuteClose)
        rangeTime = openTime + openDeltaTime
        clearTime = closeTime + closeDeltaTime
        tickTime = tick.datetime

        # 设置订单参数
        volume = 1
        stop = False

        # 查询当前委托及其成交状况
        if self.orderSent and not self.orderTraded: # 已经发送委托，但尚未确认成交
            self.checkOrderStatus()

        # 更新区间高低点
        if tickTime < openTime: # 早上开盘之前可能会收到推送的昨晚收盘价
            pass
        elif tickTime < rangeTime:
            if self.rangeHigh == EMPTY_FLOAT or self.rangeHigh < tick.lastPrice:
                self.rangeHigh = tick.lastPrice
                if self.rangeHigh == EMPTY_FLOAT:
                    self.writeCtaLog(u'价格区间上限初始化完成：%f' % self.rangeHigh)
            if self.rangeLow == EMPTY_FLOAT or self.rangeLow > tick.lastPrice:
                self.rangeLow = tick.lastPrice
                if self.rangeLow == EMPTY_FLOAT:
                    self.writeCtaLog(u'价格区间下限初始化完成：%f' % self.rangeLow)
        # 开始交易
        elif tickTime < clearTime:
            if not self.tradeReady:
                if self.rangeHigh != EMPTY_FLOAT and self.rangeLow != EMPTY_FLOAT:
                    self.tradeReady = True    # 每日价格区间的高低点都已经更新过了，才可以开始交易
                    self.writeCtaLog(u'价格区间上下限均已更新，进入交易准备完成状态')
            if self.tradeReady:
                if self.pos == 0: # 开仓
                    if tick.lastPrice > self.rangeHigh and not self.traded and not self.orderSent:
                        self.orderID = self.sendOrder(CTAORDER_BUY, tick.upperLimit, volume, stop)
                        self.orderSent = True
                        self.orderTime = dt.datetime.now() + dt.timedelta(seconds=self.secondCheck)
                        self.writeCtaLog(u'价格突破区间上限，发送买开委托：%s' % self.orderID)
                    elif tick.lastPrice < self.rangeLow and not self.traded and not self.orderSent:
                        self.orderID = self.sendOrder(CTAORDER_SHORT, tick.lowerLimit, volume, stop)
                        self.orderSent = True
                        self.orderTime = dt.datetime.now() + dt.timedelta(seconds=self.secondCheck)
                        self.writeCtaLog(u'价格突破区间下限，发送卖开委托：%s' % self.orderID)
                else: # 平仓
                    if self.pos > 0: # 买开
                        if abs(tick.lastPrice - self.rangeHigh) > abs(self.rangeHigh - self.rangeLow) * self.rangeRatio and not self.orderSent:
                            self.orderID = self.sendOrder(CTAORDER_SELL, tick.lowerLimit, volume, stop) # 卖平
                            self.orderSent = True
                            self.orderTime = dt.datetime.now() + dt.timedelta(seconds=self.secondCheck)
                            self.writeCtaLog(u'价格触及止盈止损，发送卖平委托：%s' % self.orderID)
                    if self.pos < 0: # 卖开
                        if abs(tick.lastPrice - self.rangeLow) > abs(self.rangeHigh - self.rangeLow) * self.rangeRatio and not self.orderSent:
                            self.orderID = self.sendOrder(CTAORDER_COVER, tick.upperLimit, volume, stop) # 买平
                            self.orderSent = True
                            self.orderTime = dt.datetime.now() + dt.timedelta(seconds=self.secondCheck)
                            self.writeCtaLog(u'价格触及止盈止损，发送买平委托：%s' % self.orderID)
        # 清仓
        else:
            if self.pos < 0 and not self.orderSent:
                self.orderID = self.sendOrder(CTAORDER_COVER, tick.upperLimit, volume, stop) # 买平
                self.orderSent = True
                self.orderTime = dt.datetime.now() + dt.timedelta(seconds=self.secondCheck)
                self.writeCtaLog(u'触及时间退场，发送买平委托：%s' % self.orderID)
            elif self.pos > 0 and not self.orderSent:
                self.orderID = self.sendOrder(CTAORDER_SELL, tick.lowerLimit, volume, stop) # 卖平
                self.orderSent = True
                self.orderTime = dt.datetime.now() + dt.timedelta(seconds=self.secondCheck)
                self.writeCtaLog(u'触及时间退场，发送卖平委托：%s' % self.orderID)

        # 发出状态更新事件
        self.putEvent()

    #----------------------------------------------------------------------
    def onBar(self, bar):
        """收到Bar推送（必须由用户继承实现）"""
        pass

    #----------------------------------------------------------------------
    def onOrder(self, order):
        """收到委托变化推送（必须由用户继承实现）"""
        self.writeCtaLog(u'委托状态变化，最新状态：%s, %s' % (self.orderID, order.status))

    #----------------------------------------------------------------------
    def onTrade(self, trade):
        """收到成交推送（必须由用户继承实现）"""
        self.writeCtaLog(u'委托交易完成：%s' % self.orderID)
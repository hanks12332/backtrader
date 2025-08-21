import backtrader as bt  # 导入 Backtrader
import pandas as pd # 导入 Pandas

FUNDING = True  # 是否启用资金费率

def load_data(path):
    data = pd.read_csv(path, parse_dates=['datetime']).set_index('datetime')
    return data

class PandasData_funding(bt.feeds.PandasData):
    lines = ('funding_rate', ) # 要添加的线
    # 设置 line 在数据源上的列位置
    params=(
        ('funding_rate', -1),
           )

class BuyAndHold(bt.Strategy):
    def __init__(self):
        print("--------- 打印 self 策略本身的 lines ----------")
        print(self.lines.getlinealiases())
        print("--------- 打印 self.datas 第一个数据表格的 lines ----------")
        print(self.datas[0].lines.getlinealiases())
        self.done = False  # 标记是否已经买入
        self.funding = FUNDING
        self.total_funding = 0

    def next(self):
        cash = self.broker.getcash()
        position = self.broker.getposition(self.datas[0])
        close_price = self.data.close[0]
        value = self.broker.getvalue()
        print(f"Current Time: {self.datas[0].datetime.datetime(0)}, Cash: {cash}, Close Price: {close_price}, Position Size: {position.size}, Value: {value}")
        if self.funding:
            # 获取当前的 funding_rate和持仓大小和当前的开盘价，计算实际产生的资金费率，并且展示费前和费后的价值
            funding_rate = self.datas[0].funding_rate[0]
            if funding_rate > 0:
                print(f"Current Time: {self.datas[0].datetime.datetime(0)}")
                open_price = self.data.open[0]
                print(f"Funding Rate: {funding_rate}, Position Size: {position.size}, Open Price: {open_price}")
                funding = funding_rate * position.size * open_price
                print(f"funding: {funding}")
                self.total_funding += funding
                print(f"Total Funding so far: {self.total_funding}")

        if self.done:
            return
        if cash <= 0:
            self.done = True
            print("No cash available to buy.")
            return
        size = int(cash / self.data.open[0])  # 如需支持小数仓位，改为 float(size)
        if size > 0:
            self.buy(size=size)
            # 打印买入信息和手续费
            print(f'Current Time: {self.datas[0].datetime.datetime(0)} : Buy {size} shares at {self.data.open[0]}, Commission: {self.broker.getcommissioninfo(self.data).getcommission(size=size, price=self.data.open[0])}')
        self.done = True

if __name__ == '__main__':

    data = load_data('./datas/merged_data.csv')
    #data = bt.feeds.PandasData(dataname=data, timeframe=bt.TimeFrame.Minutes, compression=60)
    data = PandasData_funding(dataname=data, timeframe=bt.TimeFrame.Minutes, compression=60)

    # 实例化 cerebro
    cerebro = bt.Cerebro()
    # 手续费
    if FUNDING:
        commission_funding = bt.ComminfoFundingRate(commission=0.0005)
        cerebro.broker.addcommissioninfo(commission_funding)
    else:
        cerebro.broker.setcommission(commission=0.0005)
    # 添加数据
    cerebro.adddata(data)
    # 设置初始资金
    cerebro.broker.setcash(100000.0)
    # 打印初始资金
    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())
    # 添加策略
    cerebro.addstrategy(BuyAndHold)
    # 启动回测
    cerebro.run()
    cerebro.addanalyzer(bt.analyzers.Returns, _name='ret')
    # 打印回测完成后的资金
    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())
    cerebro.plot(style='candlestick')

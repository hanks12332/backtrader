import backtrader as bt  # 导入 Backtrader
import pandas as pd # 导入 Pandas

def load_data(path):
    data = pd.read_csv(path, parse_dates=['datetime']).set_index('datetime')
    return data

class PrintData(bt.Strategy):
    def __init__(self):
        self.data_close = self.datas[0].close

    def next(self):
        # 打印当前时间和收盘价
        print(f'Datetime: {self.datas[0].datetime.datetime(0)}, Close: {self.data_close[0]}')

if __name__ == '__main__':

    data = load_data('./datas/merged_data.csv')
    data = bt.feeds.PandasData(dataname=data, timeframe=bt.TimeFrame.Minutes, compression=60)

    # 实例化 cerebro
    cerebro = bt.Cerebro()
    # 添加数据
    cerebro.adddata(data)
    # 设置初始资金
    cerebro.broker.setcash(100000.0)
    # 打印初始资金
    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())
    # 添加策略
    cerebro.addstrategy(PrintData)
    # 启动回测
    cerebro.run()
    # 打印回测完成后的资金
    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())

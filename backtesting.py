import math
from datetime import datetime
from copy import deepcopy

def sign(number):
    if number > 0:
        return 1
    elif number < 0:
        return -1
    return 0

class Event():

    BID, ASK, TRADE, CANDLE = ['BID', 'ASK', 'TRADE', 'CANDLE']

    def __init__(self, instrument, timestamp, type, price, quantity):
        self.instrument = instrument
        self.timestamp = timestamp
        self.type = type
        self.price = price
        self.quantity = quantity

class Order():

    id = 0

    NEW, PARTIAL, FILLED, REJECTED, CANCELED = [
        'NEW', 'PARTIAL', 'FILLED', 'REJECTED', 'CANCELED']

    @staticmethod
    def nextId():
        Order.id += 1
        return Order.id

    def __init__(self, instrument, quantity, price):
        self.id = Order.nextId()
        self.owner = 0
        self.instrument = instrument
        self.status = Order.NEW
        self.timestamp = ''
        self.quantity = quantity
        self.price = price
        self.executed = 0
        self.average = 0

    def print(self):
        return '{0} - {1} - {5}: {2}/{3}@{4}'.format(self.id, self.timestamp, self.executed, self.quantity, self.price, self.instrument)

class MarketData():

    TICK, HIST, INTR = ['TICK', 'HIST', 'INTR']

    def __init__(self):

        self.events = {}

    def loadBBGTick(self, file, instrument):

        with open(file, 'r') as file:
            data = file.read()

        events = data.split('\n')
        events = events[1:]
        for event in events:
            cols = event.split(';')
            if len(cols) == 4:
                date = datetime.strptime(cols[0], '%d/%m/%Y %H:%M:%S')
                price = float(cols[2].replace(',', '.'))
                quantity = int(cols[3])
                type = cols[1]

                if date.toordinal() not in self.events:
                    self.events[date.toordinal()] = []

                self.events[date.toordinal()].append(
                    Event(instrument, date, type, price, quantity))

    def loadYAHOOHist(self, file, instrument, type=Event.CANDLE):

        with open(file, 'r') as file:
            data = file.read()

        events = data.split('\n')
        events = events[1:]
        for event in events:
            cols = event.split(',')
            if len(cols) == 7 and cols[1] != 'null':

                date = datetime.strptime(cols[0], '%Y-%m-%d')
                price = (float(cols[1]), float(cols[2]),
                         float(cols[3]), float(cols[5]))
                #quantity = int(cols[6])
                quantity = 0

                if date.toordinal() not in self.events:
                    self.events[date.toordinal()] = []

                self.events[date.toordinal()].append(
                    Event(instrument, date, type, price, quantity))

    def loadBBGIntr(self, file, instrument, type=Event.CANDLE):

        with open(file, 'r') as file:
            data = file.read()

        events = data.split('\n')
        events = events[1:]
        for event in events:
            cols = event.split(';')
            if len(cols) == 5:

                date = datetime.strptime(cols[0], '%d/%m/%Y %H:%M:%S')
                price = (float(cols[1].replace(',', '.')),
                         float(cols[3].replace(',', '.')),
                         float(cols[4].replace(',', '.')),
                         float(cols[2].replace(',', '.')))
                quantity = 0

                if date.timestamp() not in self.events:
                    self.events[date.timestamp()] = []

                self.events[date.timestamp()].append(
                    Event(instrument, date, type, price, quantity))

    def run(self, ts):
        dates = list(self.events.keys())
        dates.sort()
        for date in dates:
            for event in self.events[date]:
                ts.inject(event)

class Strategy():

    id = 0

    @staticmethod
    def nextId():
        Strategy.id += 1
        return Strategy.id

    def __init__(self):
        pass

    def clear(self):
        self._id = Strategy.nextId()

        self._position = {}
        self._last = {}

        self._legs = []

        self._result = {}
        self._notional = {}

        self._orders = []
        #self.prices = []

    def cancel(self, owner, id):
        pass

    def submit(self, id, orders):
        pass

    def event(self, event):

        self._last[event.instrument] = event.price
        #self.prices.append(event.price[3])
        return self.push(event)

    def push(self, event):
        pass

    def fill(self, id, instrument, price, quantity, status):

        if price != 0:

            if instrument not in self._position:
                self._position[instrument] = 0

            if instrument not in self._result:
                self._result[instrument] = 0

            if instrument not in self._notional:
                self._notional[instrument] = 0

            self._position[instrument] += quantity
            self._result[instrument] -= quantity*price

            if quantity > 0:
                self._notional[instrument] += quantity*price
            else:
                self._notional[instrument] -= quantity*price

            if self.zeroed():
                self._legs.append((self.totalResult(), self.totalNotional()))

    def zeroed(self):
        for position in self._position.values():
            if position != 0:
                return False
        return True

    def close(self):

        orders = []
        for instrument, position in self._position.items():
            if position != 0:
                orders.append(Order(instrument, -position, 0))

        return orders

    def partialResult(self):
        res = {}
        for instrument, result in self._result.items():
            res[instrument] = result + \
                self._position[instrument]*self._last[instrument]
        return res

    def totalNotional(self):
        res = 0
        for notional in self._notional.values():
            res += notional
        return res

    def totalResult(self):
        res = 0
        for result in self._result.values():
            res += result
        return res

    def summary(self, tax=0.00024, fee=0):

        # Number of trades
        nt = len(self._legs)

        # Hitting ratio
        hr = 0

        # P&L
        pnl = 0

        # Accumulated Return
        ret = 0

        net = 0
        avg = 0
        mp = -float("inf")
        md = float("inf")
        amo = 0
        if nt > 0:
            pnl = self._legs[-1][0]

            amo = self._legs[-1][1]
            ret = pnl / (amo/2)

            if pnl > 0:
                hr += 1

            mp = self._legs[0][0]
            md = self._legs[0][0]

            avg = self._legs[0][0]/(self._legs[0][1]/2)

            i = 1
            while i < len(self._legs):
                res = self._legs[i][0]-self._legs[i-1][0]
                amo = (self._legs[i][1]-self._legs[i-1][1])/2
                avg += res/amo

                if res > mp:
                    mp = res
                if res < md:
                    md = res

                if res > 0:
                    hr += 1

                i += 1

            avg = avg/nt
            hr = hr/nt

        res = ''
        res += 'Number of trades: {0}\n'.format(nt)
        res += 'Gross P&L: {0:.2f}\n'.format(pnl)
        res += 'Gross Accumulated return: {0:.2f}%\n'.format(100 * ret)
        res += 'Gross Average Return: {0:.2f}%\n'.format(100 * avg)

        net = pnl - amo * tax - nt * fee
        res += 'Net P&L: {0:.2f}\n'.format(net)

        res += 'Hitting ratio: {0:.2f}%\n'.format(100*hr)
        #res += 'Max Profit: {0:.2f}\n'.format(mp)
        #res += 'Max Drawdown: {0:.2f}\n'.format(md)

        return res

class Book():

    def __init__(self, instrument, fill):

        self.instrument = instrument
        self.fill = fill

        # market data
        self.bid = None
        self.ask = None
        self.trade = None
        self.timestamp = None

        self.orders = []

    def inject(self, event):
        if event.instrument == self.instrument:
            self.timestamp = event.timestamp

            if event.type == Event.CANDLE:
                event.price = event.price[3]

            if event.type == Event.BID or event.type == Event.CANDLE:
                self.bid = event
                for order in self.orders:
                    if order.quantity < 0:
                        if order.price <= event.price:
                            rem = order.quantity - order.executed

                            if event.quantity == 0:
                                qty = rem
                            else:
                                qty = max(rem, -event.quantity)

                            average = order.average * order.executed + qty * event.price

                            order.executed += qty
                            order.average = average / order.executed

                            if order.quantity == order.executed:
                                order.status = Order.FILLED

                            self.fill(order.id, event.price, qty, order.status)

            if event.type == Event.ASK or event.type == Event.CANDLE:
                self.ask = event
                for order in self.orders:
                    if order.quantity > 0:
                        if order.price >= event.price:
                            rem = order.quantity - order.executed

                            if event.quantity == 0:
                                qty = rem
                            else:
                                qty = min(rem, event.quantity)

                            average = order.average * order.executed + qty * event.price

                            order.executed += qty
                            order.average = average / order.executed

                            if order.quantity == order.executed:
                                order.status = Order.FILLED

                            self.fill(order.id, event.price, qty, order.status)

            if event.type == Event.TRADE:
                self.trade = event
                for order in self.orders:
                    if order.quantity > 0 and order.price >= event.price:
                        rem = order.quantity - order.executed

                        if event.quantity == 0:
                            qty = rem
                        else:
                            qty = min(rem, event.quantity)

                        average = order.average * order.executed + qty * event.price

                        order.executed += qty
                        order.average = average / order.executed

                        if order.quantity == order.executed:
                            order.status = Order.FILLED

                        self.fill(order.id, event.price, qty, order.status)

                    if order.quantity < 0 and order.price <= event.price:
                        rem = order.quantity - order.executed

                        if event.quantity == 0:
                            qty = rem
                        else:
                            qty = max(rem, -event.quantity)

                        average = order.average * order.executed + qty * event.price

                        order.executed += qty
                        order.average = average / order.executed

                        if order.quantity == order.executed:
                            order.status = Order.FILLED

                        self.fill(order.id, event.price, qty, order.status)

            i = 0
            while i < len(self.orders):
                if self.orders[i].status == Order.FILLED:
                    del self.orders[i]
                else:
                    i += 1

    def submit(self, order):
        if order is not None:
            if order.price == 0:  # MKT
                if order.quantity > 0:
                    if self.ask.quantity == 0:
                        order.executed = order.quantity
                    else:
                        order.executed = min(
                            [self.ask.quantity, order.quantity])

                    order.average = self.ask.price
                    order.status = Order.FILLED

                    self.fill(order.id, order.average,
                              order.executed, order.status)

                elif order.quantity < 0:
                    if self.bid.quantity == 0:
                        order.executed = order.quantity
                    else:
                        order.executed = max(
                            [-self.bid.quantity, order.quantity])

                    order.average = self.bid.price
                    order.status = Order.FILLED

                    self.fill(order.id, order.average,
                              order.executed, order.status)

            else:  # LMT order
                if self.ask is not None and order.quantity > 0 and order.price >= self.ask.price:
                    if self.ask.quantity == 0:
                        order.executed = order.quantity
                        order.average = self.ask.price
                        order.status = Order.FILLED
                    else:
                        order.executed = min(
                            [self.ask.quantity, order.quantity])
                        order.average = self.ask.price
                        if order.executed == order.quantity:
                            order.status = Order.FILLED
                        else:
                            order.status = Order.PARTIAL
                            self.orders.append(order)
                    self.fill(order.id, order.average,
                              order.executed, order.status)
                elif self.bid is not None and order.quantity < 0 and order.price <= self.bid.price:
                    if self.bid.quantity == 0:
                        order.executed = order.quantity
                        order.average = self.bid.price
                        order.status = Order.FILLED
                    else:
                        order.executed = max(
                            [-self.bid.quantity, order.quantity])
                        order.average = self.bid.price
                        if order.executed == order.quantity:
                            order.status = Order.FILLED
                        else:
                            order.status = Order.PARTIAL
                            self.orders.append(order)
                    self.fill(order.id, order.average,
                              order.executed, order.status)
                elif order.quantity != 0:
                    self.orders.append(order)

    def cancel(self, id):
        i = 0
        while i < len(self.orders):
            if self.orders[i].id == id:
                order = self.orders[i]
                del self.orders[i]
                order.status = Order.CANCELED
                self.fill(order.id, 0, 0, order.status)
                i = len(self.orders)
            else:
                i += 1

class TradingSystem():

    def __init__(self):
        self.books = {}
        self.position = {}
        self.orders = {}
        self.listeners = {}
        self.strategies = {}

    def createBook(self, instrument):
        if instrument not in self.books:
            self.books[instrument] = Book(instrument, self.fill)

        if instrument not in self.position:
            self.position[instrument] = {}

        if instrument not in self.listeners:
            self.listeners[instrument] = []

    def inject(self, event):
        instrument = event.instrument
        if instrument in self.books:
            self.books[instrument].inject(deepcopy(event))

            for id in self.listeners[instrument]:
                if id in self.strategies:
                    self.submit(id, self.strategies[id].event(event))

    def subscribe(self, instrument, strategy):
        if strategy._id not in self.strategies:
            self.strategies[strategy._id] = strategy
            strategy.cancel = self.cancel
            strategy.submit = self.submit

        if instrument in self.books:
            if strategy._id not in self.position[instrument]:
                self.position[instrument][strategy._id] = 0

            if strategy._id not in self.listeners[instrument]:
                self.listeners[instrument].append(strategy._id)

    def submit(self, id, orders):
        if orders is None:
            orders = []

        for order in orders:

            order.owner = id
            instrument = order.instrument

            if instrument in self.position:
                if id in self.position[instrument]:
                    position = self.position[instrument][id]

            if sign(position) * sign(position + order.quantity) == -1:
                order.status = Order.REJECTED
                if id in self.strategies:
                    strategy = self.strategies[id]
                    strategy.fill(order.id, instrument, 0, 0, order.status)
            else:
                if order.id not in self.orders:
                    self.orders[order.id] = order

                if instrument in self.books:
                    self.books[instrument].submit(order)

    def cancel(self, owner, id):
        if id in self.orders:
            if self.orders[id].owner == owner:
                instrument = self.orders[id].instrument
                if instrument in self.books:
                    self.books[instrument].cancel(id)

    def fill(self, id, price, quantity, status):

        if id in self.orders:

            order = self.orders[id]
            instrument = order.instrument
            owner = order.owner

            if instrument in self.position:
                if owner in self.position[instrument]:
                    self.position[instrument][owner] += quantity

            if owner in self.strategies:
                strategy = self.strategies[owner]
                strategy.fill(id, instrument, price, quantity, status)

def evaluate(strategy, type, files):
    strategy.clear()
    data = MarketData()

    ts = TradingSystem()

    for instrument, file in files.items():
        ts.createBook(instrument)
        ts.subscribe(instrument, strategy)
        if file != '':
            if type == MarketData.TICK:
                data.loadBBGTick(file, instrument)
            elif type == MarketData.HIST:
                data.loadYAHOOHist(file, instrument)
            elif type == MarketData.INTR:
                data.loadBBGIntr(file, instrument)

    data.run(ts)

    ts.submit(strategy.id, strategy.close())
    return strategy.summary()


def evaluateTick(strategy, files):
    return evaluate(strategy, MarketData.TICK, files)


def evaluateHist(strategy, files):
    return evaluate(strategy, MarketData.HIST, files)


def evaluateIntr(strategy, files):
    return evaluate(strategy, MarketData.INTR, files)

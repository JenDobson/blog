from sqlalchemy import Column, ForeignKey, Integer
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy import create_engine

Base = declarative_base()

'''
Demonstrate the basic relationship structure.
No inheritance: Start with separate BuyTransaction and SellTransaction class.
Lots are not automatically created when BuyTransaction is created.
'''

class BuyTransaction(Base):
    __tablename__ = 'buy_transaction'

    buy_transaction_id = Column(Integer, primary_key=True)
    purchased_lot = relationship("Lot",back_populates='buy_transaction',
                                 uselist=False)
class SellTransaction(Base):
    __tablename__ = 'sell_transaction'

    sell_transaction_id = Column(Integer, primary_key=True)
    sold_lot = relationship("Lot",back_populates='sell_transaction',
                                 uselist=False)

''' Lot is like an edge connecting two transactions'''
class Lot(Base):
    __tablename__ = 'lot'

    # Each lot has one non-null buy transaction and zero or one sell transactions
    # primary key of lot is the buy_transaction_id since the lot uniquely maps onto the BuyTransaction.  
    # (SellTransaction is unique or None, so don't use as primary key.)

    buy_transaction_id = Column(Integer,
                                ForeignKey('buy_transaction.buy_transaction_id'),
                                primary_key=True)

    sell_transaction_id = Column(Integer,
                                 ForeignKey('sell_transaction.sell_transaction_id'))

    buy_transaction = relationship(BuyTransaction,
                                   back_populates='purchased_lot')
    sell_transaction = relationship(SellTransaction,
                                    back_populates='sold_lot')

    def __repr__(self):
        return "<Lot(buy_transaction={buy},sell_transaction={sell}>".format(
            buy=self.buy_transaction,sell=self.sell_transaction)



engine = create_engine('sqlite+pysqlite:///:memory:')
Base.metadata.create_all(engine)

b = BuyTransaction()
s = SellTransaction()
l = Lot()

l.buy_transaction = b
l.sell_transaction = s

print('\n\nb: ',b,'\n')
print('s: ',s,'\n')
print('l: ',l,'\n')

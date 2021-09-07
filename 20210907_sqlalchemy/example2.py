from sqlalchemy import Column, ForeignKey, Integer
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from sqlalchemy import create_engine
from sqlalchemy import event

Base = declarative_base()

'''
Now, make it a little more interesting by creating the lot when a BuyTransaction is created.  
'''

class BuyTransaction(Base):
    __tablename__ = 'buy_transaction'

    buy_transaction_id = Column(Integer, primary_key=True)
    purchased_lot = relationship("Lot",back_populates='buy_transaction',
                                 uselist=False)

@event.listens_for(BuyTransaction, "after_insert")
def after_insert(mapper,connection,instance):
    connection.execute(instance.metadata.tables['lot'].insert(),
                       {"buy_transaction_id":instance.buy_transaction_id})

class SellTransaction(Base):
    __tablename__ = 'sell_transaction'

    sell_transaction_id = Column(Integer, primary_key=True)
    sold_lot = relationship("Lot",back_populates='sell_transaction',
                                 uselist=False)

''' Lot is like an edge connecting two transactions'''
class Lot(Base):
    __tablename__ = 'lot'

    # Each lot has one non-null buy transaction and zero or one sell transactions
    # Creation of a buy transaction should create a lot
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



engine = create_engine('sqlite+pysqlite:///:memory:',future=True)
Base.metadata.create_all(engine)
DBSession = sessionmaker(bind=engine)
session=DBSession()

b = BuyTransaction()
s = SellTransaction()
l = b.purchased_lot

print('\n\nb: ',b,'\n')
print('s: ',s,'\n')
print('l: ',l,'\n')

print('\n==================ADDING AND COMMITTING TO DATABASE===============\n')
session.add_all([b,s])
session.commit()

l = b.purchased_lot

print('l: ',l,'\n')



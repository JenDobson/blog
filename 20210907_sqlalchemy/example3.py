from sqlalchemy import Column, ForeignKey, Integer, Date
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from sqlalchemy import create_engine
from sqlalchemy import event
from sqlalchemy import select, update 

Base = declarative_base()

'''
Now, when we create a SellTransaction, find the first Lot with no buy transaction 
and point the lot's sell_transaction to this newly created SellTransaction.  
Also add 'transaction_date' field to BuyTransaction so that we can sort the 
Lots in order when attaching the SellTransaction.
Note we need to use after_insert so that IDs are assigned before we update Lot.
'''

class BuyTransaction(Base):
    __tablename__ = 'buy_transaction'

    transaction_date = Column(Date,nullable=False)
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
    
@event.listens_for(SellTransaction, "after_insert")
def after_insert(mapper,connection,instance):
    # Find the earliest Lot with no SellTransaction
    tables = instance.metadata.tables
    lot_table = tables['lot']
    buy_transaction_table = tables['buy_transaction']
    qstmt = select(lot_table.c.buy_transaction_id). \
            where(lot_table.c.sell_transaction_id == None). \
            join_from(lot_table,buy_transaction_table). \
            order_by(buy_transaction_table.c.transaction_date) 
 
    res = connection.execute(qstmt).first()
    update_stmt = update(lot_table).where(lot_table.c.buy_transaction_id == res[0]). \
            values(sell_transaction_id=instance.sell_transaction_id)
    connection.execute(update_stmt)

class Lot(Base):
    __tablename__ = 'lot'

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
DBSession = sessionmaker(bind=engine)
session = DBSession()

import datetime
b = BuyTransaction(transaction_date=datetime.date(2021,9,1))
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

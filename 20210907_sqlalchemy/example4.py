from sqlalchemy import Column, ForeignKey, Integer, Date, String
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from sqlalchemy import create_engine
from sqlalchemy import event
from sqlalchemy import select, update 

Base = declarative_base()

'''
Last step:  buy transaction and sell transaction are subclasses of transaction. i

Use Single Table Inheritance pattern (https://docs.sqlalchemy.org/en/14/orm/inheritance.html?highlight=single%20table%20inheritance#single-table-inheritance)
'''

class Transaction(Base):
    __tablename__ = 'transaction'
    
    transaction_id = Column(Integer, primary_key=True)
    date = Column(Date,nullable=False)
    type = Column(String(20))

    # 
    __mapper_args__ = {
        'polymorphic_on':type
    }

class BuyTransaction(Transaction):

    purchased_lot = relationship("Lot",back_populates='buy_transaction',
                                 foreign_keys='lot.c.buy_transaction_id',
                                 uselist=False)

    __mapper_args__ = {
        'polymorphic_identity': 'buy_transaction'
    }

@event.listens_for(BuyTransaction, "after_insert")
def after_insert(mapper,connection,instance):
    connection.execute(instance.metadata.tables['lot'].insert(),
                       {"buy_transaction_id":instance.transaction_id})

class SellTransaction(Transaction):
    
    sold_lot = relationship("Lot",back_populates='sell_transaction',
                            foreign_keys='lot.c.sell_transaction_id',
                            uselist=False)
    
    __mapper_args__ = {
        'polymorphic_identity': 'sell_transaction'
    }

@event.listens_for(SellTransaction, "after_insert")
def after_insert(mapper,connection,instance):
    # Find the earliest Lot with no SellTransaction
    tables = instance.metadata.tables
    lot_table = tables['lot']
    transaction_table = tables['transaction']
    
    '''
    sqlalchemy.exc.AmbiguousForeignKeysError: Can't determine join between 'lot' and 'transaction'; tables have more than one foreign key constraint relationship between them. Please specify the 'onclause' of this join explicitly.
    '''

    qstmt = select(lot_table.c.buy_transaction_id). \
            where(lot_table.c.sell_transaction_id == None). \
            join_from(lot_table,transaction_table,
                      onclause=lot_table.c.buy_transaction_id==transaction_table.c.transaction_id). \
            order_by(transaction_table.c.date) 
    res = connection.execute(qstmt).first()
    update_stmt = update(lot_table).where(lot_table.c.buy_transaction_id == res[0]). \
            values(sell_transaction_id=instance.transaction_id)
    connection.execute(update_stmt)

''' Lot is like an edge connecting two transactions'''
class Lot(Base):
    __tablename__ = 'lot'

    # Each lot has one non-null buy transaction and zero or one sell transactions
    # Creation of a buy transaction should create a lot
    buy_transaction_id = Column(Integer,
                                ForeignKey('transaction.transaction_id'),
                                primary_key=True)

    sell_transaction_id = Column(Integer,
                                 ForeignKey('transaction.transaction_id'))



    buy_transaction = relationship(BuyTransaction,
                                   back_populates='purchased_lot',
                                  foreign_keys=buy_transaction_id)
    sell_transaction = relationship(SellTransaction,
                                    back_populates='sold_lot',
                                   foreign_keys=sell_transaction_id)

    def __repr__(self):
        return "<Lot(buy_transaction={buy},sell_transaction={sell}>".format(
            buy=self.buy_transaction,sell=self.sell_transaction)



engine = create_engine('sqlite+pysqlite:///:memory:')
Base.metadata.create_all(engine)
DBSession = sessionmaker(bind=engine)
session = DBSession()

import datetime
b = BuyTransaction(date=datetime.date(2021,9,1))
s = SellTransaction(date=datetime.date(2021,9,8))
l = b.purchased_lot

print('\n\nb: ',b,'\n')
print('s: ',s,'\n')
print('l: ',l,'\n')

print('\n==================ADDING AND COMMITTING TO DATABASE===============\n')
session.add_all([b,s])
session.commit()

l = b.purchased_lot

print('l: ',l,'\n')

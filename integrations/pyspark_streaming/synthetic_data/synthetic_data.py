from faker import Faker
import numpy as np
import pandas as pd
import datetime
import random
import bisect
from dataclasses import dataclass
from typing import List
import hashlib

@dataclass
class transaction_probablity:
    min_value : float
    max_value : float
    probablity : float

@dataclass
class categories_price_probality:
    category : str
    min_price : float
    max_price : float
    probablity : float

@dataclass
class transaction_price_distribution:
    price_dist : List[transaction_probablity]
    
@dataclass
class categories_price_distribution:
    category_dist : List[categories_price_probality]

class synthetic_data:
    def __init__(self, total_unique_users : int = 100, 
                 total_unique_transactions : int = 54000, 
                 cash_withrawal_cards_cards_total : int = 2000, 
                 total_unique_cash_withdrawals : int = 1200, 
                 fraud_ratio : int = 0.0025,
                 atm_withrawal_seq_length : list = [3, 4, 5, 6, 7, 8, 9, 10], 
                 attack_chain_length = [3, 4, 5, 6, 7, 8, 9, 10],
                 normal_atm_radius : float = 0.01,
                 transaction_distribution : transaction_price_distribution = transaction_price_distribution(price_dist=[transaction_probablity(min_value=0.01, max_value=1.01, probablity=0.05),
                                                                                                            transaction_probablity(min_value=1, max_value=11.01, probablity=0.075),
                                                                                                            transaction_probablity(min_value=10, max_value=100.01, probablity=0.525),
                                                                                                            transaction_probablity(min_value=100, max_value=1000.01, probablity=0.25),
                                                                                                            transaction_probablity(min_value=1000, max_value=10000.01, probablity=0.099),
                                                                                                            transaction_probablity(min_value=10000, max_value=30000.01, probablity=0.001),]),
                categories_distribution : categories_price_distribution = categories_price_distribution(category_dist=[categories_price_probality(category="Grocery", min_price=0.01, max_price=100, probablity=0.5),
                                                                                                                        categories_price_probality(category="Restaurant/Cafeteria", min_price=1, max_price=100, probablity=0.2),
                                                                                                                        categories_price_probality(category="Health/Beauty", min_price=10, max_price=500.01, probablity=0.1),
                                                                                                                        categories_price_probality(category="Domestic Transport", min_price=10, max_price=100.01, probablity=0.1),
                                                                                                                        categories_price_probality(category="Clothing", min_price=10, max_price=2000.01, probablity=0.05),
                                                                                                                        categories_price_probality(category="Electronics", min_price=100, max_price=10000.01, probablity=0.02),
                                                                                                                        categories_price_probality(category="Sports/Outdoors", min_price=10, max_price=100.01, probablity=0.015),
                                                                                                                        categories_price_probality(category="Holliday/Travel", min_price=10, max_price=100.01, probablity=0.014),
                                                                                                                        categories_price_probality(category="Jewelery", min_price=10, max_price=100.01, probablity=0.001),                                            
                                                                                                                        ])):
        
        # Setting up parameter for simulated data generation
        self.TOTAL_UNIQUE_USERS = total_unique_users
        self.TOTAL_UNIQUE_TRANSACTIONS = total_unique_transactions
        self.TOTAL_CASH_WITHRAWALS = cash_withrawal_cards_cards_total
        self.TOTAL_UNIQUE_CASH_WITHDRAWALS = total_unique_cash_withdrawals
        self.ATM_WITHRAWAL_SEQ_LENGTH = atm_withrawal_seq_length
        self.NORMAL_ATM_RADIUS = normal_atm_radius
        self.AMOUNT_DISTRIBUTION_PERCENTAGES = transaction_distribution
        self.CATEGORY_PERC_PRICE = categories_distribution
        self.NUMBER_OF_FRAUDULENT_TRANSACTIONS = self.TOTAL_UNIQUE_TRANSACTIONS * fraud_ratio
        self.ATTACK_CHAIN_LENGTHS = attack_chain_length
        self.NUMBER_OF_FRAUDULENT_ATM_TRANSACTIONS = self.TOTAL_CASH_WITHRAWALS * fraud_ratio

        self.DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
        self.END_DATE = datetime.datetime.now().strftime(self.DATE_FORMAT)
        self.START_DATE = (datetime.datetime.now() - datetime.timedelta(days=30 * 6)).strftime(self.DATE_FORMAT)

        # Setting up faker
        self.faker = Faker()

        # TODO : Make setting seeds a funcion and create a parameter for it
        self.faker.seed_locale('en_US', 0)
        seed = 12345
        random.seed(seed)
        np.random.seed(seed)
        self.faker.seed_instance(seed)



        

    def generate_list_credit_cards(self) -> pd.DataFrame:
        """ Function that generates and returns a dataframe of credit card numbers
        """
        credit_cards = []
        delta_time_object = datetime.datetime.strptime(self.START_DATE, self.DATE_FORMAT)

        # Generating credit card number, expiry date using faker
        for _ in range(self.TOTAL_UNIQUE_USERS):
            address = self.faker.local_latlng(country_code='US')
            age = 0
            profile = None
            while age < 18 or age > 100:
                profile = self.faker.profile(fields=['name', 'mail', 'birthdate'])
                bday = profile['birthdate']
                delta = datetime.datetime.now() - datetime.datetime(bday.year, bday.month, bday.day)
                age = int(delta.days / 365)

            credit_cards.append({'cc_num': self.faker.credit_card_number(card_type='visa'), 
                                 'cc_provider': random.choice(['visa', 'mastercard']),
                                 'cc_type' : random.choice(["credit", "debit"]),
                                 'cc_expiration_date': self.faker.credit_card_expire(start=delta_time_object, end="+5y",date_format="%m/%y"),
                                 'name' : profile["name"],
                                 'mail' : profile["name"],
                                 'birthdate' : profile["birthdate"],
                                 'age' : age,
                                 'city' : address[2],
                                 'country_of_residence' : address[3]})
        return pd.DataFrame(credit_cards)
    
    def generate_transaction_amounts(self, number_of_transactions : int) -> list:
        """Function that returns all a simulated list of transaction amounts based on the transaction probablity distributions
        """
        amounts = []
        for price_dist in self.AMOUNT_DISTRIBUTION_PERCENTAGES.price_dist:
            n = int(number_of_transactions * price_dist.probablity)
            start, end = price_dist.min_value, price_dist.max_value
            for _ in range(n):
                amounts.append(round(np.random.uniform(start, end + 1),2))
        return amounts
    
    def create_transaction(self, timestamp, credit_card_number, category, amount, latitude, longitude, city, country, fraud_label):
        transaction_id = self.generate_transaction_id(timestamp, credit_card_number, category)
        return {'tid': transaction_id,
                'datetime': timestamp.strftime(self.DATE_FORMAT),
                'cc_num': credit_card_number,
                'category': category,
                'amount': amount,
                'latitude': latitude,
                'longitude': longitude,
                'city': city,
                'country': country,
                'fraud_label': fraud_label}
    
    def generate_card_transactions(self, card_amounts, credit_card_numbers) -> list:
        categories = []
        transaction_data_start = datetime.datetime.strptime(self.START_DATE, self.DATE_FORMAT)
        transaction_data_end = datetime.datetime.strptime(self.END_DATE, self.DATE_FORMAT)
        total_transactions = len(card_amounts)

        # Catgeories for Card transactions
        for category_dist in self.CATEGORY_PERC_PRICE.category_dist:
            n = round(total_transactions * category_dist.probablity)
            for _ in range(n):
                credit_card_number = random.choice(credit_card_numbers)
                point_of_tr = self.faker.local_latlng(country_code="US")
                timestamp = self.faker.date_time_between(start_date=transaction_data_start, end_date=transaction_data_end, tzinfo=None)
                min_price_i = bisect.bisect_left(card_amounts, category_dist.min_price)
                max_price_i = bisect.bisect_right(card_amounts, category_dist.max_price, lo=min_price_i)

                transaction = self.create_transaction(timestamp=timestamp, 
                                                      credit_card_number=credit_card_number, 
                                                      category=category_dist.category, 
                                                      amount=random.choice(card_amounts[min_price_i:max_price_i]), 
                                                      latitude=point_of_tr[0], 
                                                      longitude=point_of_tr[1], 
                                                      city=point_of_tr[2], 
                                                      country=point_of_tr[3], 
                                                      fraud_label=0)
                categories.append(transaction)
        random.shuffle(categories)
        return categories

    def generate_atm_withdrawal(self, withdrawal_amounts, credit_card_numbers):

        transaction_data_start = datetime.datetime.strptime(self.START_DATE, self.DATE_FORMAT)
        transaction_data_end = datetime.datetime.strptime(self.END_DATE, self.DATE_FORMAT)
        
        cash_withdrawals = []
        atm_count = 0
        while atm_count < self.TOTAL_UNIQUE_CASH_WITHDRAWALS:
            for ATM_WITHRAWAL_SEQ in self.ATM_WITHRAWAL_SEQ_LENGTH:
                # interval in hours between normal cash withdrawals
                delta = random.randint(6, 168)
                credit_card_number = random.choice(credit_card_numbers)
                point_of_tr = self.faker.local_latlng(country_code="US")
                withdrawal_timestamp = self.faker.date_time_between(start_date=transaction_data_start, end_date=transaction_data_end, tzinfo=None)
                
                # Generating sequence of transactions using the generated data
                for _ in range(ATM_WITHRAWAL_SEQ):
                    withdrawal_timestamp =  withdrawal_timestamp - datetime.timedelta(hours=delta)
                    transaction = self.create_transaction(timestamp=withdrawal_timestamp, 
                                                      credit_card_number=credit_card_number, 
                                                      category="Cash Withdrawal", 
                                                      amount=random.choice(withdrawal_amounts), 
                                                      latitude=self.faker.coordinate(point_of_tr[0], self.NORMAL_ATM_RADIUS), # updating latitude for sequence of transactions
                                                      longitude=self.faker.coordinate(point_of_tr[1], self.NORMAL_ATM_RADIUS), # updating longitude for sequence of transactions
                                                      city=point_of_tr[2], 
                                                      country=point_of_tr[3], 
                                                      fraud_label=0)
                    cash_withdrawals.append(transaction)
                atm_count+=ATM_WITHRAWAL_SEQ
        return cash_withdrawals

    def generate_transaction_id(self, timestamp: str, credit_card_number: str, transaction_amount: float) -> str:
        """."""
        hashable = f'{timestamp}{credit_card_number}{transaction_amount}'
        hexdigest = hashlib.md5(hashable.encode('utf-8')).hexdigest()
        return hexdigest

    def create_transactions_data(self, credit_card_numbers):
        # Schema transaction dataframe - tid, datetime,	cc_num,	category, amount, latitude,	longitude, city, country

        # Creating transaction amounts
        card_transactions_amounts = self.generate_transaction_amounts(self.TOTAL_UNIQUE_TRANSACTIONS)
        cash_withdrawal_amounts = self.generate_transaction_amounts(self.TOTAL_UNIQUE_CASH_WITHDRAWALS)
        
        # Creating corresponding transaction categories
        card_transactions = self.generate_card_transactions(card_transactions_amounts, credit_card_numbers)
        atm_transactions = self.generate_atm_withdrawal(cash_withdrawal_amounts, credit_card_numbers)

        # Creating fraud transactions
        fraud_card_transactions = self.create_fraud_card_transactions(card_transactions)
        fraud_atm_transactions = self.create_atm_fraud_transactions(atm_transactions)

        transactions_dataframe = pd.DataFrame(card_transactions + atm_transactions + fraud_card_transactions + fraud_atm_transactions)

        return transactions_dataframe

    def create_fraud_card_transactions(self, card_transactions):
        # Create frauds labels for normal transactions using attack chains, attack happens when multiple transactions happen in very close timeperiods
        # for different categories of data 

        # Creating attack chains -> selecting card for which fraud happens and adding fraud transactions for it
        tot_fraud_tractions = 0
        fraud_transactions = []

        transaction_data_start = datetime.datetime.strptime(self.START_DATE, self.DATE_FORMAT)
        transaction_data_end = datetime.datetime.strptime(self.END_DATE, self.DATE_FORMAT)

        while tot_fraud_tractions < self.NUMBER_OF_FRAUDULENT_TRANSACTIONS:
            selected_target_transaction = random.choice(card_transactions)
            attack_chain_length = random.choice(self.ATTACK_CHAIN_LENGTHS)
            
            attack_amounts = self.generate_transaction_amounts(attack_chain_length)
            attack_transactions = self.generate_card_transactions(attack_amounts, [selected_target_transaction["cc_num"]])
            timestamp = self.faker.date_time_between(start_date=transaction_data_start, end_date=transaction_data_end, tzinfo=None)

            for i in range(len(attack_transactions)):
                # interval in seconds between fraudulent attacks
                delta = random.randint(30, 120)
                attack_transactions[i]["datetime"] = (timestamp + datetime.timedelta(seconds=delta)).strftime(self.DATE_FORMAT)
                attack_transactions[i]["fraud_label"] = 1
                fraud_transactions.append(attack_transactions[i])
                tot_fraud_tractions+=1

                if(tot_fraud_tractions == self.NUMBER_OF_FRAUDULENT_TRANSACTIONS):
                    break
        
        return fraud_transactions
    

    def create_atm_fraud_transactions(self, atm_transactions):
        # Fraud ATM transactions are transactions that are out if US in a sequence of ATM transactions and been done in quick sequence
        fraud_atm_transactions = []
        tot_fraud_tractions = 0

        attack_amounts = self.generate_transaction_amounts(self.NUMBER_OF_FRAUDULENT_ATM_TRANSACTIONS)

        while tot_fraud_tractions < self.NUMBER_OF_FRAUDULENT_ATM_TRANSACTIONS:
            selected_target_transaction = random.choice(atm_transactions)
            delta = random.randint(1, 5)
            fraudulent_atm_location = self.faker.location_on_land()
            while fraudulent_atm_location[3] == 'US':
                fraudulent_atm_location = self.faker.location_on_land()
            withdrawal_timestamp = datetime.datetime.strptime(selected_target_transaction["datetime"], self.DATE_FORMAT) + datetime.timedelta(delta)
            transaction = self.create_transaction(timestamp=withdrawal_timestamp, 
                                                      credit_card_number=selected_target_transaction["cc_num"], 
                                                      category="Cash Withdrawal", 
                                                      amount=random.choice(attack_amounts), 
                                                      latitude=fraudulent_atm_location[0], 
                                                      longitude=fraudulent_atm_location[1], 
                                                      city=fraudulent_atm_location[2], 
                                                      country=fraudulent_atm_location[3], 
                                                      fraud_label=1)
            fraud_atm_transactions.append(transaction)
            tot_fraud_tractions+=1
        return fraud_atm_transactions



    def create_simulated_transactions(self):
        credit_cards = self.generate_list_credit_cards()
        
        transactions = self.create_transactions_data(credit_cards["cc_num"].tolist())
        
        return credit_cards, transactions
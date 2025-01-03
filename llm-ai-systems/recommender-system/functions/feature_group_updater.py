import pandas as pd
from datetime import datetime
import streamlit as st
import hopsworks
from typing import Optional
import logging
import math
import random

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FeatureGroupUpdater:
    def __init__(self):
        """Initialize the FeatureGroup updater"""
        self._initialize_feature_groups()
    
    def _initialize_feature_groups(self) -> None:
        """Initialize connection to Hopsworks Feature Groups"""
        try:
            if 'feature_group' not in st.session_state:
                logger.info("📡 Initializing Hopsworks Feature Groups connection...")
                project = hopsworks.login()
                fs = project.get_feature_store()
                
                # Initialize interactions feature group
                st.session_state.feature_group = fs.get_feature_group(
                    name="interactions",
                    version=1,
                )
                
                # Initialize transactions feature group
                st.session_state.transactions_fg = fs.get_feature_group(
                    name="transactions",
                    version=1,
                )
                logger.info("✅ Feature Groups connection established")

        except Exception as e:
            logger.error(f"Failed to initialize Feature Groups connection: {str(e)}")
            st.error("❌ Failed to connect to Feature Groups. Check terminal for details.")
            raise

    def _prepare_transaction_for_insertion(self, purchase_data: dict) -> pd.DataFrame:
        """Prepare transaction data for insertion into transactions feature group"""
        try:
            timestamp = datetime.now()
            
            transaction = {
                't_dat': int(timestamp.timestamp()),
                'customer_id': str(purchase_data['customer_id']),
                'article_id': str(purchase_data['article_id']),
                'price': round(random.uniform(10, 140), 2),
                'sales_channel_id': 2,
                'year': timestamp.year,
                'month': timestamp.month,
                'day': timestamp.day,
                'day_of_week': timestamp.weekday(),
                'month_sin': math.sin(2 * math.pi * timestamp.month / 12),
                'month_cos': math.cos(2 * math.pi * timestamp.month / 12)
            }
            
            df = pd.DataFrame([transaction])
            
            # Ensure correct data types
            df['t_dat'] = df['t_dat'].astype('int64')
            df['customer_id'] = df['customer_id'].astype(str)
            df['article_id'] = df['article_id'].astype(str)
            df['price'] = df['price'].astype('float64')
            df['sales_channel_id'] = df['sales_channel_id'].astype('int64')
            df['year'] = df['year'].astype('int32')
            df['month'] = df['month'].astype('int32')
            df['day'] = df['day'].astype('int32')
            df['day_of_week'] = df['day_of_week'].astype('int32')
            df['month_sin'] = df['month_sin'].astype('float64')
            df['month_cos'] = df['month_cos'].astype('float64')
            
            logger.info(f"Prepared transaction for insertion: {transaction}")
            return df

        except Exception as e:
            logger.error(f"Error preparing transaction data: {str(e)}")
            return None

    def insert_transaction(self, purchase_data: dict) -> bool:
        """Insert a single transaction into transactions feature group"""
        try:
            transaction_df = self._prepare_transaction_for_insertion(purchase_data)
            
            if transaction_df is not None:
                logger.info("Inserting transaction...")
                with st.spinner("💫 Recording transaction..."):
                    st.session_state.transactions_fg.multi_part_insert(transaction_df)
                logger.info("✅ Transaction inserted successfully")
                return True

        except Exception as e:
            logger.error(f"Failed to insert transaction: {str(e)}")
            st.error("❌ Failed to insert transaction. Check terminal for details.")

        return False

    def _prepare_interactions_for_insertion(self, df: pd.DataFrame) -> pd.DataFrame:
        """Prepare interactions dataframe for insertion"""
        if df is None or df.empty:
            return None

        try:
            # Convert timestamp to Unix timestamp if needed
            if not pd.api.types.is_integer_dtype(df['t_dat']):
                df['t_dat'] = pd.to_datetime(df['t_dat']).astype('int64') // 10**9

            prepared_df = pd.DataFrame({
                't_dat': df['t_dat'].astype('int64'),
                'customer_id': df['customer_id'].astype(str),
                'article_id': df['article_id'].astype(str),
                'interaction_score': df['interaction_score'].astype('int64'),
                'prev_article_id': df['prev_article_id'].astype(str)
            })

            logger.info(f"Prepared interaction for insertion")
            return prepared_df

        except Exception as e:
            logger.error(f"Error preparing interaction data: {str(e)}")
            return None

    def process_interactions(self, tracker, force: bool = False) -> bool:
        """Process and insert interactions immediately"""
        try:
            interactions_df = tracker.get_interactions_data()
            
            if interactions_df.empty:
                return False

            prepared_df = self._prepare_interactions_for_insertion(interactions_df)
            if prepared_df is not None:
                logger.info("Inserting interactions...")
                st.session_state.feature_group.multi_part_insert(prepared_df)
                logger.info("✅ Interactions inserted successfully")
                return True

        except Exception as e:
            logger.error(f"Error processing interactions: {str(e)}")
            return False

        return False

def get_fg_updater():
    """Get or create FeatureGroupUpdater instance"""
    if 'fg_updater' not in st.session_state:
        st.session_state.fg_updater = FeatureGroupUpdater()
    return st.session_state.fg_updater
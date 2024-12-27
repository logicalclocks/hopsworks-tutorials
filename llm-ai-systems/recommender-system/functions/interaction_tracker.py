from dataclasses import dataclass
from typing import Optional, Dict, Set, List, Tuple
from datetime import datetime
import pandas as pd
import streamlit as st
import logging
from enum import Enum, auto

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class InteractionType(Enum):
    """Enum for interaction types and their corresponding scores"""
    PURCHASE = auto()
    CLICK = auto()
    IGNORE = auto()
    
    @property
    def score(self) -> int:
        return {
            InteractionType.PURCHASE: 2,
            InteractionType.CLICK: 1,
            InteractionType.IGNORE: 0
        }[self]
    
    @classmethod
    def from_str(cls, value: str) -> 'InteractionType':
        return {
            'purchase': cls.PURCHASE,
            'click': cls.CLICK,
            'ignore': cls.IGNORE
        }[value.lower()]

@dataclass
class Interaction:
    t_dat: int  # Unix timestamp
    customer_id: str
    article_id: str
    interaction_type: str
    interaction_score: int
    prev_article_id: Optional[str]

class InteractionTracker:
    def __init__(self):
        """Initialize interaction tracking containers"""
        # Key: (customer_id, article_id, type) -> Interaction
        self.interactions: Dict[Tuple[str, str, str], Interaction] = {}
        # Key: customer_id -> list of article_ids
        self.current_items: Dict[str, List[str]] = {}
        # Key: customer_id -> set of article_ids
        self.purchased_items: Dict[str, Set[str]] = {}
        # Key: customer_id -> article_id
        self.last_interaction: Dict[str, str] = {}
        logger.info("Initialized InteractionTracker")
    
    def track_shown_items(self, customer_id: str, items_with_scores: list):
        """Record items being shown with their scores"""
        if customer_id not in self.purchased_items:
            self.purchased_items[customer_id] = set()
            
        item_ids = [str(item_id) for item_id, _ in items_with_scores]
        self.current_items[customer_id] = item_ids
        
        # Record ignore interactions
        timestamp = int(datetime.now().timestamp())
        
        for idx, item_id in enumerate(item_ids):
            if item_id not in self.purchased_items.get(customer_id, set()):
                prev_id = item_ids[idx-1] if idx > 0 else item_id
                self._add_interaction(
                    customer_id=customer_id,
                    article_id=item_id,
                    interaction_type='ignore',
                    prev_article_id=prev_id,
                    timestamp=timestamp
                )
        
        logger.info(f"Tracked {len(item_ids)} shown items for customer {customer_id}")
    
    def track(self, customer_id: str, article_id: str, interaction_type: str):
        """Record a user interaction"""
        article_id = str(article_id)
        
        if customer_id not in self.purchased_items:
            self.purchased_items[customer_id] = set()
        
        prev_article_id = self.last_interaction.get(customer_id, article_id)
        
        self._add_interaction(
            customer_id=customer_id,
            article_id=article_id,
            interaction_type=interaction_type,
            prev_article_id=prev_article_id
        )
        
        # Update tracking state and UI feedback
        int_type = InteractionType.from_str(interaction_type)
        if int_type == InteractionType.PURCHASE:
            self.purchased_items[customer_id].add(article_id)
            st.toast(f"🛍️ Purchased item {article_id}", icon="🛍️")
            logger.info(f"Tracked purchase of item {article_id} by customer {customer_id}")
        elif int_type == InteractionType.CLICK:
            st.toast(f"Viewed details of item {article_id}", icon="👁️")
            logger.info(f"Tracked click on item {article_id} by customer {customer_id}")
            
        if int_type in (InteractionType.CLICK, InteractionType.PURCHASE):
            self.last_interaction[customer_id] = article_id
    
    def _add_interaction(self, customer_id, article_id, interaction_type, prev_article_id, timestamp=None):
        """Add interaction with duplicate handling using dictionary"""
        if timestamp is None:
            timestamp = int(datetime.now().timestamp())
            
        key = (customer_id, article_id, interaction_type)
        int_type = InteractionType.from_str(interaction_type)
        
        self.interactions[key] = Interaction(
            t_dat=timestamp,
            customer_id=str(customer_id),
            article_id=str(article_id),
            interaction_type=interaction_type,
            interaction_score=int_type.score,
            prev_article_id=str(prev_article_id)
        )
        
        logger.debug(
            f"Added {interaction_type} interaction: "
            f"customer={customer_id}, article={article_id}, score={int_type.score}"
        )
    
    def get_interactions_data(self) -> pd.DataFrame:
        """Get all recorded interactions as a pandas DataFrame"""
        if not self.interactions:
            logger.info("No interactions recorded yet")
            return pd.DataFrame(columns=[
                't_dat', 'customer_id', 'article_id', 
                'interaction_type', 'interaction_score', 'prev_article_id'
            ])
            
        df = pd.DataFrame([vars(i) for i in self.interactions.values()])
        logger.info(f"Retrieved {len(df)} interactions")
        return df
    
    def should_show_item(self, customer_id: str, article_id: str) -> bool:
        """Check if an item should be shown (not purchased)"""
        return str(article_id) not in self.purchased_items.get(customer_id, set())
    
    def get_current_items(self, customer_id: str) -> List[str]:
        """Get current items for a customer"""
        return self.current_items.get(customer_id, [])
    
    def clear_interactions(self):
        """Clear all recorded interactions while preserving purchased items"""
        self.interactions.clear()
        logger.info("Cleared all recorded interactions")

def get_tracker():
    """Get or create InteractionTracker instance"""
    if 'interaction_tracker' not in st.session_state:
        st.session_state.interaction_tracker = InteractionTracker()
        logger.info("Created new InteractionTracker instance")
    return st.session_state.interaction_tracker

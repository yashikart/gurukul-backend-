"""
Reward Manager Service

Manages unified reward table and policy updates for the RL system.
Provides functions to query, aggregate, and update rewards.
"""

import logging
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


def add_reward(
    episode_id: str,
    source: str,
    reward_value: float,
    reward_type: str,
    context: Optional[Dict[str, Any]] = None,
    feedback_text: Optional[str] = None,
    db: Session = None
) -> bool:
    """
    Add a reward to the unified reward store
    
    Args:
        episode_id: Episode ID
        source: Reward source ('lm_core', 'ksml', 'vaani', 'user_feedback')
        reward_value: Reward value (0.0 to 1.0)
        reward_type: Type of reward ('quality', 'accuracy', 'user_satisfaction')
        context: Additional context
        feedback_text: User feedback text if applicable
        db: Database session
        
    Returns:
        bool: True if successful
    """
    if db is None:
        logger.warning("No database session provided, reward not saved")
        return False
    
    try:
        from app.models.rl_models import RLEpisode, RLReward
        
        # Find episode
        episode = db.query(RLEpisode).filter(RLEpisode.episode_id == episode_id).first()
        if not episode:
            logger.warning(f"Episode {episode_id} not found, cannot add reward")
            return False
        
        # Create reward
        reward = RLReward(
            episode_id=episode.id,
            source=source,
            reward_value=reward_value,
            reward_type=reward_type,
            context=context or {},
            feedback_text=feedback_text
        )
        
        db.add(reward)
        db.commit()
        
        logger.debug(f"Reward added: {source} = {reward_value} for episode {episode_id}")
        return True
        
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to add reward: {e}")
        return False


def get_unified_rewards(
    episode_id: str,
    db: Session
) -> Dict[str, Any]:
    """
    Get all rewards for an episode
    
    Args:
        episode_id: Episode ID
        db: Database session
        
    Returns:
        dict: Unified rewards with aggregated statistics
    """
    try:
        from app.models.rl_models import RLEpisode, RLReward
        
        # Find episode
        episode = db.query(RLEpisode).filter(RLEpisode.episode_id == episode_id).first()
        if not episode:
            return {"error": f"Episode {episode_id} not found"}
        
        # Get all rewards
        rewards = db.query(RLReward).filter(RLReward.episode_id == episode.id).all()
        
        # Aggregate by source
        rewards_by_source = {}
        total_reward = 0.0
        
        for reward in rewards:
            source = reward.source
            if source not in rewards_by_source:
                rewards_by_source[source] = {
                    "rewards": [],
                    "average": 0.0,
                    "count": 0
                }
            
            rewards_by_source[source]["rewards"].append({
                "value": reward.reward_value,
                "type": reward.reward_type,
                "context": reward.context,
                "timestamp": reward.created_at.isoformat() if reward.created_at else None
            })
            rewards_by_source[source]["count"] += 1
            total_reward += reward.reward_value
        
        # Calculate averages
        for source_data in rewards_by_source.values():
            if source_data["count"] > 0:
                source_data["average"] = sum(
                    r["value"] for r in source_data["rewards"]
                ) / source_data["count"]
        
        overall_average = total_reward / len(rewards) if rewards else 0.0
        
        return {
            "episode_id": episode_id,
            "total_rewards": len(rewards),
            "overall_average": round(overall_average, 4),
            "rewards_by_source": rewards_by_source,
            "episode_metadata": {
                "source_text": episode.source_text[:100] + "..." if len(episode.source_text) > 100 else episode.source_text,
                "target_lang": episode.target_lang,
                "tone": episode.tone,
                "created_at": episode.created_at.isoformat() if episode.created_at else None
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to get unified rewards: {e}")
        return {"error": str(e)}


def update_policy(
    language: str,
    rewards: List[Dict[str, Any]],
    db: Session
) -> bool:
    """
    Update RL policy based on accumulated rewards
    
    Args:
        language: Language code (e.g., 'ar')
        rewards: List of reward data
        db: Database session
        
    Returns:
        bool: True if policy updated successfully
    """
    try:
        from app.models.rl_models import RLPolicy
        
        policy_name = f"sovereign_fusion_{language}"
        
        # Find or create policy
        policy = db.query(RLPolicy).filter(
            RLPolicy.policy_name == policy_name,
            RLPolicy.is_active == True
        ).first()
        
        if not policy:
            policy = RLPolicy(
                policy_name=policy_name,
                language=language,
                parameters={},
                version="1.0.0"
            )
            db.add(policy)
        
        # Calculate average reward
        if rewards:
            avg_reward = sum(r.get("reward_value", 0.0) for r in rewards) / len(rewards)
            
            # Update policy statistics
            policy.total_episodes += 1
            # Exponential moving average
            policy.average_reward = 0.9 * policy.average_reward + 0.1 * avg_reward
            
            # Update parameters (simplified - in production would use actual RL algorithm)
            policy.parameters = {
                "learning_rate": 0.001,
                "last_avg_reward": round(avg_reward, 4),
                "update_count": policy.parameters.get("update_count", 0) + 1
            }
        
        db.commit()
        logger.info(f"Policy {policy_name} updated for {language}")
        return True
        
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to update policy: {e}")
        return False


def get_policy_stats(language: str, db: Session) -> Optional[Dict[str, Any]]:
    """
    Get current policy statistics for a language
    
    Args:
        language: Language code
        db: Database session
        
    Returns:
        dict: Policy statistics or None if not found
    """
    try:
        from app.models.rl_models import RLPolicy
        
        policy_name = f"sovereign_fusion_{language}"
        policy = db.query(RLPolicy).filter(
            RLPolicy.policy_name == policy_name,
            RLPolicy.is_active == True
        ).first()
        
        if not policy:
            return None
        
        return {
            "policy_name": policy.policy_name,
            "language": policy.language,
            "version": policy.version,
            "total_episodes": policy.total_episodes,
            "average_reward": round(policy.average_reward, 4),
            "parameters": policy.parameters,
            "last_updated": policy.last_updated.isoformat() if policy.last_updated else None
        }
        
    except Exception as e:
        logger.error(f"Failed to get policy stats: {e}")
        return None


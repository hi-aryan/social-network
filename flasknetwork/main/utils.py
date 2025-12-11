from flask import current_app
from sqlalchemy import case, desc, asc
from flasknetwork.models import Post, WorkloadLevel

def get_sorted_posts(query, sort_by):
    """
    Applies sorting to a SQLAlchemy query for Posts based on the sort_by parameter.
    
    Args:
        query: Base SQLAlchemy query object (e.g., Post.query)
        sort_by (str): The sort criterion ('newest', 'overall', 'professor', 'workload', etc.)
        
    Returns:
        Query: The query object with order_by applied.
    """
    # Whitelist of allowed sort options to prevent SQL injection and logic errors
    # Maps safe strings to actual sort logic
    
    # Default sort (Newest)
    if not sort_by or sort_by == 'newest':
        return query.order_by(Post.date_posted.desc())

    # Robust handling for other options
    if sort_by == 'top':
        # Overall Rating: Average of Professor, Material, Peers
        # We compute this on the fly in the DB.
        # (Prof + Mat + Peers) / 3
        # We assume these columns are not null (nullable=False in model).
        overall_score = (Post.rating_professor + Post.rating_material + Post.rating_peers) / 3
        return query.order_by(overall_score.desc(), Post.date_posted.desc())
        
    elif sort_by == 'professor':
        return query.order_by(Post.rating_professor.desc(), Post.date_posted.desc())
        
    elif sort_by == 'material':
        return query.order_by(Post.rating_material.desc(), Post.date_posted.desc())
        
    elif sort_by == 'peers':
        return query.order_by(Post.rating_peers.desc(), Post.date_posted.desc())
        
    elif sort_by == 'workload':
        # Workload: Light at the top.
        # Enum values: 'light', 'medium', 'heavy'.
        # We want order: Light (1) -> Medium (2) -> Heavy (3).
        # We use a CASE statement to assign numeric values for sorting.
        workload_order = case(
            {
                WorkloadLevel.light: 1,
                WorkloadLevel.medium: 2,
                WorkloadLevel.heavy: 3
            },
            value=Post.rating_workload
        )
        return query.order_by(workload_order.asc(), Post.date_posted.desc())
    
    # Fallback for any undefined/invalid sort param -> Default to Newest
    return query.order_by(Post.date_posted.desc())

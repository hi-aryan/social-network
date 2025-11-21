"""
Script to populate the RandomUsername table with Reddit-style usernames.
Run this script once to initialize the username pool.
"""

from dotenv import load_dotenv
load_dotenv()

from flasknetwork import create_app, db
from flasknetwork.models import RandomUsername

def create_username_pool(limit=None):
    """Create a pool of Reddit-style anonymous usernames."""
    
    # Reddit-style username components
    adjectives = [
        'Awesome', 'Crazy', 'Clever', 'Daring', 'Epic', 'Fantastic', 'Glorious', 'Happy',
        'Incredible', 'Jolly', 'Kind', 'Lucky', 'Mysterious', 'Noble', 'Outstanding', 'Peaceful',
        'Quirky', 'Radiant', 'Stellar', 'Tremendous', 'Ultimate', 'Vibrant', 'Wonderful', 
        'Ancient', 'Bold', 'Cosmic', 'Divine', 'Electric', 'Fierce', 'Golden', 'Hidden',
        'Infinite', 'Majestic', 'Nimble', 'Organic', 'Pristine',
        'Quantum', 'Royal', 'Sacred', 'Timeless', 'Unique', 'Wild'
    ]
    
    nouns = [
        'Panda', 'Student', 'Dragon', 'Phoenix', 'Tiger', 'Eagle', 'Wolf', 'Bear', 'Lion',
        'Falcon', 'Shark', 'Dolphin', 'Owl', 'Fox', 'Raven', 'Hawk',
        'Penguin', 'Koala', 'Octopus', 'Wizard', 'Ninja', 'Scholar', 'Artist', 'Explorer',
        'Coder', 'Hacker', 'Gamer', 'Dreamer', 'Thinker', 'Creator', 'Builder', 'Seeker',
        'Storm', 'Thunder', 'Lightning', 'Comet', 'Galaxy', 'Nebula', 'Meteor', 'Aurora'
    ]
    # TODO: add "Reviewer" and such words
    
    suffixes = ['42', '69', '88', '99', '777', '007', 'X', 'Pro', 'Max']
    
    usernames = []
    
    # Generate combinations
    for adj in adjectives:
        for noun in nouns:
            # Basic combination
            username = f"{adj}{noun}"
            if len(username) <= 20:
                usernames.append(username)
            
            # With suffixes
            for suffix in suffixes:
                username_with_suffix = f"{adj}{noun}{suffix}"
                if len(username_with_suffix) <= 20:
                    usernames.append(username_with_suffix)
    
    # Add some single-word usernames with numbers
    single_words = adjectives + nouns
    for word in single_words:
        for i in range(1, 1000, 37):  # Skip by 37 to get varied numbers
            username = f"{word}{i}"
            if len(username) <= 20:
                usernames.append(username)
    
    # Limit the number if specified
    if limit:
        usernames = usernames[:limit]
    
    return usernames

def populate_database(limit=None):
    """Populate the database with usernames."""
    app = create_app()
    
    with app.app_context():
        # Clear existing usernames (if any)
        RandomUsername.query.delete()
        
        usernames = create_username_pool(limit=limit)
        print(f"Generated {len(usernames)} usernames")
        
        # Add usernames to database in batches
        batch_size = min(100, len(usernames))  # Don't batch more than we have
        for i in range(0, len(usernames), batch_size):
            batch = usernames[i:i + batch_size]
            for username in batch:
                random_username = RandomUsername(username=username)
                db.session.add(random_username)
            
            db.session.commit()
            print(f"Added batch {i//batch_size + 1}/{(len(usernames)-1)//batch_size + 1}")
        
        print(f"Successfully added {len(usernames)} usernames to the database!")

if __name__ == '__main__':
    # Change this number to control how many usernames to generate
    USERNAME_LIMIT = None  # Set to 20, 50, 100, 1000, or None for all
    
    populate_database(limit=USERNAME_LIMIT)

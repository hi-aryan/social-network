import argparse
import sys
import os
# Add parent directory to path to allow importing flasknetwork
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from dotenv import load_dotenv

# Load environment variables from .env file in parent directory
load_dotenv(os.path.join(os.path.dirname(__file__), '../.env'))

from flasknetwork import create_app, db
from flasknetwork.models import Post, Tag

def add_tag_to_post(post_id, tag_names):
    """Adds tags to a specific post."""
    post = Post.query.get(post_id)
    if not post:
        print(f"Error: Post with ID {post_id} not found!")
        return

    print(f"Found post {post.id} by {post.author.username} for course {post.course.code}")

    tags_to_add = Tag.query.filter(Tag.name.in_(tag_names)).all()
    found_tag_names = {t.name for t in tags_to_add}
    missing_tags = set(tag_names) - found_tag_names

    if missing_tags:
        print(f"Warning: The following tags not found in DB: {', '.join(missing_tags)}")
        if not tags_to_add:
            print("No valid tags to add. Aborting.")
            return

    added_count = 0
    for tag in tags_to_add:
        if tag not in post.tags:
            post.tags.append(tag)
            added_count += 1
            print(f" -> Adding tag: {tag.name}")
        else:
            print(f" -> Post already has tag: {tag.name}")

    if added_count > 0:
        db.session.commit()
        print(f"Success! {added_count} tags added.")
    else:
        print("No changes made.")

def remove_tag_from_post(post_id, tag_names):
    """Removes specific tags from a post."""
    post = Post.query.get(post_id)
    if not post:
        print(f"Error: Post with ID {post_id} not found!")
        return

    print(f"Found post {post.id} by {post.author.username}")

    tags_to_remove = Tag.query.filter(Tag.name.in_(tag_names)).all()
    found_tag_names = {t.name for t in tags_to_remove}
    
    # Check for typos in command line args (tags that don't exist in DB)
    missing_db_tags = set(tag_names) - found_tag_names
    if missing_db_tags:
        print(f"Warning: These tags don't exist in the database: {', '.join(missing_db_tags)}")

    removed_count = 0
    for tag in tags_to_remove:
        if tag in post.tags:
            post.tags.remove(tag)
            removed_count += 1
            print(f" -> Removing tag: {tag.name}")
        else:
            print(f" -> Post does not have tag: {tag.name}")

    if removed_count > 0:
        db.session.commit()
        print(f"Success! {removed_count} tags removed.")
    else:
        print("No changes made.")

def delete_tag_globally(tag_name):
    """Permanently deletes a tag from the database and all posts."""
    tag = Tag.query.filter_by(name=tag_name).first()
    if not tag:
        print(f"Error: Tag '{tag_name}' not found in database.")
        return

    # Count usage before deletion
    usage_count = len(tag.posts)
    print(f"\nWARNING: You are about to PERMANENTLY DELETE the tag: '{tag.name}'")
    print(f"This tag is currently used on {usage_count} posts.")
    print("This action cannot be undone.")
    
    confirm = input("Are you sure? Type 'DELETE' to confirm: ")
    if confirm != 'DELETE':
        print("Aborted.")
        return

    # SQLAlchemy handles the association table cleanup automatically
    # But explicitly clearing it is safe/explicit
    tag.posts = [] 
    
    db.session.delete(tag)
    db.session.commit()
    print(f"Tag '{tag_name}' has been deleted from the database and removed from {usage_count} posts.")

def list_tags():
    """Lists all tags in the database."""
    tags = Tag.query.order_by(Tag.name).all()
    print(f"\nFound {len(tags)} tags:")
    print("-" * 40)
    for tag in tags:
        print(f"- {tag.name} ({tag.sentiment.value}) [Used on {len(tag.posts)} posts]")
    print("-" * 40)

def main():
    parser = argparse.ArgumentParser(description='Manage tags for Flask Network')
    subparsers = parser.add_subparsers(dest='command', help='Command to run')

    # ADD command
    add_parser = subparsers.add_parser('add', help='Add tags to a post')
    add_parser.add_argument('post_id', type=int, help='ID of the post')
    add_parser.add_argument('tags', nargs='+', help='List of tags to add')

    # REMOVE command (from post)
    remove_parser = subparsers.add_parser('remove', help='Remove tags from a specific post')
    remove_parser.add_argument('post_id', type=int, help='ID of the post')
    remove_parser.add_argument('tags', nargs='+', help='List of tags to remove')

    # DELETE command (global)
    delete_parser = subparsers.add_parser('delete-global', help='PERMANENTLY delete a tag from the database')
    delete_parser.add_argument('tag_name', help='Exact name of the tag to delete')

    # LIST command
    subparsers.add_parser('list', help='List all available tags')

    args = parser.parse_args()

    app = create_app()
    with app.app_context():
        if args.command == 'add':
            add_tag_to_post(args.post_id, args.tags)
        elif args.command == 'remove':
            remove_tag_from_post(args.post_id, args.tags)
        elif args.command == 'delete-global':
            delete_tag_globally(args.tag_name)
        elif args.command == 'list':
            list_tags()
        else:
            parser.print_help()

if __name__ == '__main__':
    main()


# ./venv/bin/python scripts/manage_tags.py list
# ./venv/bin/python scripts/manage_tags.py add <post_id> "Tag Name 1" "Tag Name 2"
# ./venv/bin/python scripts/manage_tags.py remove <post_id> "Tag Name 1"
# ./venv/bin/python scripts/manage_tags.py delete-global "Tag Name To Destroy"
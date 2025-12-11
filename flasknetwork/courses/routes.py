from flask import Blueprint, render_template, request, jsonify, current_app
from flasknetwork.models import Course, Post
from sqlalchemy.exc import SQLAlchemyError
from flask_login import current_user

courses = Blueprint('courses', __name__)


class CourseSearchService:
    """
    Service class for handling course search operations.
    Encapsulates business logic and error handling.
    """
    
    @staticmethod
    def search_courses(query_param, limit_param=None):
        """
        Search for courses based on query parameter.
        
        Args:
            query_param (str): The search query from request
            limit_param (str|int): The limit parameter from request
            
        Returns:
            tuple: (success: bool, data: list|str, status_code: int)
        """
        try:
            limit = 50  # Default limit
            if limit_param:
                try:
                    limit = int(limit_param)
                    if limit < 1 or limit > 100:
                        return False, "Limit must be between 1 and 100", 400
                except (ValueError, TypeError):
                    return False, "Invalid limit parameter", 400
            
            courses = Course.search(query_param, limit)
            
            # Convert to dictionary format for JSON response
            courses_data = [course.to_dict() for course in courses]
            
            return True, courses_data, 200
            
        except ValueError as e:
            # Input validation errors
            current_app.logger.warning(f"Course search validation error: {str(e)}")
            return False, str(e), 400
            
        except SQLAlchemyError as e:
            # db errors
            current_app.logger.error(f"Database error in course search: {str(e)}")
            return False, "Database error occurred", 500
            
        except Exception as e:
            # Unexpected errors
            current_app.logger.error(f"Unexpected error in course search: {str(e)}")
            return False, "An unexpected error occurred", 500


@courses.route('/search')
def search():
    """
    Render the course search page.
    Replaces the former About page functionality.
    """
    # has to look in the templates/courses dir to find search.html
    return render_template('courses/search.html', title='Search Courses')


# this route just returns JSON data if query is valid
@courses.route('/api/search')
def api_search():
    """
    API endpoint for course search and browse.
    
    Query Parameters:
        q (str): Search query (optional - if empty, returns all courses)
        limit (int): Maximum results to return (optional, default 20, max 100)
        offset (int): Number of results to skip for pagination (optional, default 0)
        
    Returns:
        JSON response with courses data and has_more flag
    """
    query = request.args.get('q', '').strip()
    limit = request.args.get('limit', 20, type=int)
    offset = request.args.get('offset', 0, type=int)
    
    # Validate limit and offset
    limit = max(1, min(limit, 100))
    offset = max(0, offset)
    
    try:
        if not query:
            # Browse mode: return all courses with pagination
            courses_list, has_more = Course.get_all(limit=limit, offset=offset)
            courses_data = [course.to_dict() for course in courses_list]
            return jsonify({'courses': courses_data, 'has_more': has_more}), 200
        
        # Search mode: use existing search logic
        success, data, status_code = CourseSearchService.search_courses(query, limit)
        
        if success:
            return jsonify({'courses': data, 'has_more': False}), status_code
        else:
            return jsonify({'error': data}), status_code
            
    except SQLAlchemyError as e:
        current_app.logger.error(f"Database error in course API: {str(e)}")
        return jsonify({'error': 'Database error occurred'}), 500


from flasknetwork.main.utils import get_sorted_posts

@courses.route('/course/<int:course_id>')
def course_detail(course_id):
    """
    Display details for a specific course including its reviews with pagination.
    
    Args:
        course_id (int): The ID of the course to display
        
    Query Parameters:
        page (int): Page number for pagination (default: 1)
        sort (str): Sort order for reviews (default: newest)
    """
    try:
        page = request.args.get('page', 1, type=int)
        sort_by = request.args.get('sort', 'newest')
        course = Course.query.get_or_404(course_id)
        
        # Base Query: Get reviews for this course
        query = Post.query.filter_by(course=course)
        
        # Apply sorting
        query = get_sorted_posts(query, sort_by)
        
        reviews = query.paginate(page=page, per_page=5)

        # Get course statistics efficiently
        avg_rating = course.get_average_rating()

        auth_can_review = ( 
            current_user.is_authenticated and current_user.can_review(course)
        )

        already_reviewed = (
            current_user.is_authenticated and course.is_reviewed_by(current_user)
        )

        not_in_program = (
            current_user.is_authenticated 
            and not already_reviewed 
            and not course.course_is_available_for_program(current_user.program_id)
        )

        return render_template('courses/detail.html', 
                             title=f'{course.code} - {course.name}',
                             course=course,
                             reviews=reviews,
                             avg_rating=avg_rating,
                             auth_can_review=auth_can_review,
                             already_reviewed=already_reviewed,
                             not_in_program=not_in_program,
                             sort_by=sort_by)

    except SQLAlchemyError as e:
        current_app.logger.error(f"Database error loading course {course_id}: {str(e)}")
        return render_template('errors/500.html'), 500
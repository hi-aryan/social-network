from flask import Blueprint, render_template, request, jsonify, current_app
from flasknetwork.models import Course
from sqlalchemy.exc import SQLAlchemyError
import logging

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
    API endpoint for course search.
    
    Query Parameters:
        q (str): Search query (required, min 2 chars)
        limit (int): Maximum results to return (optional, default 50, max 100)
        
    Returns:
        JSON response with courses data or error message
    """
    # TODO: what is this "q" parameter?? how does it work?
    query = request.args.get('q', '').strip()
    
    # Early return for empty queries
    if not query:
        return jsonify([]), 200
    
    limit = request.args.get('limit')
    
    # Use service class for business logic
    success, data, status_code = CourseSearchService.search_courses(query, limit)
    
    if success:
        return jsonify(data), status_code
    else:
        return jsonify({'error': data}), status_code


@courses.route('/course/<int:course_id>')
def course_detail(course_id):
    """
    Display details for a specific course including its reviews.
    
    Args:
        course_id (int): The ID of the course to display
    """
    try:
        course = Course.query.get_or_404(course_id)
        
        # Get all reviews for this course, ordered by date
        # TODO: how/why/WHERE is it ordered by date??
        reviews = course.reviews
        
        return render_template('courses/detail.html', 
                             title=f'{course.code} - {course.name}',
                             course=course,
                             reviews=reviews)
                             
    except SQLAlchemyError as e:
        current_app.logger.error(f"Database error loading course {course_id}: {str(e)}")
        return render_template('errors/500.html'), 500
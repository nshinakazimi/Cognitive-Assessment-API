from flask import Blueprint, render_template

ui_bp = Blueprint('ui', __name__)

@ui_bp.route('/')
def index():
    """Render the UI testing interface."""
    return render_template('index.html')

@ui_bp.route('/test')
def test():
    """Alternative endpoint for the UI testing interface."""
    return render_template('index.html') 
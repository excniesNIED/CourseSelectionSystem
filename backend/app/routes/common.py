from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app import db
from app.models import Course, Class, Teacher

common_bp = Blueprint('common', __name__)

@common_bp.route('/courses', methods=['GET'])
@jwt_required()
def get_all_courses():
    """获取所有课程（用于下拉选择等）"""
    try:
        courses = Course.query.all()
        return jsonify([{
            'course_id': c.course_id,
            'course_name': c.course_name,
            'hours': c.hours,
            'credits': c.credits,
            'exam_type': c.exam_type
        } for c in courses]), 200
    except Exception as e:
        return jsonify({'message': f'获取课程列表失败: {str(e)}'}), 500

@common_bp.route('/classes', methods=['GET'])
@jwt_required()
def get_all_classes():
    """获取所有班级（用于下拉选择等）"""
    try:
        classes = Class.query.all()
        return jsonify([{
            'class_id': c.class_id,
            'class_name': c.class_name
        } for c in classes]), 200
    except Exception as e:
        return jsonify({'message': f'获取班级列表失败: {str(e)}'}), 500

@common_bp.route('/teachers', methods=['GET'])
@jwt_required()
def get_all_teachers():
    """获取所有教师（用于下拉选择等）"""
    try:
        teachers = Teacher.query.all()
        return jsonify([{
            'teacher_id': t.teacher_id,
            'name': t.name,
            'title': t.title
        } for t in teachers]), 200
    except Exception as e:
        return jsonify({'message': f'获取教师列表失败: {str(e)}'}), 500

@common_bp.route('/academic-years', methods=['GET'])
@jwt_required()
def get_academic_years():
    """获取学年列表"""
    try:
        # 这里可以根据实际需求调整
        years = ['2022', '2023', '2024', '2025']
        return jsonify(years), 200
    except Exception as e:
        return jsonify({'message': f'获取学年列表失败: {str(e)}'}), 500

@common_bp.route('/semesters', methods=['GET'])
@jwt_required()
def get_semesters():
    """获取学期列表"""
    try:
        semesters = [
            {'value': 1, 'label': '第一学期'},
            {'value': 0, 'label': '第二学期'}
        ]
        return jsonify(semesters), 200
    except Exception as e:
        return jsonify({'message': f'获取学期列表失败: {str(e)}'}), 500

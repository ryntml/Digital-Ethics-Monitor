# api/routes.py
from flask import Blueprint, request, jsonify
from api.auth import require_auth, require_role
from main_secure import SecureDigitalEthicsMonitor
from services.security_manager import SecurityManager, SecurityException
import traceback

api_bp = Blueprint('api', __name__)
security_manager = SecurityManager()

@api_bp.route('/auth/login', methods=['POST'])
def login():
    """User login endpoint"""
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    # TODO: Implement actual user validation
    # For now, demo authentication
    if username and password:
        role = 'admin' if username == 'admin' else 'analyst'
        token = security_manager.generate_token(username, role)
        
        return jsonify({
            "success": True,
            "token": token,
            "user": {
                "id": username,
                "role": role
            },
            "expires_in": 86400
        })
    
    return jsonify({"error": "Invalid credentials"}), 401

@api_bp.route('/ethics/evaluate', methods=['POST'])
@require_auth
@require_role('analyst')
def evaluate_fairness():
    """Evaluate dataset fairness"""
    try:
        token = request.headers.get('Authorization').replace('Bearer ', '')
        monitor = SecureDigitalEthicsMonitor(token)
        
        data = request.json
        dataset_id = data.get('dataset_id', 'balanced')
        dataset_path = data.get('dataset_path', f'datasets/{dataset_id}.csv')
        
        results = monitor.process_datasets({
            dataset_id: dataset_path
        })
        
        return jsonify({
            "success": True,
            "results": results.get(dataset_id, {})
        })
        
    except SecurityException as e:
        return jsonify({"error": str(e)}), 403
    except Exception as e:
        safe_error = security_manager.sanitize_error(e)
        return jsonify({"error": safe_error}), 500

@api_bp.route('/ethics/security-report', methods=['GET'])
@require_auth
@require_role('admin')
def get_security_report():
    """Get security report (admin only)"""
    try:
        token = request.headers.get('Authorization').replace('Bearer ', '')
        monitor = SecureDigitalEthicsMonitor(token)
        
        report = monitor.generate_security_report()
        return jsonify(report)
        
    except SecurityException as e:
        return jsonify({"error": str(e)}), 403

@api_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "version": "1.0.0"
    })
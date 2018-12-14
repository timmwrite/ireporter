"""Views for Incidents"""
import datetime
import os
from functools import wraps

import jwt
from flask import jsonify, make_response, request, session
from flask_restful import Resource

from app.api.v2.users.models import UserModel

from .models import IncidentModel

secret = os.getenv('SECRET_KEY')

def require_token(f):
    @wraps(f)
    def secure(*args, ** kwargs):
        token = None

        if 'token' in request.headers:
            token = request.headers['token']
        if not token:
            return make_response(jsonify({
                "message" : "Token is missing"
            }), 401)

        try:
            data = jwt.decode(token, secret)
            current_user =UserModel().find_user_by_email(data['email'])
        except:
            return make_response(jsonify({
                "message" : "Token is invalid"
            }), 401)
        return f(current_user, *args, **kwargs)
    return secure

   
class Incidents(Resource):
    """docstring for incidents class"""

    def __init__(self):
        """initiliase the incidents class"""
        self.db = IncidentModel()
        
    @require_token
    def post(current_user, self):
        """docstring for saving an incident"""
        incident = self.db.save(current_user[0]['user_id'])

        return jsonify({
            "status": 201,
            "data": incident,
            "message": "Created incidents record"    
        })

    @require_token
    def get(current_user, self):
        """docstring for getting all the incidents posted by users"""
        self.db.find_all()
        return make_response(jsonify({
            "status": 200,
            "data": self.db.find_all()
        }), 200)


class Incident(Resource):
    """docstring of a single incident"""

    def __init__(self):
        """initiliase the incident class"""
        self.db = IncidentModel()

    @require_token
    def get(current_user, self, incident_id):
        """method for getting a specific incident"""
        incident = self.db.find_by_id(incident_id)
        if incident == "incident does not exit":
            return make_response(jsonify({
                "status": 404,
                "error": "incident does not exit"
            }))

        return make_response(jsonify({
            "status": 200,
            "data": incident
        }), 200)

    @require_token
    def delete(current_user, self, incident_id):
        """docstring for deleting an incident"""   
        incident = self.db.find_by_id(incident_id)
        if incident == "incident does not exit":
            return jsonify({
                "status": 404,
                "error": "incident does not exit"
            })

        if current_user[0]["user_id"] != incident["createdby"]: 
            return jsonify({
             "status":401,   
            "error":"sorry you can't delete an incident you din't create"
            }) 
        
        if self.db.delete(incident_id) == "deleted":
            return jsonify({
                "status": 200,
                "message": 'incident record has been deleted'
            })


class UpdateLocation(Resource):
    """class to update incident location"""

    def __init__(self):
        """initiliase the update location class"""
        self.db = IncidentModel()

    @require_token
    def patch(current_user, self, incident_id):
        """method to update an incidents location"""
        incident = self.db.find_by_id(incident_id)

        if incident == "incident does not exit":
            return jsonify({
                "status": 404,
                "error": "sorry Incident does not exist"
            })

        if current_user[0]["user_id"] != incident['createdby']: 
            return jsonify({
             "status":401,   
            "error":"sorry you can't edit an incident you din't create"
            }) 

        if incident == "incident does not exit":
            return jsonify({
                "status": 404,
                "error": "sorry Incident does not exist"
            })
        edit_status = self.db.edit_incident_location(incident_id)
        if edit_status == "keyerror":
            return jsonify({
                "status": 500,
                "error": "KeyError Incidents location not updated"
            })
        elif edit_status == "location updated":
            return jsonify({
                "status": 200,
                "data": {
                    "id": incident_id,
                    "message": "Updated incident record's location"
                }
            })


class UpdateComment(Resource):
    """docstring for patching comment"""

    def __init__(self):
        self.db = IncidentModel()
    @require_token
    def patch(current_user, self, incident_id):
        """method to update comment in an incident"""
        incident = self.db.find_by_id(incident_id)
        if incident == "incident does not exit":
            return jsonify({
                "status": 404,
                "error": "incident does not exit"
            })
        if current_user[0]["user_id"] != incident['createdby']: 
            return jsonify({
             "status":401,   
            "error":"sorry you can't edit an incident you din't create"
            }) 

        edit_status = self.db.edit_incident_comment(incident_id)
        if edit_status == "keyerror":
            return jsonify({
                "status": 500,
                "error": "KeyError Incident's comment not updated"
            })
        elif edit_status == "comment updated":
            return jsonify({
                "status": 200,
                "data": {
                    "id": incident_id,
                    "message": "Updated incident record's comment"
                }
            })

class UpdateStatus(Resource):
    """docstring for patching status"""

    def __init__(self):
        self.db = IncidentModel()

    @require_token
    def patch(current_user, self, incident_id):
        """method to update status in an incident"""
        incident = self.db.find_by_id(incident_id)
        if incident == "incident does not exit":
            return jsonify({
                "status": 404,
                "error": "incident does not exit"
            })
        if current_user['isadmin'] is False:
            return jsonify({
                "status": 401,
                "message": "sorry Only an admin can change the status of an incident"
            })
        
        edit_status = self.db.edit_incident_status(incident_id)
        if edit_status == "keyerror":
            return jsonify({
                "status": 500,
                "error": "KeyError Incident's comment not updated"
            })
        elif edit_status == "status updated":
            return jsonify({
                "status": 200,
                "data": {
                    "id": incident_id,
                    "message": "Updated incident's status"
                }
            })

class Filter(Resource):
    """docstring filtering incidents by type"""

    def __init__(self):
        """initiliase the incident class"""
        self.db = IncidentModel()
    @require_token
    def get(current_user, self, incident_type):
        """method for getting a specific category of incidents"""
        incident = self.db.find_by_type(incident_type)
        if incident == "incident does not exit":
            return make_response(jsonify({
                "status": 404,
                "error": "incident does not exit"
            }), 404)

        return make_response(jsonify({
            "status": 200,
            "data": incident
        }), 200)

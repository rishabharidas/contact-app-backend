from starlette.applications import Starlette
from starlette.routing import Route
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware

from operations import * # importing everything from operations.py

routes = [
    # end points for all the functons
    Route("/contacts/", endpoint=list_all_contacts, methods=["GET"]), # to list
    Route("/contacts/search/", endpoint=search_contact, methods=["GET"]), # search contacts
    Route("/contact/", endpoint=contact_creation, methods=["POST"]), # for create
    Route("/contacts/{contactId:int}", endpoint=contact_details,
    methods=["GET"]), # for contact details
    Route("/contacts/{contactId:int}", endpoint=delete_contact,
    methods=["DELETE"]), # for deletion 
    Route("/contacts/{contactId:int}", endpoint=edit_contact,
    methods=["PUT"]) # for edit
]

middleware = [
    Middleware(CORSMiddleware, allow_origins=['*'])
]

contact_app = Starlette(debug=False, routes=routes, middleware=middleware )

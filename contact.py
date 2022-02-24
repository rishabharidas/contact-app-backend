from starlette.applications import Starlette
from starlette.routing import Route
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware

from operations import * # importing everything from operations

routes = [
    Route("/contacts/", endpoint=list_all_contacts, methods=["GET"]), # for LIST
    Route("/contact/", endpoint=contact_creation, methods=["POST"]), # for CFREATE
    Route("/contacts/{contactId:int}", endpoint=contact_details,
    methods=["GET"]), # for DETAILS
    Route("/contacts/{contactId:int}", endpoint=delete_contact,
    methods=["DELETE"]), # foe DELETE
    Route("/contacts/{contactId:int}", endpoint=edit_contact,
    methods=["PUT"]), # for EDIT
    Route("/contacts/", endpoint=search_contact, methods=["GET"]) # search contacts
]

middleware = [
    Middleware(CORSMiddleware, allow_origins=['*'])
]

contact_app = Starlette(debug=False, routes=routes, middleware=middleware )

from starlette.applications import Starlette
from starlette.routing import Route
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware

from operations import * # importing everything from operations

routes = [
    Route("/contacts", endpoint=list_all_contacts, methods=["GET"]),
    Route("/contact", endpoint=contact_creation, methods=["POST"]),
    Route("/contacts/{contactId:int}", endpoint=contact_details, methods=["GET"]),
    Route("/contacts/{contactId:int}", endpoint=delete_contact, methods=["DELETE"]),
    Route("/contacts/{contactId:int}", endpoint=edit_contact, methods=["PUT"]),
    Route("/contacts/", endpoint=search_contact, methods=["GET"])
]

middleware = [
    Middleware(CORSMiddleware, allow_origins=['*'])
]

contact_app = Starlette(debug=False, routes=routes, middleware=middleware )

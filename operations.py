from ast import Return
import json,operator
from starlette.responses import JSONResponse
from sqlalchemy import JSON, delete
from databasedata import connected_engine
from sqlalchemy.sql import insert, update, delete
import json

from tables import contactemails, contactphones, contactstable

async def contact_creation(request):
    """function for contact creation."""
    
    number = {}
    contact_basics = {}
    email = {}
    received_contact = await request.json()
    for contact_data in received_contact: # --------- basics & job insertion

        contact_basics[contact_data] = received_contact[contact_data]
        if contact_data == "job":

            for job_details in received_contact[contact_data]:
                contact_basics[job_details] = \
                    received_contact[contact_data][job_details]

    contact_basics.pop("job")
    contact_basics.pop("phones")
    contact_basics.pop("emails")
    try:
        contact_basics.pop("contactId")
    except:
        pass
    contact_basics_query = insert(contactstable).values(**contact_basics)
    connected_engine.execute(contact_basics_query)

    max_id = connected_engine.execute(
        f"select contactId from contactstable where contactId = @@Identity"
        ).fetchall()

    for i in max_id:
        contactId = i[0]

    for contact_data in received_contact: # ----------- phones insertion

        if contact_data == "phones": # condition to check if phones
            phones_data = received_contact[contact_data] #saving list of datas
            number["contactId"] = contactId

            for phone_numbers in phones_data: # loop to iterate through dicts

                for each_phone in phone_numbers: # loop for each key value
                    number[each_phone] = phone_numbers[each_phone] # new dict
                number_query = insert(contactphones).values(**number)
                connected_engine.execute(number_query)

    for contact_data in received_contact: #  ----------- emails insertion

        if contact_data == "emails": # condition to check if email
            email_data = received_contact[contact_data] #saving list of datas
            email["contactId"] = contactId

            for emailIds in email_data: # loop to iterate through dicts
                for each_email in emailIds: # loop for each key value
                    email[each_email] = emailIds[each_email] # new dict
                email_query = insert(contactemails).values(**email)
                connected_engine.execute(email_query)
                

    return JSONResponse(received_contact)

async def list_all_contacts(request):
    """function to list all contacts."""
    contacts = []

    query = f"""
    select json_object(
        "contactId", contactstable.contactId,
        "firstName", contactstable.firstName,
        "lastName", contactstable.lastName,
        "phones", (
            select json_arrayagg(
                        json_object(
                            "type", contactphones.type,
                            "phoneNumber", contactphones.phoneNumber
                        )
                    )
                    from contactphones
                where
                    contactphones.contactId = contactstable.contactId
                ),
                "emails", (
                    select json_arrayagg(
                        json_object(
                            "type", contactemails.type,
                            "emailValue", contactemails.emailValue
                        )
                    )
                    from contactemails
                where 
                    contactemails.contactId = contactstable.contactId
                ),
                "notes", contactstable.notes,
                "job", json_object(
                            "companyName", contactstable.companyName,
                            "jobTitle", contactstable.jobTitle
                        )
            ) as contacts from contactstable
        left join contactemails
            on contactemails.contactId = contactstable.contactId
        left join contactphones
            on contactphones.contactId = contactstable.contactId 
    group by contactstable.contactId""" # query to take all contacts
    contact_data = connected_engine.execute(query)
    for contact in contact_data:
        contacts.append(json.loads(contact.contacts)) #append contacts to list

    return JSONResponse(contacts)

async def contact_details(request):
    """function to search for a contact."""
    requested_contactId = request.path_params['contactId'] # takes path parms
    # query for contact details

    details_query = f"""
            select json_object(
            "contactId", contactstable.contactId,
            "firstName", contactstable.firstName,
            "lastName", contactstable.lastName,
            "phones", (
                select json_arrayagg(
                            json_object(
                                "type", contactphones.type,
                                "phoneNumber", contactphones.phoneNumber
                            )
                        )
                        from contactphones
                    where
                        contactphones.contactId = contactstable.contactId
                    ),
                    "emails", (
                        select json_arrayagg(
                            json_object(
                                "type", contactemails.type,
                                "emailValue", contactemails.emailValue
                            )
                        )
                        from contactemails
                    where 
                        contactemails.contactId = contactstable.contactId
                    ),
                    "notes", contactstable.notes,
                    "job", json_object(
                                "companyName", contactstable.companyName,
                                "jobTitle", contactstable.jobTitle
                            )
                ) as contact from contactstable
            left join contactemails
                on contactemails.contactId = contactstable.contactId
            left join contactphones
                on contactphones.contactId = contactstable.contactId 
        where contactstable.contactId = {requested_contactId}"""

    contact_result = connected_engine.execute(details_query) # execute query 

    try:
        for contact_data in contact_result:
            contact = json.loads(contact_data.contact)
    except:
        raise Exception("no contact")

    return JSONResponse(contact)

async def search_contact(request):
    """Function to serach contacts on name"""
    requested_contactname = request.query_params['name']

    details_query = f"""
        select json_object(
        "contactId", contactstable.contactId,
        "firstName", contactstable.firstName,
        "lastName", contactstable.lastName,
        "phones", (
            select json_arrayagg(
                        json_object(
                            "type", contactphones.type,
                            "phoneNumber", contactphones.phoneNumber
                        )
                    )
                    from contactphones
                where
                    contactphones.contactId = contactstable.contactId
                ),
                "emails", (
                    select json_arrayagg(
                        json_object(
                            "type", contactemails.type,
                            "emailValue", contactemails.emailValue
                        )
                    )
                    from contactemails
                where 
                    contactemails.contactId = contactstable.contactId
                ),
                "notes", contactstable.notes,
                "job", json_object(
                            "companyName", contactstable.companyName,
                            "jobTitle", contactstable.jobTitle
                        )
            ) as contact from contactstable
        left join contactemails
            on contactemails.contactId = contactstable.contactId
        left join contactphones
            on contactphones.contactId = contactstable.contactId 
    where contactstable.firstName = '{requested_contactname}'
    or contactstable.lastName = '{requested_contactname}'
    group by contactstable.contactId""" # query to search contacts

    contact_result=  connected_engine.execute(details_query)

    try:
        contacts = []
        for contact_data in contact_result:

            # append search results to list
            contacts.append(json.loads(contact_data.contact))
            
    except:
        raise Exception("no contact")

    return JSONResponse(contacts)

async def edit_contact(request):
    """function for editing a contact."""

    passed_contact = await request.json()
    requested_contactId = request.path_params['contactId'] # takes path parms

    # query for contact details
    contact_get_query = f"""
            select json_object(
            "contactId", contactstable.contactId,
            "firstName", contactstable.firstName,
            "lastName", contactstable.lastName,
            "phones", (
                select json_arrayagg(
                            json_object(
                                "type", contactphones.type,
                                "phoneNumber", contactphones.phoneNumber
                            )
                        )
                        from contactphones
                    where
                        contactphones.contactId = contactstable.contactId
                    ),
                    "emails", (
                        select json_arrayagg(
                            json_object(
                                "type", contactemails.type,
                                "emailValue", contactemails.emailValue
                            )
                        )
                        from contactemails
                    where 
                        contactemails.contactId = contactstable.contactId
                    ),
                    "notes", contactstable.notes,
                    "job", json_object(
                                "companyName", contactstable.companyName,
                                "jobTitle", contactstable.jobTitle
                            )
                ) as contact from contactstable
            left join contactemails
                on contactemails.contactId = contactstable.contactId
            left join contactphones
                on contactphones.contactId = contactstable.contactId 
        where contactstable.contactId = {requested_contactId}
        group by contactstable.contactId"""

    contact_result = connected_engine.execute(contact_get_query) # execute qry

    for contact_data in contact_result:
        try:
            contact_from_db = json.loads(contact_data.contact)
        except:
            raise Exception("no data to insert")

    print(contact_from_db)
    contact_basics = {}
    for contact_data in passed_contact: # ------- basics & job insertion
        contact_basics[contact_data] = passed_contact[contact_data]

        if contact_data == "job": # adding job data to common dict
            for job_details in passed_contact[contact_data]:
                contact_basics[job_details] = \
                    passed_contact[contact_data][job_details]

    contact_basics.pop("job")
    contact_basics.pop("phones")
    contact_basics.pop("emails")
    contact_basics.pop("contactId")

    update_name_query = update(contactstable).where(
        contactstable.contactId == requested_contactId
        ).values(**contact_basics) # query to update all basics data
        
    connected_engine.execute(update_name_query) # ----- End for basics insertion


    passed_phones_data = passed_contact["phones"] # saving values of phones data
    number = {}
    phones_keys_user = [z["type"] for z in passed_phones_data]  # adding all keys from passed resume of phones to list

    def number_insertion():
        for key_values in phones_keys_user:
            for update_number in passed_phones_data:
                if update_number["type"] == key_values:
                    number["contactId"] = requested_contactId
                    for key, value in update_number.items():
                        number[key] = value
                    print(number)
                    number_update_query = insert(contactphones)\
                        .values(**number)
                    connected_engine.execute(number_update_query)
                    print("inserting" )   
        
    try:
        phones_keys_db = [z["type"] for z in contact_from_db["phones"]] # add all key fron db of phones to list
    except TypeError:
        number_insertion()
    check_list = []
    contact_result = connected_engine.execute(contact_get_query) # execute qry
    for contact_data in contact_result:
        contact_from_db = json.loads(contact_data.contact)
    phones_keys_db = [z["type"] for z in contact_from_db["phones"]] # add all key fron db of phones to list
    removed_type = set(phones_keys_db) - set(phones_keys_user)
    print(removed_type)
    for to_delete_type in removed_type:
        delete_query = delete(contactphones)\
                .where(contactphones.contactId == requested_contactId)\
                .where(contactphones.type == to_delete_type)
        print("deleting ", to_delete_type)
        connected_engine.execute(delete_query)

    update_type = set(phones_keys_db) - removed_type 
    for to_update_type in update_type:
        for update_number in passed_phones_data:
            if update_number["type"] == to_update_type:
                for key, value in update_number.items():
                    number[key] = value
                print(number)
                number_update_query = update(contactphones)\
                    .where(contactphones.contactId == requested_contactId)\
                    .where(contactphones.type == to_update_type)\
                    .values(**number)
                connected_engine.execute(number_update_query)
                print("updating phone numbers" )
    
    for key_values in phones_keys_user:
        try:
            if key_values not in phones_keys_db:
                for update_number in passed_phones_data:
                    if update_number["type"] == key_values:
                        number["contactId"] = requested_contactId
                        for key, value in update_number.items():
                            number[key] = value
                        print(number)
                        number_update_query = insert(contactphones)\
                            .values(**number)
                        connected_engine.execute(number_update_query)
                        print("inserting" )
        except:
            number_insertion()  
    
    passed_emails_data = passed_contact["emails"] # saving values of emails data
    email = {}
    emails_keys_user = [z["type"] for z in passed_emails_data]  # adding all keys from passed resume of emails to list

    def email_insertion():
        for key_values in emails_keys_user:
            for update_email in passed_emails_data:
                if update_email["type"] == key_values:
                    email["contactId"] = requested_contactId
                    for key, value in update_email.items():
                        email[key] = value
                    print(email)
                    email_update_query = insert(contactemails)\
                        .values(**email)
                    connected_engine.execute(email_update_query)
                    print("inserting" )   
        
    try:
        emails_keys_db = [z["type"] for z in contact_from_db["emails"]] # add all key fron db of emails to list
    except TypeError:
        email_insertion()

    contact_result = connected_engine.execute(contact_get_query) # execute qry
    for contact_data in contact_result:
        contact_from_db = json.loads(contact_data.contact)
    emails_keys_db = [z["type"] for z in contact_from_db["emails"]] # add all key fron db of emails to list
    removed_type = set(emails_keys_db) - set(emails_keys_user)
    print(removed_type)
    for to_delete_type in removed_type:
        delete_query = delete(contactemails)\
                .where(contactemails.contactId == requested_contactId)\
                .where(contactemails.type == to_delete_type)
        print("deleting ", to_delete_type)
        connected_engine.execute(delete_query)

    update_type = set(emails_keys_db) - removed_type 
    for to_update_type in update_type:
        for update_email in passed_emails_data:
            if update_email["type"] == to_update_type:
                for key, value in update_email.items():
                    email[key] = value
                print(email)
                email_update_query = update(contactemails)\
                    .where(contactemails.contactId == requested_contactId)\
                    .where(contactemails.type == to_update_type)\
                    .values(**email)
                connected_engine.execute(email_update_query)
                print("updating phone emails" )
    
    for key_values in emails_keys_user:
        try:
            if key_values not in emails_keys_db:
                for update_email in passed_emails_data:
                    if update_email["type"] == key_values:
                        email["contactId"] = requested_contactId
                        for key, value in update_email.items():
                            email[key] = value
                        print(email)
                        email_update_query = insert(contactemails)\
                            .values(**email)
                        connected_engine.execute(email_update_query)
                        print("inserting" )
        except:
            email_insertion()  
    
    return JSONResponse()

async def delete_contact(request):
    """function for deleting a contact."""
    requested_contactId = request.path_params['contactId']
    delete_query = delete(contactstable).where(
        contactstable.contactId == requested_contactId
        ) # delete query
    delete_query2 = delete(contactemails).where(
        contactstable.contactId == requested_contactId
        ) # delete query
    delete_query3 = delete(contactphones).where(
    contactstable.contactId == requested_contactId
    ) # delete query
    connected_engine.execute(delete_query3) # executing delete
    connected_engine.execute(delete_query2) # executing delete
    connected_engine.execute(delete_query) # executing delete

    return JSONResponse("Deleted Sucessfully")

    
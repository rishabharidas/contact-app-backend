import json
from starlette.responses import JSONResponse
from sqlalchemy.sql import insert, update, delete

from databasedata import connected_engine # importing connection engine
from tables import contactemails, contactphones, contactstable

async def contact_creation(request):
    """function for contact creation."""
    
    number = {}
    contact_basics = {}
    email = {}
    received_contact = await request.json()
    for contact_data in received_contact: # ------ basics & job insertion

        contact_basics[contact_data] = received_contact[contact_data]
        if contact_data == "job":

            for job_details in received_contact[contact_data]:
                contact_basics[job_details] = \
                    received_contact[contact_data][job_details]

    try:
        contact_basics.pop("job")
    except KeyError:
        pass
    try:
        contact_basics.pop("phones")
    except KeyError:
        pass
    try:
        contact_basics.pop("emails")
    except KeyError:
        pass
    try:
        contact_basics.pop("contactId")
    except KeyError:
        pass

    try: # to check if no names are passed
        try:
            if contact_basics["firstName"]:
                pass
        except KeyError:
            if contact_basics["lastName"]:
                pass
    except KeyError:
        contact_basics["firstName"] = "No Name" # default name

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
                

    return JSONResponse({"contactId": contactId})

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
                ) as contact from contactstable
            left join contactemails
                on contactemails.contactId = contactstable.contactId
            left join contactphones
                on contactphones.contactId = contactstable.contactId 
        group by contactstable.contactId""" # query to take all contacts

    contact_data = connected_engine.execute(query)
    for contact in contact_data:
        contact = json.loads(contact.contact) # loads contact as json
        contact = {
            key : value for key, value in contact.items()
            if value
        } # removing empty key values

        # append search results to list
        contacts.append(contact)

    return JSONResponse(contacts)

async def contact_details(request):
    """function to search for a contact."""
    requested_contactId = request.path_params['contactId'] # takes path parms

    # query for collecting contact details
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
            contact = {
                key : value for key, value in contact.items()
                if value
            }
    except:
        raise Exception("no contact")
    

    return JSONResponse(contact)

async def search_contact(request):
    """Function to serach contacts on name"""
    requested_contactname = request.query_params['name'] # parameter passing

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
        search_contacts = []
        for contact_data in contact_result:
            # loads each contacts to a list
            search_contact = json.loads(contact_data.contact)
            search_contact = {
                key : value for key, value in search_contact.items()
                if value
            } # removing empty key values

            # append search results to list
            search_contacts.append(search_contact)
            
    except:
        raise Exception("no contact")

    return JSONResponse(search_contacts)

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

    contact_basics = {}
    for contact_data in passed_contact: # ------- basics & job insertion
        contact_basics[contact_data] = passed_contact[contact_data]

        if contact_data == "job": # adding job data to common dict
            for job_details in passed_contact[contact_data]:
                contact_basics[job_details] = \
                    passed_contact[contact_data][job_details]

    try:
        contact_basics.pop("job")
    except KeyError:
        pass
    try:
        contact_basics.pop("phones")
    except KeyError:
        pass
    try:
        contact_basics.pop("emails")
    except KeyError:
        pass
    contact_basics.pop("contactId")

    update_name_query = update(contactstable).where(
        contactstable.contactId == requested_contactId
        ).values(**contact_basics) # query to update all basics data
        
    connected_engine.execute(update_name_query) # --- End for basics insertion


    try:
        number = {}
        # saving values of phones data
        passed_phones_data = passed_contact["phones"] 

        # adding all keys from passed resume of phones to list
        phones_keys_user = [ 
            number_set["type"]
            for number_set in passed_phones_data
        ] 

        async def number_insertion(): # number insertion function
            for keys_value in phones_keys_user:
                for update_number in passed_phones_data:

                    if update_number["type"] == key_values:
                        number["contactId"] = requested_contactId
                        for key, value in update_number.items():
                            number[key] = value
                        number_update_query = insert(contactphones)\
                            .values(**number)
                        connected_engine.execute(number_update_query)
            
        try:
            # add all key fron db of phones to list
            phones_keys_db = [
                number_set["type"] 
                for number_set in contact_from_db["phones"]
            ] 
        except TypeError:
            await number_insertion()

        contact_result = connected_engine.execute(contact_get_query)
        for contact_data in contact_result:
            contact_from_db = json.loads(contact_data.contact)

        # add all key fron db of phones to list
        phones_keys_db = [
            number_set["type"] 
            for number_set in contact_from_db["phones"]
        ] 

        # finding to be deleted number set
        removed_type = set(phones_keys_db) - set(phones_keys_user)

        for to_delete_type in removed_type:
            delete_query = delete(contactphones)\
                .where(contactphones.contactId == requested_contactId)\
                .where(contactphones.type == to_delete_type)
            connected_engine.execute(delete_query)

        # finding diference betweeen lists
        update_type = set(phones_keys_db) - removed_type # for update 
        for to_update_type in update_type:
            for update_number in passed_phones_data:
                if update_number["type"] == to_update_type:
                    for key, value in update_number.items():
                        number[key] = value # adding data to number dict
                    number_update_query = update(contactphones).where(
                        contactphones.contactId == requested_contactId
                    ).where(contactphones.type == to_update_type)\
                        .values(**number) # update query
                    connected_engine.execute(number_update_query)
        
        for key_values in phones_keys_user:
            try:
                if key_values not in phones_keys_db: # insertion on update
                    for update_number in passed_phones_data:
                        if update_number["type"] == key_values:
                            number["contactId"] = requested_contactId
                            for key, value in update_number.items():
                                number[key] = value # adding data to number dict
                            number_update_query = insert(contactphones)\
                                .values(**number) # insert query
                            connected_engine.execute(number_update_query)
            except:
                await number_insertion()  

        # --- end for number section

    except KeyError:
        delete_query = delete(contactphones).where(
            contactphones.contactId == requested_contactId
        ) # delete query
        connected_engine.execute(delete_query)
        
    try:
        email = {}
        passed_emails_data = passed_contact["emails"] # saving "emails" data
        # adding all keys from passed resume of emails to list
        emails_keys_user = [email_set["type"] 
        for email_set in passed_emails_data]  

        async def email_insertion(): # function for emails insertion
            for keys_value in emails_keys_user:
                for update_email in passed_emails_data:
                    if update_email["type"] == key_values:
                        email["contactId"] = requested_contactId
                        for key, value in update_email.items():
                            email[key] = value # adding data to email dict
                        email_update_query = insert(contactemails)\
                            .values(**email)
                        connected_engine.execute(email_update_query)
            
        try:
            # add all key fron db of emails to list
            emails_keys_db = [
                email_set["type"] 
                for email_set in contact_from_db["emails"]
            ]
        except TypeError:
            await email_insertion()

        contact_result = connected_engine.execute(contact_get_query) # run qry
        for contact_data in contact_result: # deleting old values
            contact_from_db = json.loads(contact_data.contact)

        # add all key fron db of emails to list
        emails_keys_db = [
            email_set["type"] 
            for email_set in contact_from_db["emails"]
        ] 

        # findind difference to find the removed data
        removed_type = set(emails_keys_db) - set(emails_keys_user)
        for to_delete_type in removed_type:
            delete_query = delete(contactemails)\
                    .where(contactemails.contactId == requested_contactId)\
                    .where(contactemails.type == to_delete_type) # delete query
            connected_engine.execute(delete_query)

        # finding differnece to find the updatable data
        update_type = set(emails_keys_db) - removed_type 
        for to_update_type in update_type: # update existing values
            for update_email in passed_emails_data:
                if update_email["type"] == to_update_type:
                    for key, value in update_email.items():
                        email[key] = value # adding data to email dict
                    email_update_query = update(contactemails).where(
                        contactemails.contactId == requested_contactId
                        ).where(contactemails.type == to_update_type)\
                        .values(**email) # update query
                    connected_engine.execute(email_update_query)
        
        # section for inserting new added dicts
        for key_values in emails_keys_user:
            try:
                if key_values not in emails_keys_db: # finds new recevied dicts
                    for update_email in passed_emails_data:
                        if update_email["type"] == key_values:
                            email["contactId"] = requested_contactId
                            for key, value in update_email.items():
                                email[key] = value # adding data to email dict
                            email_update_query = insert(contactemails)\
                                .values(**email) # update query
                            connected_engine.execute(email_update_query)
            except:
                await email_insertion()  

    except KeyError:
        delete_query = delete(contactemails)\
                .where(
                    contactemails.contactId == requested_contactId
                )# del qry
        connected_engine.execute(delete_query)
        
    return JSONResponse("Sucessfully Updated")

async def delete_contact(request):
    """function for deleting a contact."""
    requested_contactId = request.path_params['contactId']

    delete_query = delete(contactstable).where(
        contactstable.contactId == requested_contactId
    ) # query for deletion
    connected_engine.execute(delete_query) # delte query execution

    return JSONResponse("Deleted Sucessfully")

    
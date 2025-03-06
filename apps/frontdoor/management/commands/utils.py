#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4
__author__ = "Alan Viars"

# adt  msg_names
adt_names = {}
adt_names["A01"] = "Admit/visit notification"
adt_names["A02"] = "Transfer a patient"
adt_names["A03"] = "Discharge/end visit"
adt_names["A04"] = "Register a patient"
adt_names["A05"] = "Pre-admit a patient"
adt_names["A06"] = "Change an outpatient to an inpatient"
adt_names["A08"] = "Update patient information"
adt_names["A10"] = "Patient arriving - tracking"
adt_names["A15"] = "Pending transfer"
adt_names["A28"] = "Add person information"
adt_names["A29"] = "Delete person information"
adt_names["A30"] = "Merge person information"
adt_names["A31"] = "Update person information"

# create a dictionary similar adt_names for VXU messages
vxu_names = {}
vxu_names["V04"] = "Immunization update"
vxu_names["V05"] = "Immunization query"
vxu_names["V06"] = "Immunization history for patient"
vxu_names["V07"] = "Immunization history for patient"
vxu_names["V08"] = "Immunization forecast for patient"
vxu_names["V09"] = "Immunization forecast query"
vxu_names["V10"] = "Immunization forecast query response"
vxu_names["V11"] = "Notification of vaccination record availability"
vxu_names["V12"] = "Notification of vaccination record availability query"
vxu_names["V13"] = "Vaccination query"
vxu_names["V14"] = "Vaccination query response"
vxu_names["V15"] = "Vaccination event report"
vxu_names["V16"] = "Vaccination event report response"
vxu_names["V17"] = "Request for deferred response to vaccination event report"
vxu_names["V18"] = "Deferred response to a vaccination event report"
vxu_names["V19"] = "Vaccination record correction"
vxu_names["V20"] = "Vaccination record completion"
vxu_names["V21"] = "Vaccination record completion query"
vxu_names["V22"] = "Vaccination record completion query response"
vxu_names["V23"] = "Vaccination query by parameter"
vxu_names["V24"] = "Vaccination query by parameter response"
vxu_names["V25"] = "Vaccination administration record query"
vxu_names["V26"] = "Vaccination administration record query response"
vxu_names["V27"] = "Vaccination query response"
vxu_names["V28"] = "Vaccination query response with multiple PID matches"

# create a dictionary similar adt_names for ORU messages
oru_names = {}
oru_names["R01"] = "Unsolicited transmission of an observation message"
oru_names["R03"] = "Unsolicited transmission of a results report"
oru_names["R04"] = "Unsolicited transmission of a results report"
oru_names["R21"] = "Unsolicited transmission of an individual laboratory observation message"
oru_names["R31"] = "Unsolicited transmission of a results report"

# create a dictionary similar adt_names for ORM messages
orm_names = {}
orm_names["O01"] = "Order message"
orm_names["O02"] = "Order response message"
orm_names["O03"] = "Order status message"
orm_names["O04"] = "Order status update message"
orm_names["O05"] = "Order status request message"
orm_names["O06"] = "Order confirmation message"
orm_names["O07"] = "Response to query transmission of an order message"
orm_names["O08"] = "Query transmission of an order message"

# transaction names
hl7_transaction_names = {}
hl7_transaction_names["ADT"] = adt_names
hl7_transaction_names["VXU"] = vxu_names
hl7_transaction_names["ORU"] = oru_names
hl7_transaction_names["ORM"] = orm_names
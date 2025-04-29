#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4
__author__ = "Alan Viars"

import argparse
import json
import hl7


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


def invalid_hl7(message):
    """ check if the file is Hl7. return a blank string if"""
    result = ""
    list_of_messages = []

    try:
        h = hl7.parse(message)
    #except hl7.exceptions.ParseException:
    #    result = "Parsing exception. Not an HL7 message."
    except Exception as e:
        print(e)   # noqa  
        return f"Parsing exception. Not an HL7 message. {e}"
    return result


def open_message(input_file):
    message = ""
    list_of_messages = []
    with open(input_file, "r") as fh:
        for line in fh:
            if len(line) == 1:
                list_of_messages.append(message)
                message = ""
            else:
                if not line.endswith('\r'):
                    line += "\r"
                message += line
    return message


def parse_message(message):
    """Parse hl7v2 message into a sensible json-like object"""
    responses = []
    h = hl7.parse(message)
    message = {}
    message["message"] = {}
    if str(h.segment('MSH')[9][0][0]):
        msg_type = str(h.segment('MSH')[9][0][0])
        sub_msg_type = str(h.segment('MSH')[9][0][1])
        message["message"]['msg_type'] = msg_type
        message["message"]["sub_msg_type"] = sub_msg_type
        message["message"]['msg_description'] = hl7_transaction_names[msg_type][sub_msg_type]
        message["message"]["id"] = h.segment('MSH')[10][0]
        message["message"]["from_system"] = str(
            h.segment('MSH')[3][0]).replace('^', '-')
        message["message"]["from_location"] = str(
            h.segment('MSH')[4][0]).replace('^', '-')
        message["message"]["to_system"] = str(
            h.segment('MSH')[5][0]).replace('^', '-')
        message["message"]["to_location"] = str(
            h.segment('MSH')[6][0]).replace('^', '-')
        message["message"]['timestamp'] = h.segment('MSH')[7][0]

        rd = {}
        rd['sub'] = h.segment('PID')[3][0]
        try:

            rd['given_name'] = h.segment('PID')[5][0][1][0]
        except IndexError:
            rd['given_name'] = ""
        
        try:
            rd['family_name'] = h.segment('PID')[5][0][0][0]
        except IndexError:
            rd['family_name'] = ""

        # phone
        try:
            rd['phone_number'] = h.segment('PID')[13][0][0][0]
        except IndexError:
            pass

        # language
        try:
            rd['language'] = h.segment('PID')[15][0]
        except IndexError:
            pass

        # marital status
        try:
            rd['marital_status'] = h.segment('PID')[16][0][0][0]
        except IndexError:
            pass

        if h.segment('PID')[8] == "M":
            rd['gender'] = "male"
        elif h.segment('PID')[8] == "F":
            rd['gender'] = "female"

        rd['birthdate'] = h.segment('PID')[7][0]

        rd['address'] = []
        rd['document'] = []
        addr = {}
        if len(h.segment('PID')[11][0]):
            addr['formatted'] = "%s %s %s %s %s" % (h.segment('PID')[11][0][0],
                                                       h.segment('PID')[
                11][0][1],
                h.segment('PID')[
                11][0][2],
                h.segment('PID')[11][0][3],
                h.segment('PID')[11][0][4],
            )
            # Clean up the formatted address
            addr['formatted'] = addr['formatted'].strip()

            if len(h.segment('PID')[11][0][0]):
                addr['street_address'] = h.segment('PID')[11][0][0][0]

            if len(h.segment('PID')[11][0][1][0]):
                addr['street_address'] = "%s %s" % (
                    addr['street_address'], h.segment('PID')[11][0][1])
            addr['locality'] = h.segment('PID')[11][0][2][0]
            addr['region'] = h.segment('PID')[11][0][3][0]
            addr['postal_code'] = h.segment('PID')[11][0][4][0]
            #addr['country'] = h.segment('PID')[11][0][5][0]
            if len(h.segment('PID')[11][0]) > 8:
                addr['county'] = h.segment('PID')[11][0][8][0]

        rd['address'].append(addr)

        doc = {}
        doc['number'] = h.segment('PID')[3][0]
        rd['document'].append(doc)

        # if an ssn was found, add it to the document claim
        # ssn
        try:
            ssn = h.segment('PID')[19][0]
            if ssn:
                doc = {}
                doc['number'] = ssn
                doc['issuer'] = "Social Security Administration (SSA)"
                doc['issuer_meta'] = []
                doc['issuer_meta'].append(
                    {"name": "ssn", "verbose_name": "Social Secuirity Number"})
                rd['document'].append(doc)
        except IndexError:
            pass

        message["patient_identity"] = rd

        # Grab info from EVN segment if available
        try:
            evn_segment = h.segment('EVN')
            message["event_type"] = {
                "event_type_code": evn_segment[1][0],
                "recorded_date_time": evn_segment[2][0],
                "date_time_planned_event": evn_segment[3][0],
                "event_reason_code": evn_segment[4][0],
                "operator_id": evn_segment[5][0],
                #"event_occurred": evn_segment[6][0]
            }
        except KeyError:
            pass

        # Grab info from PD1 segment if available
        try:
            pd1_segment = h.segment('PD1')
            message["patient_additional_demographic"] = {
                "living_dependency": pd1_segment[1][0],
                "living_arrangement": pd1_segment[2][0],
                "primary_facility": pd1_segment[3][0],
                "primary_care_provider": pd1_segment[4][0],
                "student_indicator": pd1_segment[5][0],
                "handicap": pd1_segment[6][0],
                "living_will_code": pd1_segment[7][0],
                "organ_donor_code": pd1_segment[8][0],
                "separate_bill": pd1_segment[9][0],
                "duplicate_patient": pd1_segment[10][0],
                "publicity_code": pd1_segment[11][0],
                "protection_indicator": pd1_segment[12][0],
                "protection_indicator_effective_date": pd1_segment[13][0],
                "place_of_worship": pd1_segment[14][0],
                "advance_directive_code": pd1_segment[15][0],
                "immunization_registry_status": pd1_segment[16][0],
                "immunization_registry_status_effective_date": pd1_segment[17][0],
                "publicity_code_effective_date": pd1_segment[18][0],
                "military_branch": pd1_segment[19][0],
                "military_rank": pd1_segment[20][0],
                "military_status": pd1_segment[21][0]
            }
        except KeyError:
            pass

        # Grab info from PV1 segment if available
        try:
            pv1_segment = h.segment('PV1')
            message["patient_visit"] = {
                "set_id": pv1_segment[1][0],
                "patient_class": pv1_segment[2][0],
                "assigned_patient_location": pv1_segment[3][0],
                "admission_type": pv1_segment[4][0],
                "preadmit_number": pv1_segment[5][0],
                "prior_patient_location": pv1_segment[6][0],
                #"attending_doctor": pv1_segment[7][0],
                #"referring_doctor": pv1_segment[8][0],
            }
        except KeyError:
            pass

        # Grab info from OBX segment if available
        try:
            obx_segments = h.segments('OBX')
            message["observations"] = []
            for obx_segment in obx_segments:
                observation = {
                    "set_id": obx_segment[1][0],
                    "value_type": obx_segment[2][0],
                    "observation_identifier": obx_segment[3][0],
                    "observation_sub_id": obx_segment[4][0],
                    "observation_value": obx_segment[5][0],
                    "units": obx_segment[6][0],
                    "references_range": obx_segment[7][0],
                    "abnormal_flags": obx_segment[8][0],
                    "probability": obx_segment[9][0],
                    "nature_of_abnormal_test": obx_segment[10][0],
                    "observ_result_status": obx_segment[11][0],
                    "date_last_obs_normal_values": obx_segment[12][0],
                    "user_defined_access_checks": obx_segment[13][0],
                    "date_time_of_the_observation": obx_segment[14][0],
                    "producer_id": obx_segment[15][0],
                    "responsible_observer": obx_segment[16][0],
                    "observation_method": obx_segment[17][0]
                }
                message["observations"].append(observation)
        except KeyError:
            pass

        # Grab info from OBR segment if available
        try:
            obr_segments = h.segments('OBR')
            message["orders"] = []
            for obr_segment in obr_segments:
                order = {
                    "set_id": obr_segment[1][0],
                    "placer_order_number": obr_segment[2][0],
                    "filler_order_number": obr_segment[3][0],
                    "universal_service_identifier": obr_segment[4][0],
                    "priority": obr_segment[5][0],
                    "requested_date_time": obr_segment[6][0],
                    "observation_date_time": obr_segment[7][0],
                    "observation_end_date_time": obr_segment[8][0],
                    "collection_volume": obr_segment[9][0],
                    "collector_identifier": obr_segment[10][0],
                    "specimen_action_code": obr_segment[11][0],
                    "danger_code": obr_segment[12][0],
                    "relevant_clinical_info": obr_segment[13][0],
                    "specimen_received_date_time": obr_segment[14][0],
                    "specimen_source": obr_segment[15][0],
                    "ordering_provider": obr_segment[16][0],
                    "order_callback_phone_number": obr_segment[17][0],
                    "placer_field_1": obr_segment[18][0],
                    "placer_field_2": obr_segment[19][0],
                    "filler_field_1": obr_segment[20][0],
                    "filler_field_2": obr_segment[21][0],
                    "results_rpt_status_chng_date_time": obr_segment[22][0],
                    "charge_to_practice": obr_segment[23][0],
                    "diagnostic_serv_sect_id": obr_segment[24][0],
                    "result_status": obr_segment[25][0],
                    "parent_result": obr_segment[26][0],
                    "quantity_timing": obr_segment[27][0],
                    "result_copies_to": obr_segment[28][0],
                    "parent": obr_segment[29][0],
                    "transportation_mode": obr_segment[30][0],
                    "reason_for_study": obr_segment[31][0],
                   #"principal_result_interpreter": obr_segment[32][0],
                   # "assistant_result_interpreter": obr_segment[33][0],
                   # "technician": obr_segment[34][0],
                   # "transcriptionist": obr_segment[35][0],
                   # "scheduled_date_time": obr_segment[36][0],
                   # "number_of_sample_containers": obr_segment[37][0],
                   # "transport_logistics_of_collected_sample": obr_segment[38][0],
                   # "collectors_comment": obr_segment[39][0],
                   # "transport_arrangement_responsibility": obr_segment[40][0],
                   # "transport_arranged": obr_segment[41][0],
                   # "escort_required": obr_segment[42][0],
                   # "planned_patient_transport_comment": obr_segment[43][0],
                   # "procedure_code": obr_segment[44][0],
                   # "procedure_code_modifier": obr_segment[45][0],
                   # "placer_supplemental_service_info": obr_segment[46][0],
                   # "filler_supplemental_service_info": obr_segment[47][0],
                   # "medically_necessary_duplicate_procedure_reason": obr_segment[48][0],
                   # "result_handling": obr_segment[49][0],
                   # "parent_universal_service_identifier": obr_segment[50][0]
                }
                message["orders"].append(order)
        except KeyError:
            pass

        responses.append(message)

    return responses


if __name__ == "__main__":

    # Parse args
    parser = argparse.ArgumentParser(description='Load in an HL7v2 file or stream.')
    parser.add_argument(
        dest='input_file',
        action='store',
        help='Input the HL7v2 source file.')
    args = parser.parse_args()
   
    result = invalid_hl7(args.input_file)
    if result:
        print(result)
        exit(1)
    message = open_message(args.input_file)
    result = parse_message(message)

    # output the JSON transaction summary
    print(json.dumps(result, indent=4))

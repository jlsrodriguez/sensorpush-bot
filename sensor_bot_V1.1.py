


import os.path
import base64
import json
import re
import time
import logging
from pysensorpush import PySensorPush
import pandas as pd
from datetime import datetime, timedelta
import math
import smtplib, ssl
from scipy import stats
import requests
import poplib
import email

port = 465

#Load Credentials

gcreds = pd.read_csv("gmail_creds.csv")

log_password = str(gcreds["Password"][0])

log_email = str(gcreds["Email"][0])

sens_creds = pd.read_csv("sens_creds.csv")

sens_password = str(sens_creds["Password"][0])

sens_email = str(sens_creds["Email"][0])

slack_log = "sensorpush_alerts-aaaahaontidulfwhtydysrdrau@altiusinstitute.slack.com"

context = ssl.create_default_context()

#Acknowledgement Instructions

ack_inst = " | To acknowledge this alert, copy/paste the following text in an email to sensorpush@altius.org: Acknowledged "

#Acknowledgement Ping

ack_pingmsg = """\
Subject: Alert Acknowledged

The latest alert for """

#Ping Alert
ping_message = """\
Subject: Info Ping

The following equipment sensor has been muted:"""

#Temperature Inc Alert

low_range_alert_inc = """\
Subject: Low Alert: Incubator out of Range

The following incubator was briefly out of range:"""

high_range_alert_inc = """\
Subject: Critical Alert: Incubator out of Range

The following incubator was CRITICALLY out of range:"""

med_range_alert_inc = """\
Subject: Medium Alert: Incubator out of Range

The following incubator was MODERATELY out of range for 30 minutes:"""

#Humidity Inc Alert

low_range_alert_inch = """\
Subject: Low Alert: Incubator out of Range

The following incubator was briefly out of range:"""

high_range_alert_inch = """\
Subject: Critical Alert: Incubator out of Range

The following incubator was CRITICALLY out of range:"""

med_range_alert_inch = """\
Subject: Medium Alert: Incubator out of Range

The following incubator was MODERATELY out of range for 30 minutes:"""

#Temperature Freezer Alert

low_range_alert_fret = """\
Subject: Low Alert: Freezer out of Range

The following freezer was briefly out of range:"""

high_range_alert_fret = """\
Subject: Critical Alert: Freezer out of Range

The following freezer was CRITICALLY out of range:"""

med_range_alert_fret = """\
Subject: Medium Alert: Freezer out of Range

The following freezer was MODERATELY out of range for 30 minutes:"""

#Humidity Freezer Alert

low_range_alert_freh = """\
Subject: Low Alert: Freezer out of Range

The following freezer was briefly out of range:"""

high_range_alert_freh = """\
Subject: Critical Alert: Freezer out of Range

The following freezer was CRITICALLY out of range:"""

med_range_alert_freh = """\
Subject: Medium Alert: Freezer out of Range

The following freezer was MODERATELY out of range for 30 minutes:"""

#Temperature Refridgerator Alert

low_range_alert_reft = """\
Subject: Low Alert: Refrigerator out of Range

The following refridgerator briefly was out of range:"""

high_range_alert_reft = """\
Subject: Critical Alert: Refrigerator out of Range

The following refridgerator was CRITICALLY out of range:"""

med_range_alert_reft = """\
Subject: Medium Alert: Refrigerator out of Range

The following refridgerator was MODERATELY out of range for 30 minutes:"""

#Temperature Refridgerator Alert

low_range_alert_reft = """\
Subject: Low Alert: Refrigerator out of Range

The following refridgerator briefly was out of range:"""

high_range_alert_reft = """\
Subject: Critical Alert: Refrigerator out of Range

The following refridgerator was CRITICALLY out of range:"""

med_range_alert_reft = """\
Subject: Medium Alert: Refrigerator out of Range

The following refrigerator was out MODERATELY of range for 30 minutes:"""

#Humidity Refridgerator Alert

low_range_alert_refh = """\
Subject: Low Alert: Refrigerator out of Range

The following refrigerator was briefly out of range:"""

high_range_alert_refh = """\
Subject: Critical Alert: Refrigerator out of Range

The following refrigerator was CRITICALLY out of range:"""

med_range_alert_refh = """\
Subject: Medium Alert: Refrigerator out of Range

The following refrigerator was MODERATELY out of range for 30 minutes:"""

#Phonebook

phonebook = pd.read_csv('phonebook.csv',dtype='string')

#Inc Temperature Ping Settings

genlow_inc = 1000
low_inc = 35
lowest_inc = 33
high_inc = 38
highest_inc = 39

inc_ping_time = 30
mute_hours = 9

#Inc Humidity Ping Settings

genlow_inch = 1000
low_inch = 85
lowest_inch = 70
high_inch = 100
highest_inch = 110

inch_ping_time = 30
mute_hours = 9

#Freezer Temperature Ping Settings

low_fret = -25
lowest_fret = -1000
genlow_fret = -15
high_fret = -10
highest_fret = -4

fret_ping_time = 30
mute_hours = 9

#Freezer Humidity Ping Settings

genlow_freh = 1000
low_freh = 45
lowest_freh = 30
high_freh = 80
highest_freh = 90

freh_ping_time = 30
mute_hours = 9

#Fridge Temp Ping Settings
genlow_reft = 8
low_reft = 2
lowest_reft = -4
high_reft = 15
highest_reft = 22

reft_ping_time = 30
mute_hours = 9

#Fridge Humidity Ping Settings
genlow_refh = 1000
low_refh = 45
lowest_refh = 30
high_refh = 80
highest_refh = 90

refh_ping_time = 30
mute_hours = 9

#Time Sensitive Ping Variables
#Incubators-Temp

mute_dif = timedelta(hours=24)
inc_high_alert_ping =  pd.DataFrame(False, columns = ['CO2-01', 'CO2-02', 'CO2-03', 'CO2-04', 'CO2-09', 'CO2-10', 'CO2-12', 'CO2-13'], index = range(1))
inc_inttime = datetime.strptime("0:0:0", "%H:%M:%S")
inc_hightime = pd.DataFrame(inc_inttime, columns = ['CO2-01', 'CO2-02', 'CO2-03', 'CO2-04', 'CO2-09', 'CO2-10', 'CO2-12', 'CO2-13'], index = range(1))
inc_pingtime = pd.DataFrame(inc_inttime, columns = ['CO2-01', 'CO2-02', 'CO2-03', 'CO2-04', 'CO2-09', 'CO2-10', 'CO2-12', 'CO2-13'], index = range(1))
inc_med_alert_ping =  pd.DataFrame(False, columns = ['CO2-01', 'CO2-02', 'CO2-03', 'CO2-04', 'CO2-09', 'CO2-10', 'CO2-12', 'CO2-13'], index = range(1))
inc_mute_array = pd.DataFrame(mute_dif, columns = ['CO2-01', 'CO2-02', 'CO2-03', 'CO2-04', 'CO2-09', 'CO2-10', 'CO2-12', 'CO2-13'], index = range(1))
inc_mute_mark  = pd.DataFrame(0, columns = ['CO2-01', 'CO2-02', 'CO2-03', 'CO2-04', 'CO2-09', 'CO2-10', 'CO2-12', 'CO2-13'], index = range(1))
inc_mute_time  = pd.DataFrame(mute_dif, columns = ['CO2-01', 'CO2-02', 'CO2-03', 'CO2-04', 'CO2-09', 'CO2-10', 'CO2-12', 'CO2-13'], index = range(1))
inc_alert_array = pd.DataFrame(0, columns = ['CO2-01', 'CO2-02', 'CO2-03', 'CO2-04', 'CO2-09', 'CO2-10', 'CO2-12', 'CO2-13'], index = range(1))

#Incubators-Humidity

mute_dif = timedelta(hours=24)
inch_high_alert_ping =  pd.DataFrame(False, columns = ['CO2-01', 'CO2-02', 'CO2-03', 'CO2-04', 'CO2-09', 'CO2-10', 'CO2-12', 'CO2-13'], index = range(1))
inch_inttime = datetime.strptime("0:0:0", "%H:%M:%S")
inch_hightime = pd.DataFrame(inc_inttime, columns = ['CO2-01', 'CO2-02', 'CO2-03', 'CO2-04', 'CO2-09', 'CO2-10', 'CO2-12', 'CO2-13'], index = range(1))
inch_pingtime = pd.DataFrame(inc_inttime, columns = ['CO2-01', 'CO2-02', 'CO2-03', 'CO2-04', 'CO2-09', 'CO2-10', 'CO2-12', 'CO2-13'], index = range(1))
inch_med_alert_ping =  pd.DataFrame(False, columns = ['CO2-01', 'CO2-02', 'CO2-03', 'CO2-04', 'CO2-09', 'CO2-10', 'CO2-12', 'CO2-13'], index = range(1))
inch_mute_array = pd.DataFrame(mute_dif, columns = ['CO2-01', 'CO2-02', 'CO2-03', 'CO2-04', 'CO2-09', 'CO2-10', 'CO2-12', 'CO2-13'], index = range(1))
inch_mute_mark  = pd.DataFrame(0, columns = ['CO2-01', 'CO2-02', 'CO2-03', 'CO2-04', 'CO2-09', 'CO2-10', 'CO2-12', 'CO2-13'], index = range(1))
inch_mute_time  = pd.DataFrame(mute_dif, columns = ['CO2-01', 'CO2-02', 'CO2-03', 'CO2-04', 'CO2-09', 'CO2-10', 'CO2-12', 'CO2-13'], index = range(1))
inch_alert_array = pd.DataFrame(0, columns = ['CO2-01', 'CO2-02', 'CO2-03', 'CO2-04', 'CO2-09', 'CO2-10', 'CO2-12', 'CO2-13'], index = range(1))

#Freezers-Temp
freezers=['Freezer-F1', 'Freezer-F2', 'Freezer-F3', 'Freezer-F4', 'Freezer-F46', 'Freezer-F47', 'Freezer-F5', 'Freezer-F6', 'Freezer-F9']
fret_high_alert_ping =  pd.DataFrame(False, columns = freezers, index = range(1))
fret_inttime = datetime.strptime("0:0:0", "%H:%M:%S")
fret_hightime = pd.DataFrame(inc_inttime, columns = freezers, index = range(1))
fret_pingtime = pd.DataFrame(inc_inttime, columns = freezers, index = range(1))
fret_med_alert_ping =  pd.DataFrame(False, columns = freezers, index = range(1))
fret_mute_array = pd.DataFrame(mute_dif, columns = freezers, index = range(1))
fret_mute_mark  = pd.DataFrame(0, columns = freezers, index = range(1))
fret_mute_time  = pd.DataFrame(mute_dif, columns = freezers, index = range(1))
fret_alert_array = pd.DataFrame(0, columns = freezers, index = range(1))

#Freezers-Humidity

freh_high_alert_ping =  pd.DataFrame(False, columns = freezers, index = range(1))
freh_inttime = datetime.strptime("0:0:0", "%H:%M:%S")
freh_hightime = pd.DataFrame(inc_inttime, columns = freezers, index = range(1))
freh_pingtime = pd.DataFrame(inc_inttime, columns = freezers, index = range(1))
freh_med_alert_ping =  pd.DataFrame(False, columns = freezers, index = range(1))
freh_mute_array = pd.DataFrame(mute_dif, columns = freezers, index = range(1))
freh_mute_mark  = pd.DataFrame(0, columns = freezers, index = range(1))
freh_mute_time  = pd.DataFrame(mute_dif, columns = freezers, index = range(1))
freh_alert_array = pd.DataFrame(0, columns = freezers, index = range(1))

#Refridgerators-Temp
fridges=['Fridge-R1', 'Fridge-R2', 'Fridge-R3', 'Fridge-R4']
reft_high_alert_ping =  pd.DataFrame(False, columns = fridges, index = range(1))
reft_inttime = datetime.strptime("0:0:0", "%H:%M:%S")
reft_hightime = pd.DataFrame(inc_inttime, columns = fridges, index = range(1))
reft_pingtime = pd.DataFrame(inc_inttime, columns = fridges, index = range(1))
reft_med_alert_ping =  pd.DataFrame(False, columns = fridges, index = range(1))
reft_mute_array = pd.DataFrame(mute_dif, columns = fridges, index = range(1))
reft_mute_mark  = pd.DataFrame(0, columns = fridges, index = range(1))
reft_mute_time  = pd.DataFrame(mute_dif, columns = fridges, index = range(1))
reft_alert_array = pd.DataFrame(0, columns = fridges, index = range(1))

#Refridgerators-Humidity
refh_high_alert_ping =  pd.DataFrame(False, columns = fridges, index = range(1))
refh_inttime = datetime.strptime("0:0:0", "%H:%M:%S")
refh_hightime = pd.DataFrame(inc_inttime, columns = fridges, index = range(1))
refh_pingtime = pd.DataFrame(inc_inttime, columns = fridges, index = range(1))
refh_med_alert_ping =  pd.DataFrame(False, columns = fridges, index = range(1))
refh_mute_array = pd.DataFrame(mute_dif, columns = fridges, index = range(1))
refh_mute_mark  = pd.DataFrame(0, columns = fridges, index = range(1))
refh_mute_time  = pd.DataFrame(mute_dif, columns = fridges, index = range(1))
refh_alert_array = pd.DataFrame(0, columns = fridges, index = range(1))

samples = 30
timer = 0
temp_sheet = pd.DataFrame()
humid_sheet = pd.DataFrame()
full_sheet = pd.DataFrame()
time_sheet = pd.DataFrame()

equipment = {
"CO2-01": "1450",
"CO2-02": "979", 
"CO2-03": "16820356", 
"CO2-04": "16820709",
"CO2-09": "16843165",
"CO2-10": "16840693",
"CO2-12": "16847238",
"CO2-13": "16843511",
"Freezer-F1": "16846000",
"Freezer-F2": "16848934",
"Freezer-F3": "16849142",
"Freezer-F4": "16846383",
"Freezer-F46": "16842353",
"Freezer-F47": "16847465",
"Freezer-F5": "16847676",
"Freezer-F6": "16849127",
"Freezer-F9": "37405",
"Fridge-R1": "1326",
"Fridge-R2": "1112",
"Fridge-R3": "37421",
"Fridge-R4": "37560"
}
equip_name = str()
name = str()
true_name = str()


def ack_ping(acklog_email_pass, acklog_password_pass, ackack_frame_pass, acktrue_name_pass):
    
    ackphonebook = phonebook[acktrue_name_pass]

    with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
         server.login(acklog_email_pass, acklog_password_pass)

         for addr in range(len(ackphonebook)):

             server.sendmail(acklog_email_pass, ackphonebook[addr], ack_pingmsg + str(acktrue_name_pass) + " has been acknowledged by " + str(ackack_frame_pass["Sender"][0]))

def ping_alert(log_email_pass, log_pass_pass, receiver, ping_message_pass, mute_time_pass, pingname_pass, mute_hours_ping_pass):

    with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
         server.login(log_email_pass, log_pass_pass)

         receiver = receiver[pingname_pass]
         for addr in range(len(receiver)):

             server.sendmail(log_email_pass, receiver[addr], ping_message_pass + " " + pingname_pass + " for " + str(timedelta(hours=mute_hours_ping_pass) - mute_time_pass))

def hum_alert(altrue_name_pass, log_email_pass, log_pass_pass, receiver, alert, humid_sheet_pass, temp_pass, alert_time_pass, al_low_pass, al_high_pass):
   
    if humid_sheet_pass.equals(humid_sheet):

       temp_humid_switch = " Humidity: "

    elif humid_sheet_pass.equals(temp_sheet):

       temp_humid_switch = " Temperature: "
    
    with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
         server.login(log_email_pass, log_pass_pass)

         if slack_log in receiver:
            server.sendmail(log_email_pass, receiver, alert + " " + altrue_name_pass + ", Optimal Range: " + str(al_low_pass) + " to " + str(al_high_pass) + " | Current " + temp_humid_switch + str(round(humid_sheet_pass[0],1)) + " @ Time: " + str(alert_time_pass["Time"][0]) + ack_inst + str(altrue_name_pass))
         elif 'Fridge' in altrue_name_pass:
            
            server.sendmail(log_email_pass, receiver, alert + " " + altrue_name_pass + ", Optimal Range: " + str(al_low_pass) + " to " + str(genlow_reft) + " | Current " + temp_humid_switch + str(round(humid_sheet_pass[0],1)) + " @ Time: " + str(alert_time_pass["Time"][0]) + ack_inst + str(altrue_name_pass))
         else:
            receiver = receiver[altrue_name_pass]
            #print(receiver)
            for addr in range(len(receiver)):

                server.sendmail(log_email_pass, receiver[addr], alert + " " + altrue_name_pass + ", Optimal Range: " + str(al_low_pass) + " to " + str(al_high_pass) + " | Current " + temp_humid_switch + str(round(humid_sheet_pass[0],1)) + " @ Time: " + str(alert_time_pass["Time"][0]) + ack_inst + str(altrue_name_pass))

def readEmails(mail_bot, mail_bot_password):

    pop3server = 'pop.gmail.com'
    username = mail_bot
    password = mail_bot_password
    pop3server = poplib.POP3_SSL(pop3server, '995')
    pop3server.user(username)
    pop3server.pass_(password)
    pop3info = pop3server.stat() #access mailbox status
    mailcount = pop3info[0] #total email
    message_report = pd.DataFrame(index=range(mailcount), columns=['Sender','Messages'])
    print("Accessing mailbox...")
    numb=0
    for i in range(mailcount):
        for j in pop3server.retr(i+1)[1]:
            msg = email.message_from_bytes(j)
            sender = msg['From']
            if sender != None:
               message_report['Sender'][i] = str(sender)    
            if (('Acknowledged' or 'Mute' or 'Ping') and ('CO2' or 'Freezer' or 'Fridge')) in str(msg):
               message_report['Messages'][i] = msg.get_payload()
              # print(message_report['Sender'][i])
              # print(message_report['Messages'][i])
               break
                      
               

    pop3server.quit()


    return message_report

def data_crunch(mute_hours_pass, inc_full_ack_pass, highest_inc_pass, high_inc_pass, low_inc_pass, lowest_inc_pass, temp_sheet_pass, realtime_sheet_pass, inc_ping_time_pass, inc_high_alert_ping_pass, true_name_pass, inc_alert_array_pass, inc_hightime_pass, inc_mute_mark_pass, inc_mute_time_pass, inc_mute_array_pass, inc_med_alert_ping_pass, inc_pingtime_pass, log_email_pass, log_password_pass, slack_log_pass, low_range_alert_inc_pass, med_range_alert_inc_pass, high_range_alert_inc_pass, genlow_pass, ping_frame_pass):
    
    temp_index = 0
    inc_alert_array_pass[true_name_pass] = 0
    for temp in range(len(temp_sheet_pass)):
 #       print(temp_sheet_pass[temp])
        dif = realtime_sheet_pass['Time'][0] - realtime_sheet_pass['Time'][temp]
        #print(dif)
        if ((float(temp_sheet_pass[temp]) >= float(high_inc_pass)) and (float(temp_sheet_pass[temp]) <= float(highest_inc_pass)) and (dif <= timedelta(minutes=inc_ping_time_pass)) and (inc_high_alert_ping_pass[true_name_pass][0] == False)):
           if inc_med_alert_ping_pass[true_name_pass][0] == False:           

              inc_alert_array_pass[true_name_pass] = inc_alert_array_pass[true_name_pass] + 60
           
              inc_hightime_pass[true_name_pass][0] = realtime_sheet_pass['Time'][temp]

    #          temp_index = temp

        elif ((float(temp_sheet_pass[temp]) <= float(low_inc_pass)) and (float(temp_sheet_pass[temp]) >= float(lowest_inc_pass)) and (dif <= timedelta(minutes=inc_ping_time_pass)) and (inc_high_alert_ping_pass[true_name_pass][0] == False)):
           if inc_med_alert_ping_pass[true_name_pass][0] == False:           

              inc_alert_array_pass[true_name_pass] = inc_alert_array_pass[true_name_pass] + 60

              inc_hightime_pass[true_name_pass][0] = realtime_sheet_pass['Time'][temp]
 
     #         temp_index = temp

        elif ((float(temp_sheet_pass[temp]) <= float(lowest_inc_pass)) and (inc_high_alert_ping_pass[true_name_pass][0] == False)):

           inc_alert_array_pass[true_name_pass] = 1800 + inc_alert_array_pass[true_name_pass]

           inc_hightime_pass[true_name_pass][0] = realtime_sheet_pass['Time'][temp]

      #     temp_index = temp

        elif ((float(temp_sheet_pass[temp]) >= float(highest_inc_pass)) and (inc_high_alert_ping_pass[true_name_pass][0] == False)):

           inc_alert_array_pass[true_name_pass] = 1800 + inc_alert_array_pass[true_name_pass]

           inc_hightime_pass[true_name_pass][0] = realtime_sheet_pass['Time'][temp]

           temp_index = temp

        elif ((float(temp_sheet_pass[temp]) >= float(genlow_pass)) and (inc_med_alert_ping_pass[true_name_pass][0] == False) and (inc_high_alert_ping_pass[true_name_pass][0] == False)):

           inc_alert_array_pass[true_name_pass] = 1 + inc_alert_array_pass[true_name_pass]

           inc_hightime_pass[true_name_pass][0] = realtime_sheet_pass['Time'][temp]

    zero_dif = realtime_sheet_pass['Time'][0] - inc_pingtime_pass[true_name_pass][0]
   # print(true_name_pass)
   # print(inc_alert_array_pass[true_name_pass])
   # print(inc_alert_array_pass[true_name_pass][0])
    if (str(true_name_pass) in str(inc_full_ack_pass["Messages"]) or inc_mute_array_pass[true_name_pass][0] <= timedelta(hours=mute_hours_pass)):

       inc_high_alert_ping_pass[true_name_pass][0] = True

       if inc_mute_mark_pass[true_name_pass][0] == 0:
             
          inc_mute_time_pass[true_name_pass][0] =  inc_hightime_pass[true_name_pass][0]

          inc_mute_mark_pass[true_name_pass][0] = 1

       inc_mute_array_pass[true_name_pass][0] = realtime_sheet_pass['Time'][0] - inc_mute_time_pass[true_name_pass][0]

          #print(inc_mute_array_pass[true_name_pass][0])

       #print("cond1")

    elif (inc_mute_array_pass[true_name_pass][0] >= timedelta(hours=mute_hours_pass) and zero_dif >= timedelta(minutes=inc_ping_time_pass)):

       inc_high_alert_ping_pass[true_name_pass][0] = False

       inc_med_alert_ping_pass[true_name_pass][0] = False

       inc_mute_mark_pass[true_name_pass][0] = 0

       #print("cond2")

    if ((inc_alert_array_pass[true_name_pass][0] >= 9000) and (inc_high_alert_ping_pass[true_name_pass][0] == False) and (inc_med_alert_ping_pass[true_name_pass][0] == False)):

       inc_pingtime_pass[true_name_pass][0] = realtime_sheet_pass['Time'][0]
       hum_alert(true_name_pass, log_email_pass, log_password_pass, phonebook, high_range_alert_inc_pass, temp_sheet_pass, temp_index, realtime_sheet_pass, low_inc_pass, high_inc_pass)
       hum_alert(true_name_pass, log_email_pass, log_password_pass, slack_log, high_range_alert_inc_pass, temp_sheet_pass, temp_index, realtime_sheet_pass, low_inc_pass, high_inc_pass)

       inc_alert_array_pass[true_name] = 0

       inc_high_alert_ping_pass[true_name_pass][0] = True

    elif ((inc_alert_array_pass[true_name_pass][0] <= 4000) and (inc_alert_array_pass[true_name_pass][0] >= 1) and (inc_med_alert_ping_pass[true_name_pass][0] == False)):
       
       inc_med_alert_ping_pass[true_name_pass][0] = True
       inc_pingtime_pass[true_name_pass][0] = realtime_sheet_pass['Time'][0]
       hum_alert(true_name_pass, log_email, log_password, slack_log, low_range_alert_inc_pass, temp_sheet_pass, temp_index, realtime_sheet_pass, low_inc_pass, high_inc_pass)
       inc_alert_array_pass[true_name_pass] = 0

    elif ((inc_alert_array_pass[true_name_pass][0] >= 4001) and (inc_alert_array_pass[true_name_pass][0] <= 8999) and (inc_med_alert_ping_pass[true_name_pass][0] == False) and (inc_high_alert_ping_pass[true_name_pass][0] == False)):

       inc_pingtime_pass[true_name_pass][0] = realtime_sheet_pass['Time'][0]
       hum_alert(true_name_pass, log_email_pass, log_password_pass, phonebook, med_range_alert_inc_pass, temp_sheet_pass, temp_index, realtime_sheet_pass, low_inc_pass, high_inc_pass)
       hum_alert(true_name_pass, log_email_pass, log_password_pass, slack_log, med_range_alert_inc_pass, temp_sheet_pass, temp_index, realtime_sheet_pass, low_inc_pass, high_inc_pass)
       inc_alert_array_pass[true_name_pass] = 0
       inc_med_alert_ping_pass[true_name_pass][0] = True
    
    if str(true_name_pass) in str(ping_frame_pass["Messages"]):
      # print(ping_frame_pass)
       ping_alert(log_email_pass, log_password_pass, phonebook, ping_message, inc_mute_array_pass[true_name_pass][0], true_name_pass, mute_hours_pass)

    
    return inc_high_alert_ping_pass, inc_hightime_pass, inc_mute_mark_pass, inc_mute_time_pass, inc_mute_array_pass, inc_med_alert_ping_pass, inc_pingtime_pass

while timer == 0:
      
      ack_frame = readEmails(log_email, log_password)    

      sensorpush = PySensorPush(sens_email, sens_password)
      
      data = sensorpush.samples(samples)
      
      #Operations and pings
      
      data = pd.DataFrame(data)
      print("Observing sensor data...")
      for sens in range(len(data)):
          
          true_name = str()          

          name = str()          

          sub_data = data.iloc[sens]

          full_sheet = pd.DataFrame(sub_data['sensors'])

          temp_sheet = full_sheet['temperature']

          temp_sheet = (temp_sheet - 32)*(5/9) 

          humid_sheet = full_sheet['humidity']

          name = sub_data.name

          time_sheet = full_sheet['observed']
      
          realtime_sheet = pd.DataFrame(columns=['Time'], index=range(len(time_sheet)))


          for t in range(len(time_sheet)):
              
              realtime_sheet['Time'][t] = datetime.strptime(str(time_sheet[t][0:19]), "%Y-%m-%d" + "T" + "%H:%M:%S")

              realtime_sheet['Time'][t] = realtime_sheet['Time'][t] - timedelta(hours=7)              

          #Rules for pinging

          #Incubators

          for equip, deviceid in equipment.items():

              if str(math.floor(float(name))) == deviceid:

                 true_name = str(equip)

       #Incubators - Temp

          if 'CO2' in true_name:
              #print(true_name)
                  
              inc_temp_ack_frame = ack_frame.query("Messages == 'Acknowledged ' + @true_name")

              inc_temp_mute_frame = ack_frame.query("Messages == 'Mute ' + @true_name")

              inc_temp_ping_frame = ack_frame.query("Messages == 'Ping ' + @true_name")
              
              inc_full_ack = pd.concat([inc_temp_ack_frame, inc_temp_mute_frame], ignore_index=True) 
              
              if len(inc_temp_ack_frame) > 0:

                 ack_ping(log_email, log_password, inc_temp_ack_frame, true_name)

              inc_alert_array[true_name] = 0

              inch_alert_array[true_name] = 0

              inc_high_alert_ping, inc_hightime, inc_mute_mark, inc_mute_time, inc_mute_array, inc_med_alert_ping, inc_pingtime = data_crunch(mute_hours, inc_full_ack, highest_inc, high_inc, low_inc, lowest_inc, temp_sheet, realtime_sheet, inc_ping_time, inc_high_alert_ping, true_name, inc_alert_array, inc_hightime, inc_mute_mark, inc_mute_time, inc_mute_array, inc_med_alert_ping, inc_pingtime, log_email, log_password, slack_log, low_range_alert_inc, med_range_alert_inc, high_range_alert_inc, genlow_inc, inc_temp_ping_frame)
              inc_temp_ping_frame = pd.DataFrame(columns=['Messages'], index=range(1))                            
              inch_high_alert_ping, inch_hightime, inch_mute_mark, inch_mute_time, inch_mute_array, inch_med_alert_ping, inch_pingtime = data_crunch(mute_hours, inc_full_ack, highest_inch, high_inch, low_inch, lowest_inch, humid_sheet, realtime_sheet, inch_ping_time, inch_high_alert_ping, true_name, inch_alert_array, inch_hightime, inch_mute_mark, inch_mute_time, inch_mute_array, inch_med_alert_ping, inch_pingtime, log_email, log_password, slack_log, low_range_alert_inch, med_range_alert_inch, high_range_alert_inch, genlow_inch, inc_temp_ping_frame)        
          
          elif 'Freezer' in true_name:

              fre_temp_ack_frame = ack_frame.query("Messages == 'Acknowledged ' + @true_name")

              fre_temp_mute_frame = ack_frame.query("Messages == 'Mute ' + @true_name")

              fre_temp_ping_frame = ack_frame.query("Messages == 'Ping ' + @true_name")

              fre_full_ack = pd.concat([fre_temp_ack_frame, fre_temp_mute_frame], ignore_index=True)

              fret_alert_array[true_name] = 0

              freh_alert_array[true_name] = 0
              
              fret_high_alert_ping, fret_hightime, fret_mute_mark, fret_mute_time, fret_mute_array, fret_med_alert_ping, fret_pingtime = data_crunch(mute_hours, fre_full_ack, highest_fret, high_fret, low_fret, lowest_fret, temp_sheet, realtime_sheet, fret_ping_time, fret_high_alert_ping, true_name, fret_alert_array, fret_hightime, fret_mute_mark, fret_mute_time, fret_mute_array, fret_med_alert_ping, fret_pingtime, log_email, log_password, slack_log, low_range_alert_fret, med_range_alert_fret, high_range_alert_fret, genlow_fret, fre_temp_ping_frame)
              fre_temp_ping_frame = pd.DataFrame(columns=['Messages'], index=range(1))
             # freh_high_alert_ping, freh_hightime, freh_mute_mark, freh_mute_time, freh_mute_array, freh_med_alert_ping, freh_pingtime = data_crunch(mute_hours, fre_full_ack, highest_freh, high_freh, low_freh, lowest_freh, humid_sheet, realtime_sheet, freh_ping_time, freh_high_alert_ping, true_name, freh_alert_array, freh_hightime, freh_mute_mark, freh_mute_time, freh_mute_array, freh_med_alert_ping, freh_pingtime, log_email, log_password, slack_log, low_range_alert_freh, med_range_alert_freh, high_range_alert_freh, genlow_freh, fre_temp_ping_frame)

          elif 'Fridge' in true_name:

              ref_temp_ack_frame = ack_frame.query("Messages == 'Mute ' + @true_name")

              ref_temp_mute_frame = ack_frame.query("Messages == 'Mute ' + @true_name")

              ref_temp_ping_frame = ack_frame.query("Messages == 'Ping ' + @true_name")

              ref_full_ack = pd.concat([ref_temp_ack_frame, ref_temp_mute_frame], ignore_index=True)

              reft_alert_array[true_name] = 0

              refh_alert_array[true_name] = 0

              reft_high_alert_ping, reft_hightime, reft_mute_mark, reft_mute_time, reft_mute_array, reft_med_alert_ping, reft_pingtime = data_crunch(mute_hours, ref_full_ack, highest_reft, high_reft, low_reft, lowest_reft, temp_sheet, realtime_sheet, reft_ping_time, reft_high_alert_ping, true_name, reft_alert_array, reft_hightime, reft_mute_mark, reft_mute_time, reft_mute_array, reft_med_alert_ping, reft_pingtime, log_email, log_password, slack_log, low_range_alert_reft, med_range_alert_reft, high_range_alert_reft, genlow_reft, ref_temp_ping_frame)
              ref_temp_ping_frame = pd.DataFrame(columns=['Messages'], index=range(1))
             # refh_high_alert_ping, refh_hightime, refh_mute_mark, refh_mute_time, refh_mute_array, refh_med_alert_ping, refh_pingtime = data_crunch(mute_hours, ref_full_ack, highest_refh, high_refh, low_refh, lowest_refh, humid_sheet, realtime_sheet, refh_ping_time, refh_high_alert_ping, true_name, refh_alert_array, refh_hightime, refh_mute_mark, refh_mute_time, refh_mute_array, refh_med_alert_ping, refh_pingtime, log_email, log_password, slack_log, low_range_alert_refh, med_range_alert_refh, high_range_alert_refh, genlow_refh, ref_temp_ping_frame)

      print("Loop completed, sleeping for a minute...")
      time.sleep(60)




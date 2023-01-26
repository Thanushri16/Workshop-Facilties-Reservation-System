# G-01: API-ify the Reservation System
#
# Group Name: 404 Team Not Found
#
# File Name: front.py
#
# Date: April 27, 2022


# Importing Libraries
import requests
import sys


# Base URL
URL = 'http://127.0.0.1:8000/v1_0/'


def resource_name(book):
    '''
    This function converts the user's choice of resource into the resource 
    name as stored in the database.

    Inputs:
        book (string): user's choice of resource.

    Returns:
        (string) the name of the resource.
    '''

    if book == "W" or book == "w":
        return 'workshop'

    if book == "M" or book == "m":
        return 'microvac'

    if book == "I" or book == "i":
        return 'irradiator'

    if book == "P" or book == "p":
        return 'extruder'

    if book == "C" or book == "c":
        return 'hvc'

    if book == "H" or book == "h":
        return 'harvester'
    
    return book


def confirm(conf):
    '''
    This function checks if the user wants to go ahead with the prompt

    Inputs:
        conf (string): user response to prompt.

    Returns: 
        (string) "Yes" or "No" based on user input.
    '''

    if conf == 'Y' or conf == 'y':
        return "Yes"
    elif conf =='N' or conf == 'n':
        return "No"


def print_details(json_object):
    '''
    This function prints the reservation details of a user on the console.

    Inputs:
        json_object (JSON): json object of user inputs in the reservation function.

    Returns:
        None.
    '''
    
    # Posting the request
    response = requests.post(URL + "reservations", json = json_object)
    response_info = response.json()

    if response.status_code == 201:
        print("\nYour reservation has been booked")
        print("Reservation details:-")
        print("Reservation ID  : {}".format(response_info["detail"]["reservation_id"]))
        print("Discount Percent: {}".format(response_info["detail"]["discount"]))
        print("Total Cost  ($) : {}".format(response_info["detail"]["total_cost"]))
        print("Downpayment ($) : {}".format(response_info["detail"]["down_payment"]))
    else: 
        print(response_info["detail"])


def reservation():
    '''
    This function displays the reservation menu for all resources, and lets 
    the user input the necessary information in order to make the reservation.

    Inputs:
        None.

    Returns:
        None.
    '''

    # Reservation Menu
    print("\nEquipment in facility:")
    print("Press W for workshop")
    print("Press M for mini microvacs")
    print("Press I for irradiators")
    print("Press P for polymer extruders")
    print("Press C for high velocity crusher")
    print("Press H for 1.21 gigawatt lightning harvester")
    print("Press E for exit")

    # User Inputs
    book = input("\nPick item for reserving: ")

    if book == "E" or book == "e":
        main() 

    name = input("\nEnter your name: ") 
    resource = resource_name(book) 

    startdate = input("Enter reservation start date (mm-dd-yyyy): ")
    starttime = input("Enter reservation start time (24 hr format - hh:mm): ")
    print("\nStart date and time entered: ")
    print("Date: {} || Time: {}".format(startdate, starttime))

    print("\nEntering an end time is optional.")
    print("By default, we will book a 30 minute slot for you.")
    conf = input("Do you still want to enter the end time? [y/n]: ")
    while conf not in ['Y', 'y', 'N', 'n']:
        print("Please enter valid input: y or n")
        conf = input("Do you still want to enter the end time? [y/n]: ")
    check = confirm(conf) 
    
    if check == "Yes":
        endtime = input("\nEnter reservation end time (24 hr format - hh:mm) for the same day: ")
        print("\nEnd time entered: ")
        print("Time: {}".format(endtime))
          
    else:
        endtime = None
        
    json_object = {
        "customer_id": name, 
        "resource": resource, 
        "start_date": startdate,
        "start_time": starttime, 
        "end_time": endtime
    }

    print_details(json_object)


def recurring_reservations():
    '''
    This function displays the reservation menu for all resources, and lets the
    user input the necessary information in order to make a recurring reservation.

    Inputs:
        None.

    Returns:
        None.
    '''

    # Reservation Menu
    print("\nEquipment in facility:")
    print("Press W for workshop")
    print("Press M for mini microvacs")
    print("Press I for irradiators")
    print("Press P for polymer extruders")
    print("Press C for high velocity crusher")
    print("Press H for 1.21 gigawatt lightning harvester")
    print("Press E for exit")

    # User Inputs
    book = input("\nPick item for reserving: ")

    if book == "E" or book == "e":
        main() 

    name = input("\nEnter your name: ") 
    resource = resource_name(book) 

    startdate = input("Enter recurring reservation start date (mm-dd-yyyy): ")
    starttime = input("Enter recurring reservation start time (24 hr format - hh:mm): ")
    print("\nStart date and time entered: ")
    print("Date: {} || Time: {}".format(startdate, starttime))

    enddate = input("Enter recurring reservation end date (mm-dd-yyyy): ")
    endtime = input("Enter recurring reservation end time (24 hr format - hh:mm): ")
    print("\nEnd date and time entered: ")
    print("Date: {} || Time: {}".format(enddate, endtime))

    json_object = {
        "customer_id": name,
        "resource": resource, 
        "start_date": startdate,
        "end_date": enddate,
        "start_time": starttime, 
        "end_time": endtime
    }

    print_details(json_object)


def cancellation():
    '''
    This function cancels a reservation based on the user's reservation ID.

    Inputs:
        None.

    Returns:
        None.
    '''

    # User Inputs
    res_id = input("\nEnter the Reservation ID you want to cancel: ")
    
    conf = input("Do you want to confirm the cancellation? [y/n]: ")
    while conf not in ['Y', 'y', 'N', 'n']:
        print("Please enter valid input: y or n")
        conf = input("Do you want to confirm the cancellation? [y/n]: ")
    check = confirm(conf) 

    if check == "No":
        main()
    else:
        json_object = {
            "reservation_id": res_id
        }
        
        # Deleting the request
        response = requests.delete(URL + 'reservations', json = json_object)
        response_info = response.json()

        if response.status_code == 200:
            print("\nYour reservation has been canceled")
            print("Cancellation details:-")
            print("Refund Percent  : {}".format(response_info["detail"]["percent_returned"]))
            print("Refund Amount($): {}".format(response_info["detail"]["refund"]))
        else: 
            print(response_info["detail"])


def get_daterange():
    '''
    This function gets a date range from the user.

    Inputs:
        None.

    Returns:
        (string) the start date.
        (string) the end date. 
    '''
    
    print("\nEntering a start date and end date is optional.")
    print("By default, the start date is set to today and the end date is set to 7 days from the start date.")
    
    # User Inputs
    conf = input("\nDo you want to enter a start date? [y/n]: ")
    while conf not in ['Y', 'y', 'N', 'n']:
        print("Please enter valid input: y or n")
        conf = input("Do you want to enter a start date? [y/n]: ")
    check = confirm(conf) 
    
    if check == "Yes":
        startdate = input("Enter the start date (mm-dd-yyyy): ")
        print("\nStart date: ")
        print("Date: {}".format(startdate))
    
    else:
        startdate = None

    conf = input("Do you want to enter an end date? [y/n]: ")
    while conf not in ['Y', 'y', 'N', 'n']:
        print("Please enter valid input: y or n")
        conf = input("Do you want to enter an end date? [y/n]: ")
    check = confirm(conf) 
    
    if check == "Yes":
        enddate = input("Enter the end date (mm-dd-yyyy): ")
        print("\nEnd date: ")
        print("Date: {}".format(enddate))
    
    else:
        enddate = None
    
    return startdate, enddate


def all_reservations_for_user():
    '''
    This function lets the user input the necessary information 
    to display all the reservations within a date range.

    Inputs:
        None.

    Returns:
        None.
    '''

    # User Inputs
    name = input("\nEnter your name (Leave blank and press enter for all users): ") 
    startdate, enddate = get_daterange()
    json_object = {
        "start_date": startdate,
        "end_date": enddate,
        "customer_id": name 
    }

    response = requests.get(URL + 'reservations', params = json_object)
    response_info = response.json()
    
    results_per_page = 5

    if response.status_code == 200 and len(response_info["detail"]["reservations"]) > 0:
        print("\nReport of current reservations for "+ name +":-")

        n = len(response_info["detail"]["reservations"])
        more = True
        i = 0

        while (more and n > 0):
            if n < results_per_page:
                for j in range(i, i + n):
                    reservation = response_info["detail"]["reservations"][j]
                    print("Reservation ID  : {}".format(reservation["reservation_id"]))
                    print("Customer ID     : {}".format(reservation["customer_id"]))
                    print("Resource        : {}".format(reservation["resource"]))
                    print("Start date      : {}".format(reservation["start_date"]))
                    print("End date        : {}".format(reservation["end_date"]))
                    print("Start time      : {}".format(reservation["start_time"]))
                    print("End time        : {}".format(reservation["end_time"]))
                    print("Total Cost  ($) : {}".format(reservation["total_cost"]))
                    print("Downpayment ($) : {}".format(reservation["down_payment"]))
                    print("\n")
                    more = False
            else:
                for j in range(i, i + results_per_page):
                    reservation = response_info["detail"]["reservations"][j]
                    print("Reservation ID  : {}".format(reservation["reservation_id"]))
                    print("Customer ID     : {}".format(reservation["customer_id"]))
                    print("Resource        : {}".format(reservation["resource"]))
                    print("Start date      : {}".format(reservation["start_date"]))
                    print("End date        : {}".format(reservation["end_date"]))
                    print("Start time      : {}".format(reservation["start_time"]))
                    print("End time        : {}".format(reservation["end_time"]))
                    print("Total Cost  ($) : {}".format(reservation["total_cost"]))
                    print("Downpayment ($) : {}".format(reservation["down_payment"]))
                    print("\n")
                
                i = i + results_per_page
                n = n - results_per_page
                        
                if (n > 0):
                    conf = input("Do you want to view the next 5 reservations? [y/n]: ")
                    while conf not in ['Y', 'y', 'N', 'n']:
                        print("Please enter valid input: y or n")
                        conf = input("Do you want to view the next 5 reservations? [y/n]: ")
                    check = confirm(conf)

                    if check == "Yes":
                        continue

                    else:
                        more = False
                else:
                    more = False
        
    elif response.status_code == 200 and len(response_info["detail"]["reservations"]) == 0:
        print("Currently, there aren't any reservations in the system.")

    else: 
        print(response_info["detail"])


def financial_transactions():
    '''
    This function lets the user input the necessary information 
    to display all the financial transactions within a date range.

    Inputs:
        None.

    Returns:
        None.
    '''

    startdate, enddate = get_daterange()
    json_object = {
        "start_date": startdate,
        "end_date": enddate
    }

    response = requests.get(URL + 'transactions', params = json_object)
    response_info = response.json()
    
    results_per_page = 5

    if response.status_code == 200 and len(response_info["detail"]["transactions"]) > 0:
        print("\nReport of all the financial transactions:-")
        n = len(response_info["detail"]["transactions"])
        more = True
        i = 0

        while (more and n > 0):
            if n < results_per_page:
                for j in range(i, i + n):
                    transaction = response_info["detail"]["transactions"][j]
                    print("Transaction ID        : {}".format(transaction["transaction_id"]))
                    print("Transaction Type      : {}".format(transaction["transaction_type"]))
                    print("Transaction date      : {}".format(transaction["transaction_date"]))
                    print("Reservation ID        : {}".format(transaction["reservation_id"]))
                    print("Customer ID           : {}".format(transaction["customer_id"]))
                    print("Resource              : {}".format(transaction["resource"]))
                    print("Total Cost         ($): {}".format(transaction["total_cost"]))
                    print("Transaction Amount ($): {}".format(transaction["transaction_amount"]))
                    print("\n")
                    more = False
            else:
                for j in range(i, i + results_per_page):
                    transaction = response_info["detail"]["transactions"][j]
                    print("Transaction ID        : {}".format(transaction["transaction_id"]))
                    print("Transaction Type      : {}".format(transaction["transaction_type"]))
                    print("Transaction date      : {}".format(transaction["transaction_date"]))
                    print("Reservation ID        : {}".format(transaction["reservation_id"]))
                    print("Customer ID           : {}".format(transaction["customer_id"]))
                    print("Resource              : {}".format(transaction["resource"]))
                    print("Total Cost         ($): {}".format(transaction["total_cost"]))
                    print("Transaction Amount ($): {}".format(transaction["transaction_amount"]))
                    print("\n")
                
                i = i + results_per_page
                n = n - results_per_page
                        
                if (n > 0):
                    conf = input("Do you want to view the next 5 financial transactions? [y/n]: ")
                    while conf not in ['Y', 'y', 'N', 'n']:
                        print("Please enter valid input: y or n")
                        conf = input("Do you want to view the next 5 financial transactions? [y/n]: ")
                    check = confirm(conf)

                    if check == "Yes":
                        continue

                    else:
                        more = False
                else:
                    more = False
                    
    elif response.status_code == 200 and len(response_info["detail"]["transactions"]) == 0:
        print("Currently, there aren't any financial transactions in the system.")
    else: 
        print(response_info["detail"])

def main():
    '''
    This function displays the Main Menu for MPCS Inc. Reservation System

    Inputs:
        None.

    Returns:
        None.
    '''
    
    choice = "100"

    while (choice != "6"):
        
        print("\nSelect task you want to perform:")
        print("Enter 1 to make a reservation")
        print("Enter 2 to make a recurring reservation")
        print("Enter 3 to cancel a reservation")
        print("Enter 4 to generate report of the current reservations over a particular time period")
        print("Enter 5 to get financial transactions over a particular time period")
        print("Enter 6 to exit\n")

        choice = input("Enter your option: ")

        if choice == "1":
            reservation()

        elif choice == "2":
            recurring_reservations()

        elif choice == "3":
            cancellation()

        elif choice == "4":
            all_reservations_for_user()

        elif choice == "5":
            financial_transactions()

    sys.exit("\nThank you for using the MPCS Inc. Reservation System")

if __name__ == "__main__":
    # Calling the main execution
    main()

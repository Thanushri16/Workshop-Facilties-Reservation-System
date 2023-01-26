# G-01: API-ify the Reservation System
#
# Group Name: 404 Team Not Found
#
# File Name: reserve.py
#
# Date: April 30, 2022

from datetime import datetime, timedelta
from fastapi import HTTPException

class Reservation:
    """
    A class representing a single reservation within the system

    All dates stored are in the form of a mm-dd-yyyy string
    Attributes:
        reservation_id (int): A unique interger for each reservation
        customer_id (str): The unique string id representing a customer
        reservation_type (str): The type of reservation made (for workshop,
            or for a special machine)
        start_date (str): The starting date of the reservation 
        end_date (str): The ending date of the reservation
        date_of_reservation (str): The date on which the reservation is made
        total (float): A float representing the total cost of this reservation
        down_payment (float): A float representing the amount required for a down payment
        reservation_string (str): A string representation of the reservation object
    """
    def __init__(self, _reserve):
        self.reservation_id = int(_reserve[0])
        self.customer_id = _reserve[1]
        self.reservation_type = _reserve[2]
        self.start_date = _reserve[3]
        self.end_date = _reserve[4]
        self.start_time = _reserve[5]
        self.end_time = _reserve[6]
        self.date_of_reservation = _reserve[7]
        self.discount = 0
        self.total_cost = float(_reserve[8]) if len(_reserve) > 8 else self.calculate_total_cost()
        self.down_payment = float(_reserve[9]) if len(_reserve) > 9 else self.calculate_down_payment()
        self.reservation_string = ' '.join(_reserve)
        if len(_reserve) <= 8:
            self.reservation_string += f' {self.total_cost} {self.down_payment}'

    def calculate_total_cost(self):
        """
        Calculate the total cost based on the current Reservation object

        Returns:
            A float amount in dollars
        """
        
        start_date = datetime.strptime(self.start_date, "%m-%d-%Y")
        end_date = datetime.strptime(self.end_date, "%m-%d-%Y")
        date_of_reservation = datetime.strptime(self.date_of_reservation, "%m-%d-%Y")
        
        # Note that if the reservation start date and end date are different days
        # It is considered to be multiple appointments from start_time to end_time
        # for each of those days, not from start_day start_time to end_day end_time
        days = (end_date - start_date).days + 1
        start_hour, start_minute = map(int, self.start_time.split(':'))
        end_hour, end_minute = map(int, self.end_time.split(':'))

        # Number of half hour blocks for this reservation
        half_hours = (end_hour - start_hour) * 2
        half_hours += -start_minute // 30 + end_minute // 30
        half_hours *= days

        # Base price
        total_cost = 0
        if self.reservation_type == 'workshop':
            total_cost = half_hours * 99 / 2
        elif self.reservation_type == 'microvac':
            total_cost = half_hours * 1000 / 2
        elif self.reservation_type == 'irradiator':
            total_cost = half_hours * 2220 / 2
        elif self.reservation_type == 'extruder':
            total_cost = half_hours * 600 / 2
        elif self.reservation_type == 'hvc':
            total_cost = half_hours * 10000
        elif self.reservation_type == 'harvester':
            total_cost = half_hours * 8800 / 2
        else:
            print(f"Unsupported resource: {self.reservation_type}.")

        # Discount by 75% if reservation is made 14 days in advance
        if (start_date - date_of_reservation).days >= 14:
            total_cost *= 0.75
            self.discount = 25
        
        return total_cost

    def calculate_down_payment(self):
        """
        Calculate the amount of down payment that needs to be made
        based on the total cost of the reservation
        
        Returns:
            A float amount in dollars
        """
        if self.reservation_type == 'workshop':
            return 0
        return self.total_cost * 0.5
    
    def tolist(self):
        """
        Convert all information in the Reservation object to a list object

        Returns:
            A string that includes all information about the Reservation object
        """
        return [str(self.reservation_id), self.customer_id, self.reservation_type,
                    self.start_date, self.end_date, self.start_time, self.end_time,
                    self.date_of_reservation, str(self.total_cost), str(self.down_payment)]

class ReservationManager:
    """
    A class to manage all the reservations within the system

    Attributes:
        reservations (Reservation): A list that tracks all existing
            Reservation objects in the system
    """

    def __init__(self):
        self.reservations = []

    def add_reservation(self, reservation: Reservation):
        """
        Add a new reservation to the list of reservations kept by the Reservation Manager
        """
        # If the reservation is a list, convert it to a Reservation object
        # Otherwise append it straight to the list of reservations
        if type(reservation) == type([]):
            self.reservations.append(Reservation(reservation))
        else:
            self.reservations.append(reservation)

    def new_id(self):
        """
        Generate a new id based on the number of registrations already in the system

        Returns:
            A unique integer ID for a new reservation
        """
        if len(self.reservations) == 0:
            return 1
        return self.reservations[-1].reservation_id + 1
    
    def save_to_file(self, file):
        """
        Write all current reservations to the designated file descriptor
        """
        for reservation in self.reservations:
            file.write(reservation.reservation_string)
            file.write('\n')

    def generate_reservations_report(self, start_date, end_date, customer_id):
        """
        Generate a JSON report of all reservations in the system based
        Formatted according to the API design dcoument

        Args:
            start_date (str): The starting date of reservations to report on 
            end_date (str): The ending date of reservations to report on
            customer_id (str): OPTIONAL, the customer ID to generate report on

        Returns:
            A JSON formatted report in accordance with API design document for
            the 'GET reservations' API endpoint
        """
        list_reservation_data = []
        for reservation in self.reservations:
            # If customer id matches or not specified
            if (customer_id == "" or reservation.customer_id == customer_id):
                # Print all reservations between this date
                if between(reservation.start_date, start_date, end_date):
                    list_reservation_data.append({
                        "reservation_id":reservation.reservation_id,
                        "customer_id": reservation.customer_id,
                        "resource": reservation.reservation_type,
                        "start_date": reservation.start_date,
                        "end_date": reservation.end_date,
                        "start_time": reservation.start_time,
                        "end_time": reservation.end_time,
                        "total_cost": reservation.total_cost, 
                        "down_payment": reservation.down_payment
                    })
        return {"reservations": list_reservation_data}

    
class Transaction:
    """
    A class representing transactions that have taken place in the system

    Attributes:
        transaction_id (int): A unique interger for each transaction
        type (str): The type of transaction (CANCELLATION or RESERVATION)
        transaction_date (str): Date of the transaction in mm-dd-yyyy format
        detail (Reservation): The Reservation object related to this transaction
        reservation_string (str): A string representation of the reservation
            related to this transaction
    """
    def __init__(self, transaction):
        self.transaction_id = int(transaction[0])
        self.type = transaction[1]
        self.transaction_date = transaction[2]
        self.detail = Reservation(transaction[3:])
        self.reservation_string = f'{self.transaction_id} {self.type} {self.transaction_date} {self.detail.reservation_string}'

class Transaction_Manager:
    """
    A class to manage all the transaction within the system

    Attributes:
        transactions ([Transaction]): A list that tracks all existing
            Transaction objects in the system
    """
    def __init__(self):
        self.transactions = []

    def add_transaction(self, transaction):
        """
        Add a new transaction to the list kept by the Transaction Manager
        """
        self.transactions.append(Transaction(transaction))
    
    def new_id(self):
        """
        Generate a new id based on the number of registrations already in the system

        Returns:
            A unique integer ID for a new reservation
        """
        return len(self.transactions) + 1
    
    def save_to_file(self, file):
        """
        Write all current transactions to the designated file descriptor
        """
        for transaction in self.transactions:
            file.write(transaction.reservation_string)
            file.write('\n')

    def create_refund(self, cancelled_reservation, cancel_date):
        """
        Given a cancelled reservation and the date on which the cancellation ismade
        Calculate the amount that should be refunded and make the refund by
        recording it as a cancellation transaction

        Args:
            cancelled_reservation (Reservation): The reservation to refund
            cancel_date (str): the date on which the cancellation is requested
        """
        # print refund
        start_date = datetime.strptime(cancelled_reservation.start_date, "%m-%d-%Y")
        cancel_datetime = datetime.strptime(cancel_date, "%m-%d-%Y")
        refund = 0
        days_before_reservation = (start_date - cancel_datetime).days

        percent_returned = 0
        # calculate the amount of refund based on how many days ahead
        if days_before_reservation >= 7:
            percent_returned = 75
            refund = 0.75 * cancelled_reservation.down_payment
        elif days_before_reservation >= 2:
            percent_returned = 50
            refund = 0.5 * cancelled_reservation.down_payment
        print(f"Cancellation succeeded! Refund: ${refund}")

        # add a cancellation transaction
        transaction_info = [self.new_id(), f'CANCELLATION${refund}', cancel_date] + cancelled_reservation.tolist()
        self.add_transaction(transaction_info)
        return percent_returned, refund


    def generate_transactions_report(self, start_date, end_date):
        """
        Generate a JSON report of all transactions in the system based
        Formatted according to the API design given in web.py

        Args:
            start_date (str): The starting date of transaction to report on 
            end_date (str): The ending date of transactions to report on

        Returns:
            A JSON formatted report in accordance with API design document for
            the 'GET transactions' API endpoint
        """
        list_transaction_data = []
        for transaction in self.transactions:
            if between(transaction.transaction_date, start_date, end_date):
                reservation = transaction.detail
                transaction_type = transaction.type.split("$")
                transaction_amount = reservation.down_payment
                if len(transaction_type) == 2:
                    transaction_amount = transaction_type[1]
                transaction_type = transaction_type[0]

                list_transaction_data.append({
                    "transaction_id": transaction.transaction_id,
                    "transaction_type": transaction_type,
                    "transaction_date": transaction.transaction_date,
                    "reservation_id": reservation.reservation_id,
                    "customer_id": reservation.customer_id,
                    "resource": reservation.reservation_type,
                    "total_cost": reservation.total_cost,
                    "transaction_amount": transaction_amount
                })
        return {"transactions": list_transaction_data}

def workshop_is_closed(start_time, end_time, date):
    """
    Given the date, start and end time of a reservation, determine if the
    workshop is going to be open for the duration of the reservation

    Returns: 
        (bool) True if workshop is open, False otherwise
    """
    if date.weekday() == 6:
        return True
    if date.weekday() == 5 and (start_time < 100 or end_time > 160):
        return True
    return start_time < 90 or end_time > 180
        
def split_time(start, end):
    """
    Split the start and end time into an integer representation
    E.g. 150 represents 15:00, 105 represents 10:30

    Args:
        Arguments are of format HH:MM
        start (str): The start time
        end (str): The end time
    
    Returns:
        Integer representation of the start time and end time
    """
    start_hour, start_minute = map(int, start.split(':'))
    end_hour, end_minute = map(int, end.split(':'))
    start_time = start_hour * 10 + start_minute // 30 * 5
    end_time = end_hour * 10 + end_minute // 30 * 5
    return start_time, end_time

def is_available(reservation_type, count):
    """
    Given the type of reservation and the number of bookings already made for
    that type of workshop/equipment, determine if it is still available for booking

    Args:
        reservation_type (str): The type of resource to reserve
        count (int): The number of reservations already made for that resource

    Returns:
        (bool) True if the workshop/equipment is still available, False otherwise
    """
    if reservation_type == 'workshop':
        return count <= 15
    elif reservation_type == 'microvac':
        return count <= 2
    elif reservation_type == 'irradiator':
        return count <= 2
    elif reservation_type == 'extruder':
        return count <= 3
    elif reservation_type == 'hvc':
        return count <= 1
    elif reservation_type == 'harvester':
        return count <= 1
    print(f"Unsupported resource: {reservation_type}.")
    return False

def between(date, start, end):
    """
    Given three date strings, determine if the first date is between the
    start (second) and the end (third) date

    Args:
        All arguments are strings of the format MM-DD-YYYY
        date (str): The date to check for
        start (str): The start date
        end (str): The end date

    Returns:
        True if it is between the start and end date, False otherwise
    """
    start_date = datetime.strptime(start, "%m-%d-%Y")
    end_date = datetime.strptime(end, "%m-%d-%Y")
    ddate = datetime.strptime(date, "%m-%d-%Y")
    return (ddate - start_date).days >= 0 and (end_date - ddate).days >=0

def reservation_is_not_in_date_range(reservation_datetime, start_datetime, end_datetime):
    """
    Given all dates of a reservation to be made, check if it is within the
    allowed date range (0 to 30 days in advance)

    Args:
        Contraint: All inputs are datetime objects
        reservation_datetime (datetime): The date on which the reservation is made
        start_datetime (datetime): The first day of the reservation
        end_datetime (datetime): The last day day of the reservation

    Returns:
        (bool) False if it is between the allowed date range, True otherwise
    """
    # Check if reservation is in the future
    if (reservation_datetime - start_datetime).days > 0:
        print('Reservation Failed: cannot reserve time already passed.')
        handle_error(400, "Reservation", 'Cannot reserve time already passed.')
    
    # Check if reservation is within 30 days
    if (end_datetime - reservation_datetime).days > 30:
        # "Clients expect to be able to make reservations up to 30 days in advance"
        print('Reservation Failed: cannot reserve time more than 30 days away.')
        handle_error(400, "Reservation", 'Cannot reserve time more than 30 days away.')
    
    return False

def reservation_type_is_not_known(reservation_type):
    """
    Check if the reservation type is valid

    Args:
        reservation_type (str):The workshop/resouce type to reserve

    Returns:
        (bool) True if it is owned by the workshop, False otherwise
    """
    if reservation_type not in ['workshop', 'microvac', 'irradiator', 'extruder', 'hvc', 'harvester']:
        print(f"Unsupported resource: {reservation_type}.")
        handle_error(400, "Reservation", f"Unsupported resource: {reservation_type}")
    return False

def reservation_is_not_on_half_hour(minute):
    """
    Check if a reservation is made on the half hour

    Args:
        reservation_type (int): The minute mark of a reservation

    Returns:
        True if it is on the half hour, False otherwise
    """
    if minute != 0 and minute != 30:
        print('Reservation Failed: reservations for all resources are made in 30 minute blocks and always start on the hour or half hour.')
        handle_error(400, "Reservation", f"Reservations for all resources are made in 30 minute blocks and always start on the hour or half hour")
    return False

def check_only_one_special_machine(reservation_manager, days_to_reserve, reservation):
    """
    Check that there is only one special machine reserved by a single client
    at any given time

    Args:
        reservation_manager (ResevationManager): the reservation manager of the system
        days_to_reserve (int): All the days this reservation is trying to make
        reservation (Reservation): Reservation Object for this reservation

    Returns:
        (bool) True if only no special machine has been reserved, False otherwise
    """
    customer_id = reservation.customer_id
    reservation_type = reservation.reservation_type
    start_time, end_time = split_time(reservation.start_time, reservation.end_time)

    for day in days_to_reserve:
        for reservation in reservation_manager.reservations:
            if reservation.customer_id != customer_id:
                continue
            if reservation_type == 'workshop':
                continue
            if not between(f'{day.month}-{day.day}-{day.year}', reservation.start_date, reservation.end_date):
                continue
            reservation_start, reservation_end = split_time(reservation.start_time, reservation.end_time)
            if not (reservation_end <= start_time or end_time <= reservation_start):
                # "They can only reserve one special machine at a time"
                print('Reservation Failed: a client can only reserve one special machine at a time')
                handle_error(400, "Reservation", "A client can only reserve one special machine at a time")
    return True

def over_three_reservations(reservation_manager, days_to_reserve, customer_id):
    """
    Check if a customer is going to go over the limit of three reservations for
    a single week, given that they are trying to make reservations given by
    days_to_reserve

    Args:
        reservation_manager (ResevationManager): the reservation manager of the system
        days_to_reserve (int): All the days this reservation is trying to make
        customer_id (str): The customer that is trying to make the reservation

    Returns:
        (bool) False if the customer is not going to go over the three days
        restriction, True if they are going to go over the restriction
    """
    weekr = {}
    # Count up the number of reservations that this customer has already made
    for reservation in reservation_manager.reservations:
        if reservation.customer_id != customer_id:
            continue
        reservation_start_datetime = datetime.strptime(reservation.start_date, "%m-%d-%Y")
        reservation_end_datetime = datetime.strptime(reservation.end_date, "%m-%d-%Y")
        rdays = []
        rcur = reservation_start_datetime
        while (reservation_end_datetime - rcur).days >= 0:
            rdays.append(rcur)
            rcur += timedelta(days=1)
        for day in rdays:
            key = f'{day.year}-{day.isocalendar()[1]}'
            if key not in weekr:
                weekr[key] = 1
            else:
                weekr[key] += 1
    # Add the days that are going to be reserved now
    for day in days_to_reserve:
        key = f'{day.year}-{day.isocalendar()[1]}'
        if key not in weekr:
            weekr[key] = 1
        else:
            weekr[key] += 1
    # Check if it is going to go over three
    for k in weekr:
        if weekr[k] > 3:
            print(f'Reservation Failed: A client can only make reservations for 3 different days in a given week.')
            handle_error(400, "Reservation", "A client can only make reservations for 3 different days in a given week")
            
    return False

def check_non_cooldown_requirements(reservation_manager, day, reservation_type, start_time, end_time):
    """
    Given the day of reservation, type of reservation and the start and end time, check all
    the non-cooldown related rules that must be applied to the reservation, if the rules
    correctly applies without error, return True, return False if there exists some error
    and the reservation cannot be made

    Args:
        reservation_manager (ReservationManager): The reservation manager of the system
        day (datetime): the datetime object of the day that is being checked
        reservation_type (str): the machine/workshop to make reservation for
        start_time (str): the start time of this reservation
        end_time (str): the finish time of this reservation

    Returns:
        (bool) False if the reservation violates some requirement, True otherwise
    """
    for t in range(start_time, end_time, 5):
        count = 0
        s_cnt = 0
        h_run = False
        for reservation in reservation_manager.reservations:
            reservation_start, reservation_end = split_time(reservation.start_time, reservation.end_time)
            if not (t >= reservation_start and t < reservation_end):
                continue
            if not between(f'{day.month}-{day.day}-{day.year}', reservation.start_date, reservation.end_date):
                continue
            if reservation.reservation_type == 'harvester':
                h_run = True
            if reservation.reservation_type != 'workshop':
                # increament special_count by 1
                s_cnt += 1
            if reservation.reservation_type == reservation_type:
                # increament count by 1
                count += 1
        if not is_available(reservation_type, count+1):
            print(f'Reservation Failed: not enough available {reservation_type}, {count} already reserved.')
            handle_error(400, "Reservation", f'Not enough available {reservation_type}, {count} already reserved')
            
        if reservation_type == 'irradiator' and count == 1:
            print('Reservation Failed: only 1 irradiator can be used at a time.')
            handle_error(400, "Reservation", 'Only 1 irradiator can be used at a time')
            
        if reservation_type != 'workshop':
            s_cnt += 1
        if h_run and s_cnt > 4:
            print('Reservation Failed: only 3 other machines can run while the 1.21 gigawatt lightning harvester is operating.')
            handle_error(400, "Reservation", 'Only 3 other machines can run while the 1.21 gigawatt lightning harvester is operating')
            
    return True

def check_hvc_requirements(reservation_manager, day, start_time, end_time):
    """
    Given a start time and an end time, check that on a given day, the hvc machine
    is used in accordance with the cooldown rules

    Args:
        reservation_manager (ReservationManager): The reservation manager of the system
        day (datetime): the datetime object of the day that is being checked
        start_time (str): the start time of this reservation
        end_time (str): the finish time of this reservation

    Returns:
        (bool) True if the hvc is being operated within requirements, False otherwise
    """
    hvc_start = start_time - 60
    hvc_end = end_time + 60
    for reservation in reservation_manager.reservations:
        if reservation.reservation_type == 'hvc':
            if not between(f'{day.month}-{day.day}-{day.year}', reservation.start_date, reservation.end_date):
                continue
            reservation_start, reservation_end = split_time(reservation.start_time, reservation.end_time)
            if not (hvc_end <= reservation_start or reservation_end <= hvc_start):
                print(f'Reservation Failed: high velocity crusher needs to cool down for 6 hours between uses, hvc currently reserved for {reservation.start_time}-{reservation.end_time}.')
                handle_error(400, "Reservation", f'High velocity crusher needs to cool down for 6 hours between uses, hvc currently reserved for {reservation.start_time}-{reservation.end_time}.')
                
    return True

def check_irradiator_requirements(reservation_manager, day, start_time, end_time):
    """
    Given a start time and an end time, check that on a given day, the irradiator
    is used in accordance with the cooldown rules

    Args:
        reservation_manager (ReservationManager): The reservation manager of the system
        day (datetime): the datetime object of the day that is being checked
        start_time (str): the start time of this reservation
        end_time (str): the finish time of this reservation

    Returns:
        (bool) True if the irradiator is being operated within requirements, False otherwise
    """
    irradiator_start = start_time - 10
    irradiator_end = end_time + 10
    count = 0
    for reservation in reservation_manager.reservations:
        if reservation.reservation_type == 'irradiator':
            if not between(f'{day.month}-{day.day}-{day.year}', reservation.start_date, reservation.end_date):
                continue
            reservation_start, reservation_end = split_time(reservation.start_time, reservation.end_time)
            if not (irradiator_end <= reservation_start or reservation_end <= irradiator_start):
                count += 1
    if count == 2:
        print(f'Reservation Failed: irradiators need to cool down for 1 hour between uses.')
        handle_error(400, "Reservation","Irradiators need to cool down for 1 hour between uses")
        
    return True

def handle_reservation(reservation_manager, reservation):
    """
    Given a reservation, check all conditions to see if it is a valid reservation
    that does not break any of the reservation rules

    Args:
        reservation_manager (ReservationManager): The reservation manager of the system
        reservation (Reservation): The reservation to be made

    Returns:
        (bool) True if it is the reservation can be made in accordance to all
        the rules, False otherwise
    """
    # Unpack all required data from the Reservation object
    customer_id = reservation.customer_id
    reservation_type = reservation.reservation_type
    start_datetime = datetime.strptime(reservation.start_date, "%m-%d-%Y")
    end_datetime = datetime.strptime(reservation.end_date, "%m-%d-%Y")
    start_time = reservation.start_time
    end_time = reservation.end_time
    reservation_datetime = datetime.strptime(reservation.date_of_reservation, "%m-%d-%Y")

    # Check if the type of machine is known
    if reservation_type_is_not_known(reservation_type):
        return False

    if reservation_is_not_in_date_range(reservation_datetime, start_datetime, end_datetime):
        return False
    
    # Convert hour and minue to form 105 for 10:30, 160 for 16:00
    original_start_time = start_time
    original_end_time = end_time
    start_hour, start_minute = map(int, start_time.split(':'))
    end_hour, end_minute = map(int, end_time.split(':'))
    start_time = start_hour * 10 + start_minute // 30 * 5
    end_time = end_hour * 10 + end_minute // 30 * 5

    if reservation_is_not_on_half_hour(start_minute) or reservation_is_not_on_half_hour(end_minute):
        return False

    # A list of days to make reservations for, based on start date and end date
    days_to_reserve = []
    cur = start_datetime
    while (end_datetime - cur).days >= 0:
        days_to_reserve.append(cur)
        cur += timedelta(days=1)
    
    # Check if the workshop is open for each of the reservation days
    for day in days_to_reserve:
        if workshop_is_closed(start_time, end_time, day):
            print(f'Reservation Failed: cannot reserve time interval from {original_start_time} to {original_end_time} on {str(day).split()[0]}')
            handle_error(400, "Reservation", f'Cannot reserve time interval from {original_start_time} to {original_end_time} on {str(day).split()[0]}')
    
    # Make sure that one client only makes one special machine reservation at any time
    if not check_only_one_special_machine(reservation_manager, days_to_reserve, reservation):
        return False
    
    # For each day in the attempted reservation, check that it does not violate some
    # requirement for booking to be successful
    for day in days_to_reserve:
        # Check that all non-cooldown rules for a reservation
        if not check_non_cooldown_requirements(reservation_manager, day, reservation_type, start_time, end_time):
            return False
        
        # check that the high velocity crusher has 6 hours cooldown between uses
        if reservation_type == 'hvc':
            if not check_hvc_requirements(reservation_manager, day, start_time, end_time):
                return False
    
        # check that irradiators have a 60 minutes cooldown period after use
        if reservation_type == 'irradiator':
            if not check_irradiator_requirements(reservation_manager, day, start_time, end_time):
                return False
    
    # Check if A customer is going to go over 3 reservations in a given week
    if over_three_reservations(reservation_manager, days_to_reserve, customer_id):
        return False
    
    return True

def load_data_from_file(reservation_manager, transactions_manager):
    """
    Given empty reservation manager and transaction manager, load from data.txt
    file all of the reservations and transactions saved in the system

    Args:
        reservation_manager (ReservationManager): the reservation manager of
            the system to load reservations into
        transactions_manager (TransactionManager): the transactions manager of
            the system to load transactions into
    """
    file = open("data/data.txt", 'r')
    lines = file.readlines()
    # Read every line from data file, with a hash # seperating the reservations
    # from the transactions
    convert_to_reservation = True
    for line in lines:
        line = line.split()
        if line[0] == '#':
            convert_to_reservation = False
            continue
        if convert_to_reservation:
            reservation_manager.add_reservation(line)
        else:
            transactions_manager.add_transaction(line)
    file.close()

def save_date_to_file(reservation_manager, transactions_manager):
    """
    Given the current reservation manager and transaction manager, save all
    data in the system to data.txt

    Args:
        reservation_manager (ReservationManager): the reservation manager of
            the system to load reservations into
        transactions_manager (TransactionManager): the transactions manager of
            the system to load transactions into
    """
    # save_to_file reservation and transaction data, seperated by a hash #
    file = open('data/data.txt', 'w')
    reservation_manager.save_to_file(file)
    file.write('#\n')
    transactions_manager.save_to_file(file)
    file.close()


def handle_request(request):
    """
    Main function of this reservation program, the format of commands are as follows:
    reserve.py reserve <customer_id> <resource> <start_date> <end_date> <start_time> <end_time> <reserve_date>
    reserve.py cancel <reservation_id> <cancel_date>
    reserve.py reservations <start_date> <end_date>
    reserve.py financial <start_date> <end_date>
    reserve.py reservations <start_date> <end_date> <customer_id>
    
    Any date is of the form mm-dd-yyyy
    Any time is of the form hh:mm in 24 hour format

    Handle the above requests by loading the data from data.txt, performing request
    and then saving updated data back into data.txt

    Args:
        request (list): A list of comand and arugments

    Returns:
        response (JSON): A JSON formatted API response
    """

    # Initialize the Reservation and transaction managers by loading all 
    # existing reservations and transactions from the data file
    reservation_manager = ReservationManager()
    transactions_manager = Transaction_Manager()
    
    load_data_from_file(reservation_manager, transactions_manager)

    response = None

    # handle request
    command = request[0]
    if command == 'reserve':
        # Get all the required arguments from the command line
        date_of_reservation = request[7]
        reservation_info = [str(reservation_manager.new_id())] + request[1:]
        new_reservation = Reservation(reservation_info)
        # check if the reservation is possible
        if handle_reservation(reservation_manager, new_reservation):
            # make the reservation
            reservation_manager.add_reservation(new_reservation)
            # add a transaction for this reservation
            transaction_info = [transactions_manager.new_id(), 'RESERVATION', date_of_reservation] + reservation_info
            transactions_manager.add_transaction(transaction_info)
            # print reservation successful message (including total cost and down payment)
            print(f"Reservation succeeded! Reservation id: {new_reservation.reservation_id}, Total cost: ${new_reservation.total_cost}, down payment: ${new_reservation.down_payment}.")
            response = reservation_detail(new_reservation)
        else:
            return
    
    elif command == 'cancel':
        reservation_id = int(request[1])
        cancel_date = request[2]
        found = False
        # cancel the reservation by removing it from the reservation manager
        for i in range(len(reservation_manager.reservations)):
            if reservation_manager.reservations[i].reservation_id == reservation_id:
                found = True
                break
        
        if not found:
            handle_error(400, "Cancellation", f"Invalid reservation id: {reservation_id}")
        
        cancelled_reservation = reservation_manager.reservations[i]
        del reservation_manager.reservations[i]

        # Ask the transaction manager to manage refund and record refund
        percent_returned, refund = transactions_manager.create_refund(cancelled_reservation, cancel_date)

        response = cancellation_detail(percent_returned, refund)
    
    elif command == 'reservations':
        customer_id = ""
        # If a specific customer is indicated
        if len(request) == 4:
            customer_id = request[3]
        response = reservation_manager.generate_reservations_report(request[1], request[2], customer_id)
    
    elif command == 'financial':
        # list transactions between the two dates
        response = transactions_manager.generate_transactions_report(request[1], request[2])
    
    else:
        print(f"Unsupported command: {command}")
        handle_error(400, "Cancellation", f"Invalid request: {command}")
    
    save_date_to_file(reservation_manager, transactions_manager)
    return response


def handle_error(code, operation_name, detail):
    """
    Raise a HTTPException

    Args:
        code (int): status code
        operation_name (str): name of the operation that triggered this error
        detail (str): error message indicating reason of the error
    """
    raise HTTPException(status_code=code, detail=f"{operation_name} failed: {detail}")


def reservation_detail(new_reservation: Reservation):
    """
    Construct detail of a reservation

    Args:
        new_reservation (Reservation): a Reservation object

    Returns:
        A dict object containing detail information of the reservation
    """
    return {
        'reservation_id': str(new_reservation.reservation_id),
        'discount': str(new_reservation.discount),
        'total_cost': str(new_reservation.total_cost),
        'down_payment': str(new_reservation.down_payment)
    }


def cancellation_detail(percent_returned, refund):
    """
    Construct detail of a cancellation

    Args:
        percent_returned (int): percentage of the refund to total cost
        refund (float): money refunded to the customer 

    Returns:
        A dict object containing detail information of the cancellation
    """
    return {
        'percent_returned': str(percent_returned),
        'refund': str(refund)
    }
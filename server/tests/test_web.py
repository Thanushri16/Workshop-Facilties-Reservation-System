from fastapi.testclient import TestClient
import web
import datetime
from datetime import timedelta
from datetime import date

client = TestClient(web.app)

class TestGetReservationsAll:
    '''
    Test both valid and invalid cases for GET /reservations/
    '''
    def test_get_reservations(self):
        #Valid GET reservations request.
        response = client.get("/v1_0/reservations?start_date=4-25-2022")
        assert response.status_code == 200
        assert response.json() == {'status_code': 200, 'detail': {'reservations': [{'reservation_id': 2, 'customer_id': 'hayder2', 'resource': 'hvc', 'start_date': '04-30-2022', 'end_date': '04-30-2022', 'start_time': '12:00', 'end_time': '12:30', 'total_cost': 10000.0, 'down_payment': 5000.0}]}}

    def test_get_reservations_invalid_start_date(self):
        #Invalid GET reservations request due to invalid start date.
        response = client.get("/v1_0/reservations?start_date=19-19-2022")
        assert response.status_code == 400
        assert response.json() == {'detail': 'Get Reservations failed: date format incorrect'}

    def test_get_reservations_invalid_end_date(self):
        #Invalid GET reservations request due to invalid end date.
        response = client.get("/v1_0/reservations?end_date=19-19-2022")
        assert response.status_code == 400
        assert response.json() == {'detail': 'Get Reservations failed: date format incorrect'}


class TestGetTransactionsAll:
    '''
    Test both valid and incalid cases for GET /transactions/
    '''
    def test_get_transations(self):
        #Valid GET transactions request.
        response = client.get("v1_0/transactions")
        assert response.status_code == 200
        print(response.json())
        assert response.json() == {'status_code': 200, \
                                'detail': {'transactions': [{'transaction_id': 1, 'transaction_type': 'RESERVATION', 'transaction_date': '4-30-2022', 'reservation_id': 1, 'customer_id': 'hayder', 'resource': 'extruder', 'total_cost': 300.0, 'transaction_amount': 150.0}, \
                                    {'transaction_id': 2, 'transaction_type': 'RESERVATION', 'transaction_date': '4-30-2022', 'reservation_id': 2, 'customer_id': 'hayder2', 'resource': 'hvc', 'total_cost': 10000.0, 'transaction_amount': 5000.0}, \
                                        {'transaction_id': 3, 'transaction_type': 'CANCELLATION', 'transaction_date': '4-30-2022', 'reservation_id': 1, 'customer_id': 'hayder', 'resource': 'extruder', 'total_cost': 300.0, 'transaction_amount': '0'}]}}
    
    def test_get_transactions_invalid_start_date(self):
        #Invalid GET transactions request due to invalid start date.
        response = client.get("/v1_0/transactions?start_date=19-19-2022")
        assert response.status_code == 400
        assert response.json() == {'detail': 'Get Transactions failed: date format incorrect'}

    def test_get_transactions_invalid_end_date(self):
        #Invalid GET transactions request due to invalid start date.
        response = client.get("/v1_0/transactions?end_date=19-19-2022")
        assert response.status_code == 400
        assert response.json() == {'detail': 'Get Transactions failed: date format incorrect'}


class TestPostReservationsPasses:
    '''
    Test for passing/valid POST /reservations/ requests
    '''
    #First set a start date that is dynamic and should never cause a failure.
    if (datetime.datetime.now()+timedelta(days=3)).weekday()==6:
        start_date=datetime.datetime.now()+timedelta(days=2)
    else:
        start_date=datetime.datetime.now()+timedelta(days=3)
    dt_date=str(start_date.strftime("%m-%d-%Y"))

    def test_post_single_reservations(self):
        #Valid POST reservations request for a single reservation.
        response = client.post("/v1_0/reservations",json = {"customer_id":"hayder","resource":"workshop","start_date":self.dt_date,"start_time":"11:00"})
        assert response.status_code == 201
        assert response.json() == {'detail': {'discount': '0', 'down_payment': '0', 'reservation_id': '3', 'total_cost': '49.5'},'status_code': 201}
    
    def test_post_recurring_reservations(self):
        #Valid POST reservations request for a recurring reservation.
        #Set a end date that is dynamic and should never cause a failure.
        if (datetime.datetime.now()+timedelta(days=3)).weekday()==6:
            end_date=datetime.datetime.now()+timedelta(days=4)
        else:
            end_date=datetime.datetime.now()+timedelta(days=5)
        e_date=str(end_date.strftime("%m-%d-%Y"))
        response = client.post("/v1_0/reservations",json = {"customer_id":"hayder2","resource":"hvc","start_date":self.dt_date,"end_date":e_date,"start_time":"11:00","start_time":"11:30"})
        assert response.status_code == 201
        assert response.json() == {'detail': {'discount': '0', 'down_payment': '15000.0', 'reservation_id': '4', 'total_cost': '30000'},'status_code': 201}


class TestPostReservationsFails:
    '''
    Test for failing/invalid POST /reservations/ requests
    Covers every failing case.
    '''
    #First set a start date that is dynamic and should never cause a failure. This start date will not be used by all failure cases.
    if (datetime.datetime.now()+timedelta(days=3)).weekday()==6:
        start_date=datetime.datetime.now()+timedelta(days=2)
    else:
        start_date=datetime.datetime.now()+timedelta(days=3)
    dt_date=str(start_date.strftime("%m-%d-%Y"))

    def test_post_empty_customer_id_single_reservations(self):
        #Valid POST reservations request for a single reservation.
        response = client.post("/v1_0/reservations",json = {"customer_id":"","resource":"workshop","start_date":self.dt_date,"start_time":"11:00"})
        assert response.status_code == 400
        assert response.json() == {'detail': "Reservation failed: Empty customer_id"}

    def test_post_geq3_per_client_reservations(self):
        #Invalid POST reservations request due to >3 reservations/week by a particular client.
        #Set a end date that is dynamic and should never cause a failure.
        if (datetime.datetime.now()+timedelta(days=3)).weekday()==6:
            end_date=datetime.datetime.now()+timedelta(days=5)
        else:
            end_date=datetime.datetime.now()+timedelta(days=6)
        e_date=str(end_date.strftime("%m-%d-%Y"))
        response = client.post("/v1_0/reservations",json = {"customer_id":"hayder3","resource":"microvac","start_date":self.dt_date,"end_date":e_date,"start_time":"11:00","start_time":"11:30"})
        assert response.status_code == 400
        assert response.json() == {'detail': 'Reservation failed: A client can only make reservations for 3 different days in a given week'}

    def test_post_single_reservations_incorrect_resource(self):
        #Invalid POST reservations request due to invalid resource.
        response = client.post("/v1_0/reservations",json = {"customer_id":"hayder","resource":"fakemachine","start_date":self.dt_date,"start_time":"11:00"})
        assert response.status_code == 400
        assert response.json() == {'detail': 'Reservation failed: Unsupported resource: fakemachine'} 

    def test_post_single_reservations_fail_date_in_past(self):
        #Invalid POST reservations request due to setting reservation start date to a date already passed.
        #Set start date to a date in the past.
        start_date=datetime.datetime.now()+timedelta(days=-2)
        dt_date=str(start_date.strftime("%m-%d-%Y"))
        response = client.post("/v1_0/reservations",json = {"customer_id":"hayder","resource":"workshop","start_date":dt_date,"start_time":"11:00"})
        assert response.status_code == 400
        assert response.json() == {'detail': 'Reservation failed: Cannot reserve time already passed.'} 

    def test_post_single_reservations_fail_geq_30days(self):
        #Invalid POST reservations request due to setting reservation start date to >30 days in the future.
        #Set start date to a date >30 days in the future.
        start_date=datetime.datetime.now()+timedelta(days=32)
        dt_date=str(start_date.strftime("%m-%d-%Y"))
        response = client.post("/v1_0/reservations",json = {"customer_id":"hayder","resource":"workshop","start_date":dt_date,"start_time":"11:00"})
        assert response.status_code == 400
        assert response.json() == {'detail': 'Reservation failed: Cannot reserve time more than 30 days away.'}

    def test_post_single_reservations_fail_not_30min_block(self):
        #Invalid POST reservations request due to setting reservation time not being a multiple of 30 minutes.
        response = client.post("/v1_0/reservations",json = {"customer_id":"hayder","resource":"workshop","start_date":self.dt_date,"start_time":"11:11"})
        assert response.status_code == 400
        assert response.json() == {'detail': 'Reservation failed: Reservations for all resources are made in 30 minute blocks and always start on the hour or half hour'}

    def test_post_single_reservations_fail_geq_1_special_machine(self):
        #Invalid POST reservations request due to a particular client trying to reserve >1 special machine at a time.
        #Set start date to clash with one of the entries in data.txt
        if (datetime.datetime.now()+timedelta(days=3)).weekday()==6:
            start_date=datetime.datetime.now()+timedelta(days=4)
        else:
            start_date=datetime.datetime.now()+timedelta(days=5)
        dt_date=str(start_date.strftime("%m-%d-%Y"))
        response = client.post("/v1_0/reservations",json = {"customer_id":"hayder2","resource":"irradiator","start_date":dt_date,"start_time":"11:30"})
        assert response.status_code == 400
        assert response.json() == {'detail': 'Reservation failed: A client can only reserve one special machine at a time'}

    def test_post_single_reservations_fail_machines_not_available(self):
        #Invalid POST reservations request due to a particular machine being out of stock.
        response = client.post("/v1_0/reservations",json = {"customer_id":"hayder3","resource":"hvc","start_date":self.dt_date,"start_time":"11:30"})
        assert response.status_code == 400
        assert response.json() == {'detail': 'Reservation failed: Not enough available hvc, 1 already reserved'}

    def test_post_single_reservations_fail_geq_1_irradiator(self):
        #Invalid POST reservations request due to an attempt to use multiple irradiators.
        client.post("/v1_0/reservations",json = {"customer_id":"hayder3","resource":"irradiator","start_date":self.dt_date,"start_time":"11:30"})
        response = client.post("/v1_0/reservations",json = {"customer_id":"hayder4","resource":"irradiator","start_date":"05-03-2022","start_time":"11:30"})
        assert response.status_code == 400
        assert response.json() == {'detail': 'Reservation failed: Only 1 irradiator can be used at a time'}

    def test_post_single_reservations_fail_hvc_cooldown(self):
        #Invalid POST reservations request due to an attempt to schedule a high velocity crusher during it's cooldown period.
        response = client.post("/v1_0/reservations",json = {"customer_id":"hayder3","resource":"hvc","start_date":self.dt_date,"start_time":"14:30"})
        assert response.status_code == 400
        assert response.json() == {'detail': 'Reservation failed: High velocity crusher needs to cool down for 6 hours between uses, hvc currently reserved for 11:30-12:00.'}

    def test_post_single_reservations_fail_irradiator_cooldown(self):
        #Invalid POST reservations request due to an attempt to schedule an irradiator during it's cooldown period.
        client.post("/v1_0/reservations",json = {"customer_id":"hayder4","resource":"irradiator","start_date":self.dt_date,"start_time":"12:00"})
        response = client.post("/v1_0/reservations",json = {"customer_id":"hayder4","resource":"irradiator","start_date":"05-03-2022","start_time":"12:30"})
        assert response.status_code == 400
        assert response.json() == {'detail': 'Reservation failed: Irradiators need to cool down for 1 hour between uses'} 

    def test_post_single_reservations_fail_geq_3machines_with_harvester(self):
        #Invalid POST reservations request due to an attempt to schedule 3 machines alongside the harvester.
        client.post("/v1_0/reservations",json = {"customer_id":"hayder4","resource":"harvester","start_date":self.dt_date,"start_time":"11:30"})
        client.post("/v1_0/reservations",json = {"customer_id":"hayder5","resource":"extruder","start_date":self.dt_date,"start_time":"11:30"})
        response = client.post("/v1_0/reservations",json = {"customer_id":"hayder6","resource":"microvac","start_date":self.dt_date,"start_time":"11:30"})
        assert response.status_code == 400
        assert response.json() == {'detail': 'Reservation failed: Only 3 other machines can run while the 1.21 gigawatt lightning harvester is operating'} 

    def test_post_single_reservations_fail_workshop_is_closed(self):
        #Invalid POST reservations request due to an attempt to book anything on a sunday.
        #Set start date to nearest sunday.
        if (datetime.datetime.now()).weekday()!=6:
            start_date=datetime.datetime.now()+timedelta(days=(6-datetime.datetime.now().weekday()))
        else:
            start_date=datetime.datetime.now()
        dt_date=str(start_date.strftime("%m-%d-%Y"))
        dt_date2=str(start_date.strftime("%Y-%m-%d"))
        response = client.post("/v1_0/reservations",json = {"customer_id":"hayder6","resource":"microvac","start_date":dt_date,"start_time":"11:30"})
        assert response.status_code == 400
        assert response.json() == {'detail': f'Reservation failed: Cannot reserve time interval from 11:30 to 12:00 on {dt_date2}'} 


class TestDeleteReservations:
    '''
    Test for both valid and invalid DELETE /reservations/ requests
    '''
    def test_delete_reservations(self):
        #Valid DELETE reservations request using a valid reservation id.
        response = client.delete("/v1_0/reservations",json = {"reservation_id":3})
        assert response.status_code == 200
        assert response.json() == {'detail': {'percent_returned': '50', 'refund': '0.0'},'status_code': 200}

    def test_delete_reservations_invalid_id(self):
        #Invalid DELETE reservations request due to reservation id being invalid.
        response = client.delete("/v1_0/reservations",json = {"reservation_id":100})
        assert response.status_code == 400
        assert response.json() == {'detail': 'Cancellation failed: Invalid reservation id: 100'}


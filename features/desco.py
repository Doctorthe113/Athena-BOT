import requests

balance_url = "http://prepaid.desco.org.bd/api/tkdes/customer/getBalance?accountNo=" # 1234567
monthly_consume = "http://prepaid.desco.org.bd/api/tkdes/customer/getCustomerMonthlyConsumption?accountNo=" # 1234567&meterNo=&monthFrom=2021-08&monthTo=2022-07
daily_consume = "http://prepaid.desco.org.bd/api/tkdes/customer/getCustomerDailyConsumption?accountNo=" # 1234567&meterNo=&dateFrom=2023-07-31&dateTo=2023-08-29
recharge_history = "http://prepaid.desco.org.bd/api/tkdes/customer/getRechargeHistory?accountNo=" # 1234567&meterNo=&dateFrom=2022-08-01&dateTo=2023-07-31

def check_balance(account):
    url = balance_url + str(account)
    response = requests.get(url).json()

    balance = response["data"]["balance"]
    current_month_consume = response["data"]["currentMonthConsumption"]
    return balance, current_month_consume

def monthly_consumption(account, month):
    monthFrom = f"&monthFrom={month}&monthTo={month}"
    url = monthly_consume + str(account) + monthFrom
    response = requests.get(url).json()

    consumed_taka = response["data"][0]["consumedTaka"]
    consumed_unit = response["data"][0]["consumedUnit"]
    return consumed_taka, consumed_unit

def daily_consumption(account, date):
    days = str.split(date, "-")
    day = days[:2] # this keeps only the year and the month
    day.append(str(int(days[2]) - 1))
    modified_date = "-".join(day) # all this to get the previous day

    dateFrom = f"&dateFrom={modified_date}&dateTo={date}"
    url = daily_consume + str(account) + dateFrom
    response = requests.get(url).json()

    previous_day_consumed_taka = response["data"][0]["consumedTaka"]
    consumed_taka_upto_today = response["data"][1]["consumedTaka"]
    previous_day_consumed_unit = response["data"][0]["consumedUnit"]
    consumed_unit_upto_today = response["data"][1]["consumedUnit"]

    consumed_taka = int(consumed_taka_upto_today) - int(previous_day_consumed_taka)
    consumed_unit = int(consumed_unit_upto_today) - int(previous_day_consumed_unit)

    return consumed_taka_upto_today, consumed_unit_upto_today, consumed_taka, consumed_unit

def last_recharge(account, date):
    days = str.split(date, "-")
    day = days[1] # this gets the month and saves it in "day" variable for later use
    del days[1]
    days.insert(1, format(int(day) - 1, "02d"))
    modified_date = "-".join(days) # all this to get the previous month

    dateFrom = f"&dateFrom={modified_date}&dateTo={date}"
    url = recharge_history + str(account) + dateFrom
    response = requests.get(url).json()

    recharge_date = response["data"][0]["rechargeDate"]
    recharge_amount = response["data"][0]["totalAmount"]
    order_id = response["data"][0]["orderID"]

    return recharge_date, recharge_amount, order_id
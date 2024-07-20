# Made by The Doctor
# https://pypi.org/project/descoApi/1.0/
from requests import get

class DescoAPI():
    def __init__(self, accountNumber: int) -> None:
        self.balanceURL = "http://prepaid.desco.org.bd/api/tkdes/customer/getBalance?"
        self.monthlyConsume = "http://prepaid.desco.org.bd/api/tkdes/customer/getCustomerMonthlyConsumption?"
        self.dailyConsume = "http://prepaid.desco.org.bd/api/tkdes/customer/getCustomerDailyConsumption?"
        self.recharge = "http://prepaid.desco.org.bd/api/tkdes/customer/getRechargeHistory?"
        self.account = accountNumber
        self.meterNo = get(self.balanceURL, params={"accountNo": self.account}).json()["data"]["meterNo"]

    def balanceCheck(self):
        response = get(self.balanceURL, params={"accountNo": self.account, "meterNo": self.meterNo}).json()
        balance = response["data"]
        return balance

    def monthlyCheck(self, monthFrom, monthTo):
        response = get(self.monthlyConsume, params={"accountNo": self.account, "meterNo": self.meterNo, "monthFrom": monthFrom, "monthTo": monthTo}).json()
        balance = response["data"]
        return balance

    def datecheck(self, dateFrom, dateTo):
        response = get(self.dailyConsume, params={"accountNo": self.account, "meterNo": self.meterNo, "dateFrom": dateFrom, "dateTo": dateTo}).json()
        balance = response["data"]
        return balance

    def rechargeHistory(self, dateFrom, dateTo):
        response = get(self.recharge, params={"accountNo": self.account, "meterNo": self.meterNo, "dateFrom": dateFrom, "dateTo": dateTo}).json()
        balance = response["data"]
        return balance

    def help(self):
        print(f"\033[35m 1. \033[37m \033[36m \'balanceCheck\' \033[0m Returns a json containing balance and monthly consumption upto today.")
        print(f"\033[35m 2. \033[37m \033[36m \'monthlyCheck\' \033[0m Returns a json for all info from \'monthFrom\' to \'monthTo\'. Max range 12 months.")
        print(f"\033[35m 3. \033[37m \033[36m \'dateCheck\' \033[0m Returns a json for all info from \'dateFrom\' to \'dateTo\'. Max range 30 days.")
        print(f"\033[35m 3. \033[37m \033[36m \'rechargeHistory\' \033[0m Returns a json for all info from \'dateFrom\' to \'dateTo\'. Max range 30 days. Only show the running month\'s info.")
        return f"\033[31m \033[4m For any issues or questions contact via GitHub. \033[0m"
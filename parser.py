import re
import datetime

months = [ "jan"
	 , "feb"
	 , "mar"
	 , "apr"
	 , "may"
	 , "jun"
	 , "jul"
	 , "aug"
	 , "sep"
	 , "oct"
	 , "nov"
	 , "dec"
	 ]

def parse(string):
	month = next((item for item in list(map(lambda x: x if x in string else None, months)) if item is not None), months[datetime.datetime.now().month - 1])
	numbers = re.findall(r"(\d+|\:)", string)
	hours = numbers[numbers.index(":") - 1]
	minutes = numbers[numbers.index(":") + 1]
	day = None
	year = datetime.datetime.now().year
	for i in range(0, len(numbers) - 1):
		if(abs(numbers.index(":")) - i > 1 and int(numbers[i]) <= 31):
			day = numbers[i]
	for n in filter(str.isdigit, numbers):
		if(int(n) > 999):
			year = int(n)
	return datetime.datetime(year, months.index(month) + 1, int(day), int(hours), int(minutes), 0)

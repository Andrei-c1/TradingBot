import datetime     # for general datetime object handling
import rfc3339      # for date object -> date string
import iso8601      # for date string -> date object

class Helper:


    @staticmethod
    def get_date_object(date_string):
        return iso8601.parse_date(date_string)
    @staticmethod
    def get_date_string(date_object):
        return rfc3339.rfc3339(date_object)
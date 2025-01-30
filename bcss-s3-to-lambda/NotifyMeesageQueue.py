from enum import Enum


class NotifyMeesageQueue(Enum):
    NHS_NUMBER = 0
    MESSAGE_ID = 1
    BATCH_ID = 2
    ROUTING_PLAN_ID = 3
    MESSAGE_STATUS = 4
    VARIABLE_TEXT_1 = 5
    ADDRESS_LINE_1 = 6
    ADDRESS_LINE_2 = 7
    ADDRESS_LINE_3 = 8
    ADDRESS_LINE_4 = 9
    ADDRESS_LINE_5 = 10
    POSTCODE = 11
    GP_PRACTICE_NAME = 12

    def __str__(self):
        return self.name

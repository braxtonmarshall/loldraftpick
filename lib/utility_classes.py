from enum import Enum


class Patch(Enum):
    TENTWENTY = "2020-09-30 00:00:00", 10.20
    TENNINETEEN = "2020-09-19 00:00:00", 10.19
    TENEIGHTTEEN = "2020-09-02 00:00:00", 10.18
    TENSEVENTEEN = "2020-08-19 00:00:00", 10.17
    TENSIXTEEN = "2020-08-05 00:00:00", 10.16
    TENFIFTEEN = "2020-07-22 00:00:00", 10.15
    TENFOURTEEN = "2020-07-08 00:00:00", 10.14
    TENTHIRTEEN = "2020-06-24 00:00:00", 10.13
    TENTWELVE = "2020-06-10 00:00:00", 10.12
    TENELEVEN = "2020-05-28 00:00:00", 10.11
    TENTEN = "2020-05-13 00:00:00", 10.10
    TENNINE = "2020-04-29 00:00:00", 10.09
    TENEIGHT = "2020-04-15 00:00:00", 10.08
    TENSEVEN = "2020-04-01 00:00:00", 10.07
    TENSIX = "2020-03-18 00:00:00", 10.06
    TENFIVE = "2020-03-04 00:00:00", 10.05
    TENFOUR = "2020-02-20 00:00:00", 10.04
    TENTHREE = "2020-02-05 00:00:00", 10.03
    TENTWO = "2020-01-23 00:00:00", 10.02
    TENONE = "2020-01-08 00:00:00", 10.01

    def __new__(cls, datetime, *value_aliases):
        obj = object.__new__(cls)
        obj._value_ = datetime
        for alias in value_aliases:
            cls._value2member_map_[alias] = obj
        return obj


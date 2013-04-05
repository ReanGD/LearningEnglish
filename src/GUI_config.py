# -*- coding: utf-8 -*-

from Tkinter import PhotoImage

clr_stat_frame = "#E9F6FE"
clr_word_frame = "#FFFFE0"
clr_answer_frame = "#E9F6FE"
clr_success = "#348000"
clr_error = "#FC0039"
clr_black = "#000000"
clr_stat = ["#7B7B00", "#007B00", "#7B7B7B"]


def edit_image():
    img = PhotoImage(format="gif",
                     data="R0lGODlhEAAQAMQAAAAAAP//////3f/lbv/MAN2qAMSRAKp3AP/lzP+/mcxmM+WATf+ZZswzM5kz"
                     + "M/9mZt1mZt3d3czMzLu7u6qqqpmZmYiIiGZmZjMzM////wAAAAAAAAAAAAAAAAAAAAAAACH5BAEA"
                     + "ABkALAAAAAAQABAAAAVJYCaOpFg9T6lmVURBzToWAiVZsUwPhDVdOgGvUACudgTiITgsLI/CpJMp"
                     + "faqQSmoW2rSWGAhDVZZZIBKHKRmTYDC8KwzGoSCPQgA7")
    return img


def find_in_web_image():
    img = PhotoImage(format="gif",
                     data="R0lGODlhEAAQAPeoAP39/YX8iLa2tuXm5jF7m/z8/Pv7+37hparArEh/l83NzcDBwU6Yuu3t7YrB"
                     + "kUiUtsHL0FCavD6KrKLE1GaLm0SQsyx7nVKbvVqiw0aStC5/oyp8oDx9mW6klWOuwpe5o4L1jYDr"
                     + "mUGOsZC8z33dqlymzHi72IP3jIi3yFWewObo54T2kWm/s4LD4Wuy1p/D08bLzHW32MTIynSXp5fO"
                     + "w4LniILvjpi+nJC3nMDAwLrJwG2yq16KnrTntqm1u87bz7e+wdjZ2oP4ipb2mVukwI6vrD6OtVyk"
                     + "xbG5vILykWy+ukSemajE0KDPvO/v7+nz+KTO0zmHqm/Bu4XUiJ7FqXbXp0CNsOrr6+rr6tzc3Fig"
                     + "wjyKrUmVt1mhw9rc2miNnFmypV25o8HjwTOCpUCOrlKEmefo6Jazo3q73KGus2OryJ6+zHjdoIT0"
                     + "iWyfrMbNyILlp67BvLvFvKKxsbzHy5TrnDyDosLGxT+Qt4LrnnvSubS6tDCApH3vjoflnZPAlqLI"
                     + "wDCBpNvd24T1kEmUtz+Mr/n5+TSEp2Wux5S7my1+op/OymC2rnrYrIKqspfA046zw9zc3UuVt4Dt"
                     + "ldDi0TiHqlWGm4Gbpof6ip/VvzV8m4ysu3TPsOzt7ZSosTmHq1CcuNjo8V6hwIfA34iep3XHv6TD"
                     + "0yl7n////wAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
                     + "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
                     + "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
                     + "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
                     + "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACH5BAEAAKgALAAAAAAQABAA"
                     + "AAjxAFEJRAVAEIIbHxB4ATCw4RUcbfSYiFHKxh8sDVGZccPmAJoWcEJIYTFFxUADM7QgSpJnxSAS"
                     + "VY4wcmBAoAxJKTxwChDgQCMlXRiAeSPwUoYIGNSACHBikh9RXMgkIsjDCqELRIQEGEIpSyQmEjoA"
                     + "KGApiogHoPpg+iEGygsIkMoUQPUlUKVCFcLUgbFoxKM1dCgITHNKw6FPW3bcyYSCBiAdcwR24nBq"
                     + "gyI+Y3zEadJDDpUGA4FYOEX6lB1PAvY4KhGqIRJNpUkvqVHEiIsnDQeQSkCAQIIzA1BNwDMqo4Ic"
                     + "AgQsUCAwyCZTGaMPdGIoIAA7")
    return img


def stat_image():
    img = PhotoImage(format="gif",
                     data="R0lGODlhEAAQAOYAAAAAAP///5dxdJNtdI9qdItncl6Atnef33uk5Fx+s3uk44Cp6Iav7Yav64Wt"
                     + "6Yew64uz7oq18Yy384659JC79Y638ZC785S+9ZO99JbA9qjP+qvS+maRMGCILV6FLJLAQZG+QpK/"
                     + "SJbEPpXDP5PBQJDEII3BH4q+H5PHIYy/I47CJJLEJZjLKJfHMpjIN6HPPJzKO57MPKTSP6LQPqDP"
                     + "Pp/NPZrIPKXUQZjGPafTTLzlYsjteJfKI5rOJZXHJp7QKJvOKp/QLKPVLqTVMqnZN6nZO6bUPqPR"
                     + "Pa7dQajWQq7cRKnWQ6zYRa3ZSLPgTLPfTrDcTrnjVbTfVLnjV7jhW8fsdMfsdaKOGqSGG6CBHJx8"
                     + "Hph3IJRzIZFvIotsJuaRUuaSUvCMSPGUVPSgZ/Slbt1XBOBdCuBmGuVqG+NrH+d3Lut7Me2FQZcx"
                     + "DZQxDaaAdqWIgqF8dZx2df///wAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACH5"
                     + "BAEAAHMALAAAAAAQABAAAAe4gHOCg4SFhoU7VVVWTIeEOlFRU0aOg1ROTk9HlYJSSEhKL4MbGhuF"
                     + "UERERTGDGRQZhU1CQkMwgxcTF4VLPz9BNoMYEhhwYF9gV0k9PUA4gxYRFm9kY2RYNzw8LCKDFQwV"
                     + "cWJhYlkyKCg+I4MQCxBybGtsWjMlJSskgw8KDwJqaGpbaJgwoeLDIAcHHAxIYyYNlxonTqQAMagB"
                     + "ggYEzpQ50yVHixYuQgwykMBAgTZu2njp4KElhzmBAAA7")
    return img

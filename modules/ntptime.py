import time
from time import gmtime
import socket
import struct
import machine

from .config import REPORTING_TIMES

class piClock:
    """
    Pico internal clock using ntp time server and the pico's realtime clock

    """


    # The NTP host can be configured at runtime by doing: instance.host = 'myhost.org'
    host = "time.google.com"
    # The NTP socket timeout can be configured at runtime by doing: instance.timeout = 2
    timeout = 1

    def __init__(self):
        self.setRtcFromNtpTime()


    def queryNTPTime(self):
        NTP_QUERY = bytearray(48)
        NTP_QUERY[0] = 0x23
        addr = socket.getaddrinfo(self.host, 123)[0][-1]
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.settimeout(self.timeout)
            s.sendto(NTP_QUERY, addr)
            msg = s.recv(48)
        finally:
            s.close()
        val = struct.unpack("!I", msg[40:44])[0]

        # 2024-01-01 00:00:00 converted to an NTP timestamp
        MIN_NTP_TIMESTAMP = 3913056000

        # Y2036 fix
        #
        # The NTP timestamp has a 32-bit count of seconds, which will wrap back
        # to zero on 7 Feb 2036 at 06:28:16.
        #
        # We know that this software was written during 2024 (or later).
        # So we know that timestamps less than MIN_NTP_TIMESTAMP are impossible.
        # So if the timestamp is less than MIN_NTP_TIMESTAMP, that probably means
        # that the NTP time wrapped at 2^32 seconds.  (Or someone set the wrong
        # time on their NTP server, but we can't really do anything about that).
        #
        # So in that case, we need to add in those extra 2^32 seconds, to get the
        # correct timestamp.
        #
        # This means that this code will work until the year 2160.  More precisely,
        # this code will not work after 7th Feb 2160 at 06:28:15.
        #
        if val < MIN_NTP_TIMESTAMP:
            val += 0x100000000

        # Convert timestamp from NTP format to our internal format

        EPOCH_YEAR = gmtime(0)[0]
        if EPOCH_YEAR == 2000:
            # (date(2000, 1, 1) - date(1900, 1, 1)).days * 24*60*60
            NTP_DELTA = 3155673600
        elif EPOCH_YEAR == 1970:
            # (date(1970, 1, 1) - date(1900, 1, 1)).days * 24*60*60
            NTP_DELTA = 2208988800
        else:
            raise Exception("Unsupported epoch: {}".format(EPOCH_YEAR))

        return val - NTP_DELTA



    def setRtcFromNtpTime(self):
        # There's currently no timezone support in MicroPython, and the RTC is set in UTC time.  Offset by #of hours in timezone difference.
        t = self.queryNTPTime()

        tm = self.utc_to_eastern(t)

        #(year, month, day, weekday, hours, minutes, seconds, subseconds)
        machine.RTC().datetime((tm[0], tm[1], tm[2], tm[6] + 1, tm[3], tm[4], tm[5], 0))


    def getRtcTime(self):
        # (year, month, day, hour, minute, second)
        dt = machine.RTC().datetime()
        # RTC datetime() = (year, month, day, weekday, hours, minutes, seconds, subseconds)
        result = (dt[0], dt[1], dt[2], dt[4], dt[5], dt[6])
        return result

    @property
    def date(self):
        dt = self.getRtcTime()
        return "{:04d}-{:02d}-{:02d}".format(dt[0], dt[1], dt[2])

    @property
    def time(self):
        dt = self.getRtcTime()
        return "{:02d}:{:02d}:{:02d}".format(dt[3], dt[4], dt[5])

    # ----------------------- REPORTING TIME ----------------------- #

    def isTimeToReport(self) -> bool:
        """
        Checks if it's time to report the data.

        Returns:
            A boolean result of true if the time matches and false otherwise.
        """
        dtTuple = self.getRtcTime()
        t_h = dtTuple[3]
        t_m = dtTuple[4]

        for reporttime in REPORTING_TIMES:
            rt_h, rt_m, _, = map(int, reporttime.split(":"))
            if t_h == rt_h and t_m == rt_m:
                return True

        return False




    #functions below are helpers to convert UTC to eastern time, taking daylight savings into account.
    # https://www.geeksforgeeks.org/dsa/tomohiko-sakamotos-algorithm-finding-day-week/
    def _sakamoto_dow(self, year, month, day):
        """Day of week for Y/M/D. Returns 0=Sunday .. 6=Saturday."""
        t = [0, 3, 2, 5, 0, 3, 5, 1, 4, 6, 2, 4]
        y = year
        if month < 3:
            y -= 1
        return (y + y // 4 - y // 100 + y // 400 + t[month - 1] + day) % 7

    def _nth_sunday(self, year, month, n):
        """Day-of-month of the nth Sunday in a given month/year."""
        dow0 = self._sakamoto_dow(year, month, 1)          # weekday of the 1st
        first_sunday = 1 if dow0 == 0 else 1 + (7 - dow0)
        return first_sunday + (n - 1) * 7

    def _is_dst(self, year, mon, mday, hour, minute):
        """
        US DST rule: 2nd Sunday in March 2:00 AM local -> 3:00 AM local (spring forward)
        1st Sunday in November 2:00 AM local -> 1:00 AM local (fall back)
        Expressed here in UTC-equivalent cutover times:
        spring cutover = 07:00 UTC (2:00 AM EST) on 2nd Sunday of March
        fall cutover   = 06:00 UTC (2:00 AM EDT) on 1st Sunday of November
        """
        march_day = self._nth_sunday(year, 3, 2)
        nov_day = self._nth_sunday(year, 11, 1)

        spring = (year, 3, march_day, 7, 0)
        fall = (year, 11, nov_day, 6, 0)
        now = (year, mon, mday, hour, minute)

        return spring <= now < fall

    def utc_to_eastern(self, t):
        """
        Convert a gmtime()-style timestamp (UTC) to US Eastern local time
        (EST/EDT as appropriate), returning a tuple in the same 8-field
        gmtime format: (year, mon, mday, hour, min, sec, wday, yday).
        """
        tm = gmtime(t)
        year, mon, mday, hour, minute, sec, wday = tm[0], tm[1], tm[2], tm[3], tm[4], tm[5], tm[6]

        offset_hours = -4 if self._is_dst(year, mon, mday, hour, minute) else -5

        # Use mktime/gmtime purely as an arithmetic tool - the epoch reference
        # (1970 vs 2000) cancels out since we go in and back out the same way.
        epoch = time.mktime((year, mon, mday, hour, minute, sec, wday, 0))
        epoch += offset_hours * 3600
        return time.gmtime(epoch)

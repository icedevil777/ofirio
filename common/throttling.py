from rest_framework.throttling import AnonRateThrottle as DrfAnonRateThrottle


class AnonRateThrottle(DrfAnonRateThrottle):
    """
    Add support of week and month to the stock class
    """
    durations = {
        'second': 1,
        'minute': 60,
        'hour': 60 * 60,
        'day': 24 * 60 * 60,
        'week': 7 * 24 * 60 * 60,
        'month': 30 * 7 * 24 * 60 * 60,
    }

    def parse_rate(self, rate):
        """
        Given the request rate string, return a two tuple of:
        <allowed number of requests>, <period of time in seconds>
        """
        if rate is None:
            return (None, None)
        num, period = rate.split('/')
        num_requests = int(num)
        duration = self.durations[period]
        return num_requests, duration

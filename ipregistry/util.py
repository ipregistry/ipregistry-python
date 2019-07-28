class UserAgent:

    @staticmethod
    def isBot(header):
        header = header.lower()
        return "bot" in header or "spider" in header

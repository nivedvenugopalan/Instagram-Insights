from app.helpers import ParsedInstagramData
from datetime import datetime


class DataAnalyzer:
    def __init__(self, data: ParsedInstagramData) -> None:
        self.data = data

        self.ads_topics_and_viewership = self._ads_topics_and_viewership(
            data.ads_and_topics, data.your_topics, data.information_about_you)

    class _ads_topics_and_viewership:
        def __init__(self, ads_and_topics, your_topics, information_about_you) -> None:
            self.ads_and_topics = ads_and_topics
            self.your_topics = your_topics
            self.information_about_you = information_about_you

        def ad_view_freq(self) -> int or float:
            """Frequency of ads seen per day."""

            # times the user has seen an ad
            datetimes = []
            for block in self.ads_and_topics.ads_viewed['impressions_history_ads_seen']:
                # time in format date month year, 24h:min
                time_string = block['string_map_data']['Time']['value']
                datetimes.append(datetime.strptime(
                    time_string, r"%d %b %Y, %H:%M"))
            print(datetimes)

            # Group the datetime objects by day
            days = {}
            for dt in datetimes:
                day = dt.date()
                if day not in days:
                    days[day] = []
                days[day].append(dt)
            print(days)

            # Calculate the total number of ads seen
            total_ads = sum([len(times) for times in days.values()])

            average_frequency = total_ads/len(days)

            return round(average_frequency, 1)

        def ad_interest(self) -> list[str]:
            """Returns a list of categories (`n`), which the 'interests' which the instagram algorithm has sought for you, belong to

            Args:
                `n` Number of categories"""

            interests = [block['string_map_data']['Interest']['value']
                         for block in self.information_about_you.ads_interest['inferred_data_ig_interest']]

            # work on this using:
            # (1) network analysis
            # (2) train ml-model on topics (text classification)

            # return

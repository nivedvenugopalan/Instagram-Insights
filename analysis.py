from app.helpers import ParsedInstagramData
from datetime import datetime
from collections import Counter


class DataAnalyzer:
    def __init__(self, data: ParsedInstagramData) -> None:
        self.data = data

        self.ads_topics_and_viewership = self._ads_topics_and_viewership(
            data.ads_and_topics, data.your_topics, data.information_about_you, data.messages)

        self.comments = self._comments(data.comments) 

    class _ads_topics_and_viewership:
        def __init__(self, ads_and_topics, your_topics, information_about_you, messages) -> None:
            self.ads_and_topics = ads_and_topics
            self.your_topics = your_topics
            self.information_about_you = information_about_you
            self.messages = messages

        def ad_view_freq(self) -> int or float:
            """Returns the frequency of ads seen per day."""

            # times the user has seen an ad
            datetimes = []
            for block in self.ads_and_topics.ads_viewed['impressions_history_ads_seen']:
                # time in format date month year, 24h:min
                time_string = block['string_map_data']['Time']['value']
                datetimes.append(datetime.strptime(
                    time_string, r"%d %b %Y, %H:%M"))

            # Group the datetime objects by day
            days = {}
            for dt in datetimes:
                day = dt.date()
                if day not in days:
                    days[day] = []
                days[day].append(dt)

            # Calculate the total number of ads seen
            total_ads = sum([len(times) for times in days.values()])

            average_frequency = total_ads/len(days)

            return round(average_frequency, 1)

        def latest_ad_interest(self, n: int) -> list[str]:
            """Returns a list of latest (`n`) 'ad_interests' which the instagram algorithm has sought for you.

            Args:
                `n` int or None
                
            If `n` is None, it returns the entire list."""

            interests = [block['string_map_data']['Interest']['value']
                         for block in self.information_about_you.ads_interest['inferred_data_ig_interest']]

            return interests[-n:] if n is not None else interests

        def latest_topics(self, n:int or None) -> list[str]:
            """Returns a list of latest (`n`) 'topics' which the instagram algorithm has added to your list of sought for you.
            
            Args:
                `n` int or None
                
            If `n` is None, it returns the entire list."""

            topics = [block['string_map_data']['Name']['value'] for block in self.your_topics.your_topics['topics_your_topics']]

            return topics[-n:] if n is not None else topics

        def most_active_hours(self) -> int:
            """Returns an int, which specifies the start interval of a one hour period, where the user has been active the most."""
            # weights
            WEIGHTS = {
                'posts': 3,
                'reels': 2.5,
                'ads': 0.5,
                'messages': 0.05
            }

            # get list of times for posts and reels viewed
            ad_view_times = [block['string_map_data']['Time']['value']
                             for block in self.ads_and_topics.ads_viewed['impressions_history_ads_seen']]

            post_view_times = [block['string_map_data']['Time']['value']
                               for block in self.ads_and_topics.posts_viewed['impressions_history_posts_seen']]

            reel_view_times = [block['string_map_data']['Time']['value']
                               for block in self.ads_and_topics.videos_watched['impressions_history_videos_watched']]

            # convert into datetime objects
            ad_view_times = [datetime.strptime(
                x, r"%d %b %Y, %H:%M") for x in ad_view_times]

            post_view_times = [datetime.strptime(
                x, r"%d %b %Y, %H:%M") for x in post_view_times]

            reel_view_times = [datetime.strptime(
                x, r"%d %b %Y, %H:%M") for x in reel_view_times]

            # message view times
            message_view_times = []
            for chat in self.messages.inbox:
                messages = chat.messages['messages']
                times = [datetime.fromtimestamp(int(message['timestamp_ms'])/1000) for message in messages]
                message_view_times.extend(times)

            hour_count = {}
            interval_size = 1

            # ad times
            for time in ad_view_times:
                interval = time.hour // interval_size * interval_size
                if interval not in hour_count.keys():
                    hour_count[interval] = 0
                hour_count[interval] += WEIGHTS['ads']

            # post time
            for time in post_view_times:
                interval = time.hour // interval_size * interval_size
                if interval not in hour_count.keys():
                    hour_count[interval] = 0
                hour_count[interval] += WEIGHTS['posts']

            # reel times
            for time in reel_view_times:
                interval = time.hour // interval_size * interval_size
                if interval not in hour_count.keys():
                    hour_count[interval] = 0
                hour_count[interval] += WEIGHTS['reels']
            
            # message view times
            for time in message_view_times:
                interval = time.hour // interval_size * interval_size
                if interval not in hour_count.keys():
                    hour_count[interval] = 0
                hour_count[interval] += WEIGHTS['messages']

            # find interval with maximum activity
            most_active_interval = max(hour_count, key=hour_count.get)

            return most_active_interval
        
    class _comments:
        def __init__(self, comments) -> None:
            self.comments = comments

        def total_comments(self) -> int:
            """Returns the total number of comments ever sent by the user."""
            post_comments_len = len(self.comments.post_comments['comments_media_comments'])

            reel_comments_len = len(self.comments.reels_comments['comments_reels_comments'])

            return (post_comments_len+reel_comments_len)

        def average_comment_length(self) -> int:
            """Returns the average comment length, int of words."""
            post_comments = [block['string_map_data']['Comment']['value'] for block in self.comments.post_comments['comments_media_comments']]

            reel_comments = [block['string_map_data']['Comment']['value'] for block in self.comments.reels_comments['comments_reels_comments']]

            comments = post_comments+reel_comments

            print(comments)
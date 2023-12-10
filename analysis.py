"""Analysis of Data"""
from datetime import datetime
from collections import Counter
from app.helpers import ParsedInstagramData


class DataAnalyzer:
    """Contains functions to analyze the instagram data, from the ParsedInstagramData class."""

    def __init__(self, data: ParsedInstagramData) -> None:
        self.data = data

        self.ads_topics_and_viewership = self._ads_topics_and_viewership(
            data.ads_and_topics,
            data.your_topics,
            data.information_about_you,
            data.messages,
        )

        self.comments = self._comments(data.comments)

        self.content = self._content(data.content)

    def export(self) -> dict:
        """Exports all the analyzed data into a dict."""

        # ads, topics and viewership
        ad_view_freq = self.ads_topics_and_viewership.ad_view_freq()
        account_based_in = self.ads_topics_and_viewership.account_based_in()
        possible_phone_numbers = self.ads_topics_and_viewership.possible_phone_numbers()

        return {
            'ad_view_freq': ad_view_freq,
            'account_based_in': account_based_in,
            'possible_phone_numbers': possible_phone_numbers
        }

    class _ads_topics_and_viewership:
        """Contains functions to analyze the data under the ads, topics and viewership group."""

        def __init__(
            self, ads_and_topics, your_topics, information_about_you, messages
        ) -> None:
            self.ads_and_topics = ads_and_topics
            self.your_topics = your_topics
            self.information_about_you = information_about_you
            self.messages = messages

        def ad_view_freq(self) -> int or float:
            """Returns the frequency of ads seen per day."""

            # times the user has seen an ad
            datetimes = []
            for block in self.ads_and_topics.ads_viewed["impressions_history_ads_seen"]:
                # time in format date month year, 24h:min
                timestamp = block["string_map_data"]["Time"]["timestamp"]
                datetimes.append(datetime.fromtimestamp(timestamp))

            # Group the datetime objects by day
            days = {}
            for dt in datetimes:
                day = dt.date()
                if day not in days:
                    days[day] = []
                days[day].append(dt)

            # Calculate the total number of ads seen
            total_ads = sum([len(times) for times in days.values()])

            average_frequency = total_ads / len(days)

            return average_frequency

        def account_based_in(self) -> str:
            """Returns city from which account is based in"""
            return self.information_about_you.account_based_in['inferred_data_primary_location'][0]['string_map_data']['City Name']['value']
        
        def possible_phone_numbers(self) -> list[str]:
            """Returns a list of possible phone numbers"""
            return [block['string_list_data'][0]['value'] for block in self.information_about_you.possible_phone_numbers['inferred_data_inferred_phone_numbers']]

        def latest_topics(self, n: int or None) -> list[str]:
            """Returns a list of latest (`n`) 'topics' which the instagram algorithm 
            has added to your list of sought for you.

            Args:
                `n` int or None

            If `n` is None, it returns the entire list."""

            topics = [
                block["string_map_data"]["Name"]["value"]
                for block in self.your_topics.your_topics["topics_your_topics"]
            ]

            return topics[-n:] if n is not None else topics

        def most_active_hours(self) -> int:
            """Returns an int, which specifies the start interval of a one hour period, 
            where the user has been active the most."""
            # weights
            weights = {"posts": 3, "reels": 2.5, "ads": 0.5, "messages": 0.05}

            # get list of times for posts and reels viewed
            ad_view_times = [
                block["string_map_data"]["Time"]["timestamp"]
                for block in self.ads_and_topics.ads_viewed[
                    "impressions_history_ads_seen"
                ]
            ]

            post_view_times = [
                block["string_map_data"]["Time"]["timestamp"]
                for block in self.ads_and_topics.posts_viewed[
                    "impressions_history_posts_seen"
                ]
            ]

            reel_view_times = [
                block["string_map_data"]["Time"]["timestamp"]
                for block in self.ads_and_topics.videos_watched[
                    "impressions_history_videos_watched"
                ]
            ]

            # convert into datetime objects
            ad_view_times = [
                datetime.strptime(x, r"%d %b %Y, %H:%M") for x in ad_view_times
            ]

            post_view_times = [
                datetime.strptime(x, r"%d %b %Y, %H:%M") for x in post_view_times
            ]

            reel_view_times = [
                datetime.strptime(x, r"%d %b %Y, %H:%M") for x in reel_view_times
            ]

            # message view times
            message_view_times = []
            for chat in self.messages.inbox:
                messages = chat.messages["messages"]
                times = [
                    datetime.fromtimestamp(int(message["timestamp_ms"]) / 1000)
                    for message in messages
                ]
                message_view_times.extend(times)

            hour_count = {}
            interval_size = 1

            # ad times
            for time in ad_view_times:
                interval = time.hour // interval_size * interval_size
                if interval not in hour_count.keys():
                    hour_count[interval] = 0
                hour_count[interval] += weights["ads"]

            # post time
            for time in post_view_times:
                interval = time.hour // interval_size * interval_size
                if interval not in hour_count.keys():
                    hour_count[interval] = 0
                hour_count[interval] += weights["posts"]

            # reel times
            for time in reel_view_times:
                interval = time.hour // interval_size * interval_size
                if interval not in hour_count.keys():
                    hour_count[interval] = 0
                hour_count[interval] += weights["reels"]

            # message view times
            for time in message_view_times:
                interval = time.hour // interval_size * interval_size
                if interval not in hour_count.keys():
                    hour_count[interval] = 0
                hour_count[interval] += weights["messages"]

            # find interval with maximum activity
            most_active_interval = max(hour_count, key=hour_count.get)

            return most_active_interval

    class _comments:
        def __init__(self, comments) -> None:
            post_comments = [
                (
                    block["string_map_data"]["Comment"]["value"],
                    block["string_map_data"]["Time"]["timestamp"],
                )
                for block in comments.post_comments.data
            ]

            self._post_comments = comments.post_comments

            reel_comments = [
                (
                    block["string_map_data"]["Comment"]["value"],
                    block["string_map_data"]["Time"]["timestamp"],
                )
                for block in comments.reels_comments["comments_reels_comments"]
            ]

            self.comments = post_comments + reel_comments

        def total_comments(self) -> int:
            """Returns the total number of comments ever sent by the user."""
            return len(self.comments)

        def average_comment_length(self) -> int:
            """Returns the average comment length, int of words."""

            avg_len = sum([len(comment[0]) for comment in self.comments]) / len(
                self.comments
            )

            return avg_len

        def most_used_emoji(self) -> str:
            """Returns the emoji most used by the user in comments.

            WIP"""

        def total_emojis_used(self) -> int:
            """Returns the total number of emojis used by the user in comments.

            WIP"""

        def average_comments_per_day(self) -> int:
            """Returns the average number of comments per day made by the user."""
            # Extract dates from time stamps
            dates = [
                datetime.strptime(time, r"%d %b %Y, %H:%M").date()
                for _, time, _ in self.comments
            ]

            # Get the number of unique dates
            unique_dates = len(set(dates))

            # Calculate the average number of comments per day
            average_comments_per_day = len(self.comments) / unique_dates

            return average_comments_per_day

        def most_commented_on_user(self) -> str:
            """Returns the username of the user, on whose posts the user has commented most."""
            comments_with_users = [
                (
                    block["string_map_data"]["Comment"]["value"],
                    block["string_map_data"].get("Media Owner", {}).get("value", ""),
                    block["string_map_data"]["Time"]["timestamp"],
                )
                for block in self._post_comments["comments_media_comments"]
            ]

            comment_count = {}
            for _, author, _ in comments_with_users:
                # if the author is not in the dictionary yet, add them with a count of 0
                if author == "":
                    continue

                if author not in comment_count.keys():
                    comment_count[author] = 0
                # incerment their count
                comment_count[author] += 1

            # most commented user
            most_commented_author = max(comment_count, key=comment_count.get)

            return most_commented_author

    class _content:
        def __init__(self, content) -> None:
            self.posts = content.posts
            self.profile_photos = content.profile_photos
            self.stories = content.stories

        def total_posts(self) -> int:
            """Total number of posts made by the user"""
            return len(self.posts)

        def posts_per_month(self, avg=True) -> dict:
            """Number of posts per month, as a dictionary with months as keys and the number of posts made in that month as values OR the average no. of posts per month."""
            months = []
            for post in self.posts.data:
                try:
                    months.append(
                        datetime.fromtimestamp(post["creation_timestamp"]).month
                    )
                except KeyError:  # some posts dont have a creation timestamp
                    # check their images for a approximate creation timestamp
                    # TODO
                    pass

            # take the average of all the values
            return [sum(months) / len(months)] if avg else Counter(months)

        def no_of_pfp_changes(self) -> int:
            """No. of times a user has changed their profile picture."""
            return len(self.profile_photos["ig_profile_picture"])

        def post_types(self) -> dict:
            """Types of posts (images, videos) based on the file extension of the uploaded posts."""
            post_types = {"IMAGE": 0, "VIDEO": 0, "OTHER": 0}
            for post in self.posts.data:
                media = post["media"]
                for file in media:
                    extension = file["uri"].split(".")[-1]
                    if extension in ["jpg", "jpeg", "png", "gif"]:
                        post_types["IMAGE"] += 1

                    elif extension in ["mp4", "webm", "mov"]:
                        post_types["VIDEO"] += 1

                    else:
                        post_types["OTHER"] += 1
            return post_types

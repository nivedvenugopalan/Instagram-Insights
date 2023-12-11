"""Analysis of Data"""
import emoji
import re

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
        your_topics = self.ads_topics_and_viewership.latest_topics(n=None)
        most_common_activity = None # TODO

        # comments
        total_comments = self.comments.total_comments()
        total_accounts_commented_on = self.comments.total_accounts_commented_on()
        total_post_comments = self.comments.total_post_comments()
        total_reel_comments = self.comments.total_reel_comments()
        most_used_emoji, most_used_emoji_count = self.comments.most_used_emoji()

        return {
            # ads, topics & viewership
            'ad_view_freq': ad_view_freq,
            'account_based_in': account_based_in,
            'possible_phone_numbers': possible_phone_numbers,
            'your_topics': your_topics,
            'most_common_activity': most_common_activity,

            # comments
            "total_comments": total_comments,
            "total_accounts_commented_on": total_accounts_commented_on,
            "total_post_comments": total_post_comments,
            "total_reel_comments": total_reel_comments,
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

        def most_common_activity(self) -> int:
            """Returns the zone across which the user has been most active."""

            def get_view_times(data, key):
                return [
                    datetime.fromtimestamp(int(block["string_map_data"]["Time"]["timestamp"]))
                    for block in data[key]
                ]

            post_view_times = get_view_times(self.ads_and_topics.posts_viewed, "impressions_history_posts_seen")
            reel_view_times = get_view_times(self.ads_and_topics.videos_watched, "impressions_history_videos_watched")


            # message view times
            message_view_times = []
            for userchat in self.messages.inbox:
                messages = userchat.messages["messages"]
                times = [
                    datetime.fromtimestamp(int(message["timestamp_ms"]) / 1000)
                    for message in messages
                ]
                message_view_times.extend(times)

            # posts_per_min_ = Counter(post_view_times, key=lambda t: t.minute)

            # TODO

            # find messaging speed, average posts per minute and average reels per minute
            return None

    class _comments:
        def __init__(self, comments) -> None:
            self.post_comments = []
            for comment in comments.post_comments.data:
                # get the media owner
                media_owner = comment["string_map_data"].get("Media Owner", {}).get("value", None)

                if isinstance(media_owner, dict):
                    media_owner = None

                # decode all unicode emojis
                comment_ = ["string_map_data"]["Comment"]["value"]
                for word in comment_.split(" "):
                    # if it contains \u, extract from that part until the last \u and add 4 characters
                    if "\u" in word:
                        word = word.split("\u")[0] + "\u" + word.split("\u")[-1][:4]

                self.post_comments.append(
                    {
                        'comment': comment_,
                        'media_owner': media_owner,
                        'timestamp': comment["string_map_data"]["Time"]["timestamp"],
                    }
                )


            self.reel_comments = []
            for comment in comments.reels_comments.data['comments_reels_comments']:
                media_owner = comment["string_map_data"].get("Media Owner", {}).get("value", None)

                self.reel_comments.append(
                    {
                        'comment': comment["string_map_data"]["Comment"]["value"],
                        'media_owner': media_owner,
                        'timestamp': comment["string_map_data"]["Time"]["timestamp"],
                    }
                )

            self.comments = self.post_comments + self.reel_comments

        def total_comments(self) -> int:
            """Returns the total number of comments ever sent by the user."""
            return len(self.comments)

        def total_accounts_commented_on(self) -> int:
            """Returns the total number of accounts commented on."""
            return len({comment['media_owner'] for comment in self.comments})
        
        def total_post_comments(self) -> int:
            """Returns the total number of post comments."""
            return len(self.post_comments)
        
        def total_reel_comments(self) -> int:
            """Returns the total number of reel comments."""
            return len(self.reel_comments)
            
        def average_comment_length(self) -> int:
            """Returns the average comment length, int of words."""

            avg_len = sum([len(comment[0]) for comment in self.comments]) / len(
                self.comments
            )

            return avg_len

        def _get_all_comments(self) -> list[str]:
            """Returns a list of all comments made by the user."""
            return [comment['comment'] for comment in self.comments]

        def most_used_emoji(self) -> (str, int):
            """Returns the emoji most used by the user in comments, how many times
            """
            comments = self._get_all_comments()
            emojis_ = []
            for comment in comments:
                de_emojized = emoji.demojize(comment)
                print(de_emojized)
                
                emojis_.extend(
                    [c for c in comments if emoji.is_emoji(c)]
                )
            print(emojis_)

            return "", 0


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

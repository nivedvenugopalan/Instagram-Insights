"""Analysis of Data"""
import emoji

from datetime import datetime
from collections import Counter
from helpers import ParsedInstagramData, fix_emojis, average_timestamps


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

        self.device_information = self._device_information(data.device_information)

        self.followers_and_following = self._followers_and_following(data.followers_and_following)

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
        average_comments_per_day = self.comments.average_comments_per_day()
        most_commented_on_user = self.comments.most_commented_on_user()
        total_emojis_used = self.comments.total_emojis_used()
        most_used_emoji = self.comments.most_used_emoji()

        ## content
        total_posts = self.content.total_posts()
        posts_per_month = self.content.posts_per_month()
        no_of_pfp_changes = self.content.no_of_pfp_changes()
        post_types = self.content.post_types()
        no_of_stories = self.content.no_of_stories()
        average_stories_per_day = self.content.average_stories_per_day()
        no_of_reels_shared_on_story = self.content.no_of_reels_shared_on_story()

        ## device information
        last_device_logged_onto = self.device_information.last_device_logged_onto()

        ## followers and following
        favorite_followers = self.followers_and_following.favorite_followers()
        no_of_blocked_users = self.followers_and_following.no_of_blocked_users()
        no_of_close_friends = self.followers_and_following.no_of_close_friends()
        close_friends = self.followers_and_following.close_friends_list()
        no_of_followers = self.followers_and_following.no_of_followers()
        earliest_follower = self.followers_and_following.earliest_follower()
        latest_follower = self.followers_and_following.latest_follower()
        no_of_following = self.followers_and_following.no_of_following()
        earliest_following = self.followers_and_following.earliest_following()
        latest_following = self.followers_and_following.latest_following()

        return {
            'ads_topics_viewsership' : {
                # ads, topics & viewership
                'ad_view_freq': ad_view_freq,
                'account_based_in': account_based_in,
                'possible_phone_numbers': possible_phone_numbers,
                'your_topics': your_topics,
                'most_common_activity': most_common_activity,
            },

            'comments': {
                "total_comments": total_comments,
                "total_accounts_commented_on": total_accounts_commented_on,
                "total_post_comments": total_post_comments,
                "total_reel_comments": total_reel_comments,
                "average_comments_per_day": average_comments_per_day,
                'most_commented_on_user': most_commented_on_user,
                'total_emojis_used': total_emojis_used,
                'most_used_emojis': most_used_emoji
            },

            'content': {
                'total_posts': total_posts,
                'posts_per_month': posts_per_month,
                'no_of_pfp_changes': no_of_pfp_changes,
                'post_types': post_types,
                'no_of_stories': no_of_stories,
                'average_stories_per_day': average_stories_per_day,
                'no_of_reels_shared_on_story': no_of_reels_shared_on_story,
            },
            
            'device_information': {
                'last_device_logged_onto': last_device_logged_onto
            },

            'followers_and_following': {
                'favorite_followers': favorite_followers,
                'no_of_blocked_users': no_of_blocked_users,
                'no_of_close_friends': no_of_close_friends,
                'close_friends': close_friends,
                'no_of_followers': no_of_followers,
                'earliest_follower': earliest_follower,
                'latest_follower': latest_follower,
                'no_of_following': no_of_following,
                'earliest_following': earliest_following,
                'latest_following': latest_following
            }
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
            timestamps = []
            for block in self.ads_and_topics.ads_viewed["impressions_history_ads_seen"]:
                # time in format date month year, 24h:min
                timestamp = block["string_map_data"]["Time"]["timestamp"]
                timestamps.append(timestamp)

            return average_timestamps(timestamps, key='day')

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
                comment_ = comment["string_map_data"]["Comment"]["value"]
                comment_ = fix_emojis(comment_)

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

            emojis = []
            for comment in self.comments:
                string = comment['comment']
                emojis.extend(
                    emoji.demojize(token.chars) for token in emoji.analyze(string)
                )
            
            top = Counter(emojis).most_common(n=1)[0]
            return top if top[0] is not None else ("", 0)


        def total_emojis_used(self) -> int:
            """Returns the total number of emojis used by the user in comments.
            """
            counts = [emoji.emoji_count(comment['comment']) for comment in self.comments]

            return sum(counts)

        def average_comments_per_day(self) -> int:
            """Returns the average number of comments per day made by the user."""
            # Extract dates from time stamps
            dates = [
                datetime.fromtimestamp(comment['timestamp']) for comment in self.comments 
            ]

            # Get the number of unique dates
            unique_dates = len(set(dates))

            # Calculate the average number of comments per day
            average_comments_per_day = len(self.comments) / unique_dates

            return average_comments_per_day

        def most_commented_on_user(self) -> (str, int):
            """Returns the username of the user, on whose posts the user has commented most along with the number of comments."""
            count = Counter(
                [comment["media_owner"] for comment in self.comments]
            )
            
            common = count.most_common(n=1)[0]

            return common if common[0] is not None else ("", 0)

    class _content:
        def __init__(self, content) -> None:
            self.posts = content.posts
            self.profile_photos = content.profile_photos
            self.stories = content.stories['ig_stories']

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

        def no_of_stories(self) -> int:
            """No. of stories the user has created."""
            return len(self.stories)
        
        def average_stories_per_day(self) -> int:
            """Average no. of stories per day the user has created."""
            timestamps = [story['creation_timestamp'] for story in self.stories]

            return average_timestamps(timestamps, key='day')
        
        def no_of_reels_shared_on_story(self) -> int:
            """No. of reels the user has shared."""
            count = 0
            for story in self.stories:
                try:
                    if story['media_metadata']['video_metadata']['exif_data'][0]['source_type'] == 'feed_reshare':
                        count += 1
                except KeyError as e:
                    if e == 'video_metadata':
                        pass
                
            return count
        
    class _device_information:
        def __init__(self, device_information) -> None:
            self.camera_information = device_information.camera_information
            self.devices = device_information.devices

        def last_device_logged_onto(self) -> str:
            return sorted(self.devices['devices_devices'], key=lambda x: x['string_map_data']['Last Login']['timestamp'], reverse=True)[0]['string_map_data']['User Agent']['value']
        
    class _followers_and_following:
        def __init__(self, followers_and_following) -> None:
            
            self.accounts_favorited = followers_and_following.accounts_favorited
            self.blocked_accounts = followers_and_following.blocked_accounts
            self.close_friends = followers_and_following.close_friends
            self.followers = followers_and_following.followers
            self.following = followers_and_following.following
            
        def favorite_followers(self) -> list[str]:
            """Returns a list of the favorite followers of the user."""
            return [
                account["string_list_data"][0]['value']
                for account in self.accounts_favorited['relationships_feed_favorites']
            ]
        
        def no_of_blocked_users(self) -> int:
            """Returns the number of blocked users."""
            return len(self.blocked_accounts['relationships_blocked_users'])
        
        def no_of_close_friends(self) -> int:
            """Returns the number of close friends."""
            return len(self.close_friends['relationships_close_friends'])
        
        def close_friends_list(self) -> list[str]:
            """Returns a list of the close friends of the user."""
            return [
                account["string_list_data"][0]['value']
                for account in self.close_friends['relationships_close_friends']
            ]
        
        def no_of_followers(self) -> int:
            """Returns the number of followers."""
            return len(self.followers)
        
        def earliest_follower(self) -> str:
            """Returns the username of the earliest follower."""
            return sorted(self.followers, key=lambda x: x['string_list_data'][0]['timestamp'])[0]['string_list_data'][0]['value']
        
        def latest_follower(self) -> str:
            """Returns the username of the latest follower."""
            return sorted(self.followers, key=lambda x: x['string_list_data'][0]['timestamp'], reverse=True)[0]['string_list_data'][0]['value'] 
        
        def no_of_following(self) -> int:
            """Returns the number of following."""
            return len(self.following["relationships_following"])
        
        def earliest_following(self) -> str:
            """Returns the username of the earliest following."""
            return sorted(self.following["relationships_following"], key=lambda x: x['string_list_data'][0]['timestamp'])[0]['string_list_data'][0]['value']
        
        def latest_following(self) -> str:
            """Returns the username of the latest following."""
            return sorted(self.following["relationships_following"], key=lambda x: x['string_list_data'][0]['timestamp'], reverse=True)[0]['string_list_data'][0]['value']

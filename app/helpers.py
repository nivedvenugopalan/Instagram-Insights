import json
import ast
import zipfile


class JsonFile:
    def __init__(self, data, name: str = "") -> None:
        self.data = data
        self.name = name if not "" else None


class ParsedInstagramData:
    def __init__(self, ads_viewed: JsonFile, posts_viewed: JsonFile, videos_watched: JsonFile, post_comments: JsonFile, reels_comments: JsonFile, posts: JsonFile, profile_photos: JsonFile, stories: JsonFile, camera_information: JsonFile, devices: JsonFile, blocked_accounts: JsonFile, close_friends: JsonFile, followers: JsonFile, following: JsonFile, ads_interest: JsonFile, liked_comments: JsonFile, liked_posts: JsonFile, login_activity: JsonFile, logout_activity: JsonFile, password_change_activity: JsonFile, message_data: list[(str, JsonFile)], profile_changes: JsonFile, account_searches: JsonFile, word_or_phrase_searches: JsonFile, saved_collections: JsonFile, saved_posts: JsonFile, emoji_sliders: JsonFile, polls: JsonFile, questions: JsonFile, quizzes: JsonFile, story_likes: JsonFile, your_topics: JsonFile) -> None:
        # ads_and_topics
        self.ads_and_topics = self._ads_and_topics(
            ads_viewed, posts_viewed, videos_watched)

        # comments
        self.comments = self._comments(post_comments, reels_comments)

        # content
        self.content = self._content(posts, profile_photos, stories)

        # device information
        self.device_information = self._device_information(
            camera_information, devices)

        # follwers and following
        self.followers_and_following = self._followers_and_following(
            blocked_accounts, close_friends, followers, following)

        # information about you
        self.information_about_you = self._information_about_you(ads_interest)

        # likes
        self.likes = self._likes(liked_comments, liked_posts)

        # login and account creation
        self.login_and_account_creation = self._login_and_account_creation(
            login_activity, logout_activity, password_change_activity)

        # messages
        self.messages = self._messages(message_data)

        # TODO: Message Requests

        # personal information
        self.personal_information = self._personal_information(profile_changes)

        # recent searches
        self.recent_searches = self._recent_searches(
            account_searches, word_or_phrase_searches)

        # saved
        self.saved = self._saved(saved_collections, saved_posts)

        # story sticker interactions
        self.story_sticker_interactions = self._story_sticker_interactions(
            emoji_sliders, polls, questions, quizzes, story_likes)

        # your topics
        self.your_topics = self._your_topics(your_topics)

    class _ads_and_topics:
        def __init__(self, ads_viewed: JsonFile, posts_viewed: JsonFile, videos_watched: JsonFile) -> None:
            self.ads_viewed = ads_viewed
            self.posts_viewed = posts_viewed
            self.videos_watched = videos_watched

    class _comments:
        def __init__(self, post_comments: JsonFile, reels_comments: JsonFile) -> None:
            self.post_comments = post_comments
            self.reels_comments = reels_comments

    class _content:
        def __init__(self, posts: JsonFile, profile_photos: JsonFile, stories: JsonFile) -> None:
            self.posts = posts
            self.profile_photos = profile_photos
            self.stories = stories

    class _device_information:
        def __init__(self, camera_information: JsonFile, devices: JsonFile) -> None:
            self.camera_information = camera_information
            self.devices = devices

    class _followers_and_following:
        def __init__(self, blocked_accounts: JsonFile, close_friends: JsonFile, followers: JsonFile, following: JsonFile) -> None:
            self.blocked_accounts = blocked_accounts
            self.close_friends = close_friends
            self.followers = followers
            self.following = following

    class _information_about_you:
        def __init__(self, ads_interest: JsonFile) -> None:
            self.ads_interest = ads_interest

    class _likes:
        def __init__(self, liked_comments: JsonFile, liked_posts: JsonFile) -> None:
            self.liked_comments = liked_comments
            self.liked_posts = liked_posts

    class _login_and_account_creation:
        def __init__(self, login_activity: JsonFile, logout_activity: JsonFile, password_change_activity: JsonFile) -> None:
            self.login_activity = login_activity
            self.logout_activity = logout_activity
            self.password_change_activity = password_change_activity

    # messages
    class _messages:
        def __init__(self, data: list[(str, JsonFile)]) -> None:
            self.inbox = []
            for user in data:
                self.inbox.append(
                    self._user(
                        username=user[0],
                        messages=user[1]
                    )
                )

        class _user:
            def __init__(self, username: str, messages: JsonFile) -> None:
                self.username = username
                self.messagses = messages

    class _personal_information:
        def __init__(self, profile_changes: JsonFile) -> None:
            self.profile_changes = profile_changes

    class _recent_searches:
        def __init__(self, account_searches: JsonFile, word_or_phrase_searches: JsonFile) -> None:
            self.recent_account_searches = account_searches
            self.recent_word_or_phrase_searches = word_or_phrase_searches

    class _saved:
        def __init__(self, saved_collections: JsonFile, saved_posts: JsonFile) -> None:
            self.saved_collections = saved_collections
            self.saved_posts = saved_posts

    class _story_sticker_interactions:
        def __init__(self, emoji_sliders: JsonFile, polls: JsonFile, questions: JsonFile, quizzes: JsonFile, story_likes: JsonFile) -> None:
            self.emoji_sliders = emoji_sliders
            self.polls = polls
            self.questions = questions
            self.quizzes = quizzes
            self.story_likes = story_likes

    class _your_topics:
        def __init__(self, your_topics: JsonFile) -> None:
            self.your_topics = your_topics


def parse_raw_data(archive: zipfile.ZipFile):

    inbox_folders = [x for x in archive.namelist() if x.endswith(
        "/") and x.startswith("messages/inbox/")]

    msg_data = []

    for chat in inbox_folders:
        username = chat[15:-1]

        if username == "" or len(username.split('/')) > 1:
            continue

        msg_data.append(
            (username, parse_json_bytes(
                archive.read(f"{chat}message_1.json")))
        )

    parsed_data = ParsedInstagramData(
        ads_viewed=parse_json_bytes(archive.read(
            'ads_and_topics/ads_viewed.json')),
        posts_viewed=parse_json_bytes(archive.read(
            'ads_and_topics/posts_viewed.json')),
        videos_watched=parse_json_bytes(archive.read(
            'ads_and_topics/videos_watched.json')),
        post_comments=parse_json_bytes(
            archive.read('comments/post_comments.json')),
        reels_comments=parse_json_bytes(
            archive.read('comments/reels_comments.json')),
        posts=parse_json_bytes(
            archive.read('content/posts_1.json')),
        profile_photos=parse_json_bytes(
            archive.read('content/profile_photos.json')),
        stories=parse_json_bytes(
            archive.read('content/stories.json')),
        camera_information=parse_json_bytes(archive.read(
            'device_information/camera_information.json')),
        devices=parse_json_bytes(archive.read(
            'device_information/devices.json')),
        blocked_accounts=parse_json_bytes(archive.read(
                                          'followers_and_following/blocked_accounts.json')),
        close_friends=parse_json_bytes(archive.read(
            'followers_and_following/close_friends.json')),
        followers=parse_json_bytes(archive.read(
            'followers_and_following/followers.json')),
        following=parse_json_bytes(archive.read(
            'followers_and_following/following.json')),
        ads_interest=parse_json_bytes(archive.read(
            'information_about_you/ads_interests.json')),
        liked_comments=parse_json_bytes(
            archive.read('likes/liked_comments.json')),
        liked_posts=parse_json_bytes(archive.read('likes/liked_posts.json')),
        login_activity=parse_json_bytes(archive.read(
            'login_and_account_creation/login_activity.json')),
        logout_activity=parse_json_bytes(archive.read(
            'login_and_account_creation/logout_activity.json')),
        password_change_activity=parse_json_bytes(archive.read(
            'login_and_account_creation/password_change_activity.json')),
        message_data=msg_data,
        profile_changes=parse_json_bytes(archive.read(
            'personal_information/profile_changes.json')),
        account_searches=parse_json_bytes(archive.read(
            'recent_searches/account_searches.json')),
        word_or_phrase_searches=parse_json_bytes(archive.read(
            'recent_searches/word_or_phrase_searches.json')),
        saved_collections=parse_json_bytes(
            archive.read('saved/saved_collections.json')),
        saved_posts=parse_json_bytes(archive.read('saved/saved_posts.json')),
        emoji_sliders=parse_json_bytes(archive.read(
            'story_sticker_interactions/emoji_sliders.json')),
        polls=parse_json_bytes(archive.read(
            'story_sticker_interactions/polls.json')),
        questions=parse_json_bytes(archive.read(
            'story_sticker_interactions/questions.json')),
        quizzes=parse_json_bytes(archive.read(
            'story_sticker_interactions/quizzes.json')),
        story_likes=parse_json_bytes(archive.read(
            'story_sticker_interactions/story_likes.json')),
        your_topics=parse_json_bytes(
            archive.read('your_topics/your_topics.json'))
    )

    return parsed_data


def parse_json_bytes(jsonbytes: bytes):
    rtn = json.loads(jsonbytes)
    rtn = JsonFile(data=rtn)
    return rtn

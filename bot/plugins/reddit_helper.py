import re
import json
import requests
from typing import Awaitable, Callable, Dict
from pydantic import BaseModel, Field


class RedditHelper:
    """
    A plugin to interact with Reddit.
    """
    def __init__(self):
        self.user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"

    def get_source_name(self) -> str:
        return "Reddit"

    def get_spec(self) -> [Dict]:
        return [{
            "name": "get_subreddit_feed",
            "description": "Get the latest posts from a subreddit.",
            "parameters": {
                "type": "object",
                "properties": {
                    "subreddit": {
                        "type": "string",
                        "description": "The subreddit to get the latest posts from."
                    }
                },
                "required": ["subreddit"],
            },
        },
        {
            "name": "get_user_feed",
            "description": "Get the latest posts from a given user.",
            "parameters": {
                "type": "object",
                "properties": {
                    "username": {
                        "type": "string",
                        "description": "The username to get the latest posts from."
                    }
                },
                "required": ["username"],
            },
        }]

    def parse_reddit_page(self, response):
        data = json.loads(response.content)
        output = []
        if "data" not in data:
            return output
        if "children" not in data["data"]:
            return output
        for item in data["data"]["children"]:
            output.append(item)
        return output

    def parse_posts(self, data: list):
        posts = []
        for item in data:
            if item["kind"] != "t3":
                continue
            item = item["data"]
            posts.append({
                "id": item["name"],
                "title": item["title"],
                "description": item["selftext"],
                "link": item["url"],
                "author_username": item["author"],
                "author_id": item["author_fullname"],
                "subreddit_name": item["subreddit"],
                "subreddit_id": item["subreddit_id"],
                "subreddit_subscribers": item["subreddit_subscribers"],
                "score": item["score"],
                "upvotes": item["ups"],
                "downvotes": item["downs"],
                "upvote_ratio": item["upvote_ratio"],
                "total_comments": item["num_comments"],
                "total_crossposts": item["num_crossposts"],
                "total_awards": item["total_awards_received"],
                "domain": item["domain"],
                "flair_text": item["link_flair_text"],
                "media_embed": item["media_embed"],
                "is_pinned": item["pinned"],
                "is_self": item["is_self"],
                "is_video": item["is_video"],
                "is_media_only": item["media_only"],
                "is_over_18": item["over_18"],
                "is_edited": item["edited"],
                "is_hidden": item["hidden"],
                "is_archived": item["archived"],
                "is_locked": item["locked"],
                "is_quarantined": item["quarantine"],
                "is_spoiler": item["spoiler"],
                "is_stickied": item["stickied"],
                "is_send_replies": item["send_replies"],
                "published_at": item["created_utc"],
            })
        return posts

    def parse_comments(self, data: list):
        comments = []
        for item in data:
            if item["kind"] != "t1":
                continue
            item = item["data"]
            comments.append({
                "id": item["name"],
                "body": item["body"],
                "link": item["permalink"],
                "post_id": item["link_id"],
                "post_title": item["link_title"],
                "post_link": item["link_permalink"],
                "author_username": item["author"],
                "author_id": item["author_fullname"],
                "subreddit_name": item["subreddit"],
                "subreddit_id": item["subreddit_id"],
                "score": item["score"],
                "upvotes": item["ups"],
                "downvotes": item["downs"],
                "total_comments": item["num_comments"],
                "total_awards": item["total_awards_received"],
                "is_edited": item["edited"],
                "is_archived": item["archived"],
                "is_locked": item["locked"],
                "is_quarantined": item["quarantine"],
                "is_stickied": item["stickied"],
                "is_send_replies": item["send_replies"],
                "published_at": item["created_utc"],
            })
        return comments

    async def execute(self, function_name, helper, **kwargs) -> Dict:
        if function_name == "get_subreddit_feed":
            return await self.get_subreddit_feed(**kwargs)
        elif function_name == "get_user_feed":
            return await self.get_user_feed(**kwargs)
        else:
            return {"error": f"Function {function_name} not found."}

    async def get_subreddit_feed(self, subreddit: str) -> str:
        """
        Get the latest posts from a subreddit, as an array of JSON objects.
        :param subreddit: The subreddit to get the latest posts from.
        :return: A list of posts or an error message.
        """
        headers = {"User-Agent": self.user_agent}

        if subreddit == "":
            return "Error: No subreddit provided"
        subreddit = subreddit.replace("/r/", "").replace("r/", "")

        if not re.match(r"^[A-Za-z0-9_]{2,21}$", subreddit):
            return "Error: Invalid subreddit name"

        try:
            response = requests.get(f"https://reddit.com/r/{subreddit}.json", headers=headers)

            if not response.ok:
                return f"Error: {response.status_code}"
            else:
                output = self.parse_posts(self.parse_reddit_page(response))
                return {"result": json.dumps(output)}
        except Exception as e:
            return f"Error: {e}"

    async def get_user_feed(self, username: str) -> str:
        """
        Get the latest posts from a given user, as a JSON object.
        :param username: The username to get the latest posts from.
        :return: An object with lists of posts and comments, or an error message.
        """
        headers = {"User-Agent": self.user_agent}

        if username == "":
            return "Error: No username provided."
        username = username.replace("/u/", "").replace("u/", "")

        if not re.match(r"^[A-Za-z0-9_]{3,20}$", username):
            return "Error: Invalid username."

        try:
            response = requests.get(f"https://reddit.com/u/{username}.json", headers=headers)

            if not response.ok:
                return f"Error: {response.status_code}"
            else:
                page = self.parse_reddit_page(response)  # user pages can have both posts and comments.
                posts = self.parse_posts(page)
                comments = self.parse_comments(page)
                return {"result": json.dumps({"posts": posts, "comments": comments})}
        except Exception as e:
            return f"Error: {e}"

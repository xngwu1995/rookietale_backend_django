# Social Media Network with Django

## accounts API introduction:
  1. sign up account: /api/accounts/signup/
  2. login account: /api/accounts/login/
  3. logout account: /api/accounts/logout/
  4. login status: /api/accounts/login_status/

## tweet API introduction:
  1. create a tweet: /api/tweets/
  2. show all tweets for a specific user: /api/tweets/?user_id={}/
  3. show a tweet details with comment: /api/tweets/?tweet_id={}/

## friendship API introduction:
  1. follow a user: /api/friendships/?user_id={}/follow/
  2. unfollow a user: /api/friendships/?user_id={}/unfollow/
  3. show all followers: /api/friendships/?user_id={}/followers/
  4. show all followings: /api/friendships/?user_id={}/followings/

## newsfeed API introduction:
  1. show all news that you received: /api/newsfeeds/

## comments API introduction:
  1. create a comment: /api/comment/
  2. show comments for a tweet: /api/comments/?tweet_id={}
  3. delete a comments: /api/comments/{comments_id}/
  4. update a comments: /api/comments/{comments_id}/

## likes API introduction:


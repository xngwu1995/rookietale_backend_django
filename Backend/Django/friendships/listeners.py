def invalidate_following_cache(instance, sender, **kwargs):
    from friendships.services import FriendshipService
    FriendshipService.invalidate_following_cache(instance.from_user_id)
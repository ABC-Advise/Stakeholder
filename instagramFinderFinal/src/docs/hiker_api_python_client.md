# Documentação do Client Python da Hiker API

## Instalação
Para usar a HikerAPI, instale com pip:

```bash
pip install hikerapi
```

## Uso Básico
```python
from hikerapi import Client
cl = Client(api_key="<sua_chave>")
cl.user_by_username_v1("usuario")

from hikerapi import AsyncClient
cl = AsyncClient(api_key="<sua_chave>")
await cl.user_by_username_v1("usuario")
```

## Métodos Principais (AsyncClient)
- async comment_likers_chunk_gql(...)
- async comments_chunk_gql(...)
- async comments_threaded_chunk_gql(...)
- async fbsearch_accounts_v2(...)
- async fbsearch_places_v1(...)
- async fbsearch_places_v2(...)
- async fbsearch_reels_v2(...)
- async fbsearch_topsearch_hashtags_v1(...)
- async fbsearch_topsearch_v1(...)
- async fbsearch_topsearch_v2(...)
- async hashtag_by_name_v1(...)
- async hashtag_by_name_v2(...)
- async hashtag_medias_clips(...)
- async hashtag_medias_clips_chunk_v1(...)
- async hashtag_medias_clips_v1(...)
- async hashtag_medias_clips_v2(...)
- async hashtag_medias_recent(...)
- async hashtag_medias_recent_v2(...)
- async hashtag_medias_top(...)
- async hashtag_medias_top_chunk_v1(...)
- async hashtag_medias_top_recent_chunk_v1(...)
- async hashtag_medias_top_v1(...)
- async hashtag_medias_top_v2(...)
- async highlight_by_id(...)
- async highlight_by_id_v2(...)
- async highlight_by_url_v1(...)
- async location_by_id_v1(...)
- async location_guides_v1(...)
- async location_medias_recent_chunk_v1(...)
- async location_medias_recent_v1(...)
- async location_medias_top_chunk_v1(...)
- async location_medias_top_v1(...)
- async location_search_v1(...)
- async media_by_code_v1(...)
- async media_by_id_v1(...)
- async media_by_url_v1(...)
- async media_code_from_pk_v1(...)
- async media_comment_offensive(...)
- async media_comment_offensive_v2(...)
- async media_comments(...)
- async media_comments_chunk_v1(...)
- async media_comments_v2(...)
- async media_info_by_code_v2(...)
- async media_info_by_id_v2(...)
- async media_info_by_url_v2(...)
- async media_insight_v1(...)
- async media_likers_gql(...)
- async media_likers_v1(...)
- async media_likers_v2(...)
- async media_oembed_v1(...)
- async media_pk_from_code_v1(...)
- async media_pk_from_url_v1(...)
- async media_template_v2(...)
- async media_user_v1(...)
- async search_accounts_v2(...)
- async search_hashtags_v1(...)
- async search_hashtags_v2(...)
- async search_music_v1(...)
- async search_music_v2(...)
- async search_places_v2(...)
- async search_reels_v2(...)
- async search_topsearch_v2(...)
- async search_users_v1(...)
- async share_by_code_v1(...)
- async share_by_url_v1(...)
- async share_reel_by_url_v1(...)
- async story_by_id_v1(...)
- async story_by_id_v2(...)
- async story_by_url_v1(...)
- async story_by_url_v2(...)
- async story_download_by_story_url_v1(...)
- async story_download_by_url_v1(...)
- async story_download_v1(...)
- async track_by_canonical_id(...)
- async track_by_canonical_id_v2(...)
- async track_by_id(...)
- async track_by_id_v2(...)
- async track_stream_by_id(...)
- async track_stream_by_id_v2(...)
- async user_a2(...)
- async user_about_v1(...)
- async user_by_id_v1(...)
- async user_by_id_v2(...)
- async user_by_url_v1(...)
- async user_by_username_v1(...)
- async user_by_username_v2(...)
- async user_clips(...)
- async user_clips_chunk_v1(...)
- async user_clips_v1(...)
- async user_clips_v2(...)
- async user_explore_businesses_by_id_v2(...)
- async user_followers_chunk_gql(...)
- async user_followers_chunk_v1(...)
- async user_followers_v2(...)
- async user_following(...)
- async user_following_chunk_gql(...)
- async user_following_chunk_v1(...)
- async user_following_v2(...)
- async user_highlights(...)
- async user_highlights_by_username(...)
- async user_highlights_by_username_v1(...)
- async user_highlights_by_username_v2(...)
- async user_highlights_v1(...)
- async user_highlights_v2(...)
- async user_medias(...)
- async user_medias_chunk_v1(...)
- async user_medias_pinned_v1(...)
- async user_medias_v2(...)
- async user_related_profiles_gql(...)
- async user_search_followers_v1(...)
- async user_search_following_v1(...)
- async user_stories_by_username_v1(...)
- async user_stories_by_username_v2(...)
- async user_stories_v1(...)
- async user_stories_v2(...)
- async user_tag_medias(...)
- async user_tag_medias_chunk_v1(...)
- async user_tag_medias_v2(...)
- async user_web_profile_info_v1(...)
- async userstream_by_id_v2(...)
- async userstream_by_username_v2(...)

## Métodos Principais (Client)
- Métodos síncronos equivalentes aos do AsyncClient

## Observações
- Consulte este arquivo para exemplos de uso e assinatura dos métodos.
- Para detalhes completos, consulte a documentação oficial da HikerAPI.

## Exemplos de Resposta dos Métodos Principais

### user_by_username_v1("victordavi_oc")
```json
{
  "pk": 3688474053,
  "username": "victordavi_oc",
  "full_name": "Victor Davi",
  "is_private": false,
  "profile_pic_url": "https://...",
  "profile_pic_url_hd": null,
  "is_verified": false,
  "media_count": 10,
  "follower_count": 502,
  "following_count": 595,
  "biography": "24 anos 😁\n🖥🖱⌨+🎼🎶🎙\nEngenheiro de Software",
  "external_url": "",
  "account_type": 3,
  "is_business": false,
  "public_email": "",
  "contact_phone_number": "",
  "public_phone_country_code": "",
  "public_phone_number": "",
  "business_contact_method": "UNKNOWN",
  "business_category_name": null,
  "category_name": null,
  "category": "Just for fun",
  "address_street": "",
  "city_id": 0,
  "city_name": "",
  "latitude": 0.0,
  "longitude": 0.0,
  "zip": "",
  "instagram_location_id": "",
  "interop_messaging_user_fbid": 118330336218247
}
```

### user_by_url_v1("https://instagram.com/victordavi_oc")
```json
{
  "pk": 3688474053,
  "username": "victordavi_oc",
  "full_name": "Victor Davi",
  "is_private": false,
  "profile_pic_url": "https://...",
  "profile_pic_url_hd": null,
  "is_verified": false,
  "media_count": 10,
  "follower_count": 502,
  "following_count": 595,
  "biography": "24 anos 😁\n🖥🖱⌨+🎼🎶🎙\nEngenheiro de Software",
  "external_url": "",
  "account_type": 3,
  "is_business": false,
  "public_email": "",
  "contact_phone_number": "",
  "public_phone_country_code": "",
  "public_phone_number": "",
  "business_contact_method": "UNKNOWN",
  "business_category_name": null,
  "category_name": null,
  "category": "Just for fun",
  "address_street": "",
  "city_id": 0,
  "city_name": "",
  "latitude": 0.0,
  "longitude": 0.0,
  "zip": "",
  "instagram_location_id": "",
  "interop_messaging_user_fbid": 118330336218247
}
```

### user_web_profile_info_v1("victordavi_oc")
```json
{
  "user": {
    "id": "3688474053",
    "username": "victordavi_oc",
    "full_name": "Victor Davi",
    "biography": "24 anos 😁\n🖥🖱⌨+🎼🎶🎙\nEngenheiro de Software",
    "profile_pic_url": "https://...",
    "profile_pic_url_hd": "https://...",
    "is_private": false,
    "is_verified": false,
    "category_name": "Just for fun",
    "edge_followed_by": {"count": 502},
    "edge_follow": {"count": 595},
    "highlight_reel_count": 3,
    "media_count": 10
    // ... outros campos omitidos para brevidade
  }
}
```

### search_accounts_v2(query="Victor Davi")
```json
{
  "num_results": 20,
  "users": [
    {
      "pk": 51659898470,
      "username": "victor.d.hanson",
      "full_name": "Victor Davis Hanson",
      "is_private": false,
      "profile_pic_url": "https://...",
      "is_verified": false
      // ... outros campos
    },
    {
      "pk": 48243289922,
      "username": "victor_.davi",
      "full_name": "Victor Davi",
      "is_private": true,
      "profile_pic_url": "https://...",
      "is_verified": false
      // ... outros campos
    }
    // ... outros perfis
  ],
  "has_more": true,
  "rank_token": "...",
  "status": "ok"
}
``` 
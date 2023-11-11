<?php
/**
 * Plugin Name: Ofirio Blog
 * Description: Our plugin to add custom behavior to WordPress
 */

add_action('post_updated', 'notify_post_updated', 10, 3);
function notify_post_updated($post_id, $post_after, $post_before) {
    $slug_before = $post_before->post_name;
    $slug_after = $post_after->post_name;
    $status_before = $post_before->post_status;
    $status_after = $post_after->post_status;

    $published_or_trashed = in_array($status_after, array('publish', 'trash'));
    $unpublished = $status_before == 'publish' && $status_after == 'draft';

    if ($published_or_trashed || $unpublished) {
        send_a_cache_notification($post_before);
        if ($slug_before !== $slug_after) {
            send_a_cache_notification($post_after);
        }
    }

}


function send_a_cache_notification($post) {
    $postid = $post->ID;
    $slug = $post->post_name;
    $author_slug = get_the_author_meta('nickname', $post->post_author);

    $cats = get_the_category($postid);
    if (!empty($cats)) {
        $cat_slug = $cats[0]->slug;
    }

    $url_1 = OFIRIO_CACHE_URL_1 . '?slug=' . $slug . '&id=' . $postid . '&category_slug=' . $cat_slug . '&author_slug=' . $author_slug . '&secret=' . OFIRIO_CACHE_SECRET;
    $url_2 = OFIRIO_CACHE_URL_2 . '?slug=' . $slug . '&id=' . $postid . '&category_slug=' . $cat_slug . '&author_slug=' . $author_slug . '&secret=' . OFIRIO_CACHE_SECRET;

    file_get_contents($url_1);
    file_get_contents($url_2);

    cache_log_write("Sent: " . $url_1 . ', ' . $url_2);
}


function cache_log_write($log_string) {
    $dt = date("Y-m-d H:i:s  ");
    file_put_contents(OFIRIO_CACHE_LOG_PATH, $dt . $log_string.PHP_EOL, FILE_APPEND | LOCK_EX);
}


/**
 * Display our preview link on Edit page
 */
add_action( 'wp_loaded', 'replace_preview' );
function replace_preview() {
    $query = array();
    parse_str($_SERVER['QUERY_STRING'], $query);
    $is_editing = $query['action'] == 'edit';
    $is_post_php = str_starts_with($_SERVER['REQUEST_URI'], '/wp-admin/post.php?');

    if ($is_editing && $is_post_php) {
        $preview_url = 'https://' . OFIRIO_HOSTNAME . '/blog/' . $query['post'] . '--no-cache';
        echo '<script type="text/javascript">
                setTimeout(function() {
                    document.querySelector(
                        "div.block-editor-post-preview__dropdown"
                    ).innerHTML = "<a target=\"_blank\" href=\"' . $preview_url . '\">Preview</a>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;";
                }, 10000);
              </script>';
    }
}

<?php

$isAdmin = (array_key_exists('context', $_REQUEST) && $_REQUEST['context'] === 'edit');
$title = block_value('title');
$url = block_value('url');
$count = block_value('count');
$seoTag = block_value('tag');


if (block_rows('related_posts')):

    if ($isAdmin) {
        echo '<b>RELATED POSTS:</b><br>';

        while (block_rows('related_posts')) {
            block_row('related_posts');
            $post = block_sub_value('post');

            echo '<li>[id';
            echo $post->ID;
            echo '] ';
            echo trim($post->post_title);
            echo '<br></li>';
        }
        reset_block_rows('related_posts');

    } else {
        $resultSet = [];
        while (block_rows('related_posts')) {
            block_row('related_posts');
            $resultSet[] = block_sub_value('post')->ID;
        }
        $result = json_encode(['post_ids' => $resultSet]);

        echo '{{RELATED-POSTS}}';
        echo base64_encode($result);
        echo '{{/RELATED-POSTS}}';

        reset_block_rows('related_posts');
    }

endif;

?>

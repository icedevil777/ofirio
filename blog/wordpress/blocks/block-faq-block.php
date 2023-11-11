<?php

$isAdmin = (array_key_exists('context', $_REQUEST) && $_REQUEST['context'] === 'edit');
$title = block_value('title');
$url = block_value('url');
$count = block_value('count');
$seoTag = block_value('tag');


if (block_rows('qas')):

    if ($isAdmin) {
        echo '<b>FAQ:</b><br>';

        while (block_rows('qas')) {
            block_row('qas');

            echo '<li>';
            echo trim(block_sub_value('question'));
            echo trim(block_sub_value('answer'));
            echo '</li>';
        }
        reset_block_rows('qas');

    } else {
        $resultSet = [];
        while (block_rows('qas')) {
            block_row('qas');
            $resultSet[] = [
                'question' => block_sub_value('question'),
                'answer' => trim(strip_tags(block_sub_value('answer'))),
            ];
        }
        $result = json_encode(['qas' => $resultSet]);

        echo '{{FAQ-BLOCK}}';
        echo base64_encode($result);
        echo '{{/FAQ-BLOCK}}';

        reset_block_rows('qas');
    }

endif;

?>

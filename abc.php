<html> <body>
<?php
?> <img src="logo.jpg"> <?php

if(isset($_POST['field1']) ) {
    $data = $_POST['field1'] ;
    $ret = file_put_contents('mydata.txt', $data);
    
}
else {
   $var1 = $_GET['var1'];
$ret = file_put_contents('mydata.txt', $var1);

}    

	$f = fopen("results.txt", "r");
?>  <center><?php
	echo " <br> You need a list of ";
	echo fgets($f); 
echo "</center>";
	fclose($f);
	include ("page2.html");
	exec("test4.py");

?>
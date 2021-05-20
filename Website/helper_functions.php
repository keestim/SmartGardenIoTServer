<?php
    ini_set('display_errors',1);
    error_reporting(E_ALL);

    header("Access-Control-Allow-Origin", "*");
    header("Access-Control-Allow-Headers", "Origin, X-Requested-With, Content-Type, Accept");

    function curl_api_request($api_url)
    {        
        //https://weichie.com/blog/curl-api-calls-with-php/
        // create & initialize a curl session
        $curl = curl_init();

        // set our url with curl_setopt()
        curl_setopt(
            $curl, 
            CURLOPT_URL, 
            $api_url);

        // return the transfer as a string, also with setopt()
        curl_setopt(
            $curl, 
            CURLOPT_RETURNTRANSFER, 
            1);

        // curl_exec() executes the started curl session
        // $output contains the output string
        $output = curl_exec($curl);

        // close curl resource to free up system resources
        // (deletes the variable made by curl_init)
        curl_close($curl); 

        return $output;
    }
?>
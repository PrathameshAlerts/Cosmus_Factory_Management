"""
"GitsApp"
This is not readme file
only for internal communication 


"""

<!DOCTYPE html>
<html>
<head>
    <title>Send Data with Path and Query Params</title>
</head>
<body>
    <button id="sendData">Send Data</button>

    <script>
        document.getElementById('sendData').addEventListener('click', function() {
            const year = 2024;
            const month = 6;
            const day = 15;
            const url = new URL(`/some-path/${year}/${month}/${day}/`, window.location.origin);

            const queryParams = {
                category: 'books',
                author: 'John Doe'
            };

            // Append query params to URL
            Object.keys(queryParams).forEach(key => url.searchParams.append(key, queryParams[key]));

            fetch(url)
                .then(response => response.json())
                .then(data => console.log(data))
                .catch(error => console.error('Error:', error));
        });
    </script>
</body>
</html>
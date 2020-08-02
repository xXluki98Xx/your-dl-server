<!doctype html>
<html lang="en">

  <head>
    <!-- Required meta tags -->
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
    <meta name="Description" content="Web frontend for youtube-dl">

    <!-- Bootstrap CSS -->
    <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.1.3/css/bootstrap.min.css" integrity="sha384-MCw98/SFnGE8fJT3GXwEOngsV7Zt27NXFoaoApmYm81iuXoPkFOJwJ8ERdknLPMO"
      crossorigin="anonymous">
    <link href="/static/style.css" rel="stylesheet">

    <title>History</title>
  </head>

  <body>

    <header>
      <h1 class="logo">ydl-server</h1>
      <input type="checkbox" id="nav-toggle" class="nav-toggle">
      <nav>
        <ul>
          <li><a href="/">Home</a></li>
          <li><a href="/downloads/">Downloads</a></li>
          <li><a href="/history">History</a></li>
          <li><a onclick="history.back()">Previous Site</a></li>
        </ul>
      </nav>
      <label for="nav-toggle" class="nav-toggle-label">
        <span></span>
      </label>
    </header>

    <div class="content container">

      <h1 class="text-light">Download History:</h1>
      <table border=0 class= "row justify-content-center text-left">
        %for item in history:
          <td><a href="{{ item['url'] }}" target="blank">{{ item['kind'] }} | {{ item['title'] }} | {{ item['status'] }}</a><td></tr>
        %end
      </table>

    </div>

    <footer>
      <div>
        <p class="text-muted">Web frontend for <a class="text-light" href="https://rg3.github.io/youtube-dl/">youtube-dl</a>,
          by <a class="text-light" href="https://twitter.com/manbearwiz">@manbearwiz</a>.</p>
      </div>
    </footer>

    <!-- Optional JavaScript -->
    <!-- jQuery first, then Popper.js, then Bootstrap JS -->
    <script src="https://code.jquery.com/jquery-3.3.1.slim.min.js" integrity="sha384-q8i/X+965DzO0rT7abK41JStQIAqVgRVzpbzo5smXKp4YfRvH+8abtTE1Pi6jizo"
      crossorigin="anonymous"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.14.3/umd/popper.min.js" integrity="sha384-ZMP7rVo3mIykV+2+9J3UJ46jBk0WLaUAdn689aCwoqbBJiSnjAK/l8WvCWPIPm49"
      crossorigin="anonymous"></script>
    <script src="https://stackpath.bootstrapcdn.com/bootstrap/4.1.3/js/bootstrap.min.js" integrity="sha384-ChfqqxuZUCnJSK3+MXmPNIyE6ZbWh2IMqE241rYiqJxyMiZ6OW/JmZQ5stwEULTy"
      crossorigin="anonymous"></script>
    <!-- Navbar -->
    <script src="/static/navbar.js"></script>
  </body>

</html>

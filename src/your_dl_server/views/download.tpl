<!doctype html>
<html lang="en">

  <head>
    <!-- Required meta tags -->
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
    <meta name="Description" content="Web frontend for youtube-dl">
    <meta http-equiv="refresh" content="60">

    <!-- Bootstrap CSS -->
    <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.1.3/css/bootstrap.min.css" integrity="sha384-MCw98/SFnGE8fJT3GXwEOngsV7Zt27NXFoaoApmYm81iuXoPkFOJwJ8ERdknLPMO"
      crossorigin="anonymous">
    <link href="/static/style.css" rel="stylesheet">

    <title>your-dl-server</title>
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

    <div id="download" class="content row">

      <div class="col-12 text-light">
        <h1>Downloaded</h1>
      </div>

      <div class="col-4">
        <h1 class="text-light">Directories:</h1>
        <br/>
        <table border=0 class= "row justify-content-left listBox">
          %for item in directories:
            <td><a href = "{{ item['url'] }}">{{ item['title'] }}</a><td></tr>
          %end
        </table>
      </div>

      <div class="col-1"></div>

      <div class="col-7">
        <h1 class="text-light">Files:</h1>
        <br/>
        <table border=0 class= "row justify-content-left listBox">
          %for item in files:
            <td><a href = "{{ item['url'] }}">{{ item['title'] }}</a><td></tr>
          %end
        </table>
      </div>

    </div>

    <footer>
      <div class="text-muted">
          <p>Web frontend for <a class="text-light" href="https://rg3.github.io/youtube-dl/">youtube-dl</a>,
          by <a class="text-light" href="https://github.com/xXluki98Xx/youtube-dl-server">xXluki98Xx</a>. A Fork of <a class="text-light" href="https://github.com/manbearwiz/youtube-dl-server">manbearwiz/youtube-dl-server</a>.</p>
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

  </body>

</html>

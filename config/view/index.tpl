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
    <link href="static/style.css" rel="stylesheet">

    <title>youtube-dl</title>
  </head>

  <body>
    <div class="container d-flex flex-column text-light text-center">
      <div class="flex-grow-1"></div>
      <div class="jumbotron bg-transparent flex-grow-1">
        <h1 class="display-4">youtube-dl</h1>
        <p class="lead">Enter a video url to download the video to the server. Url can be to YouTube or <a class="text-info"
            href="https://rg3.github.io/youtube-dl/supportedsites.html">any
            other supported site</a>. The server will automatically download the highest quality version available.</p>
        <hr class="my-4">
        <div>
          <form action="/api/add" method="POST">
            <div class="input-group">
              <input name="url" type="url" class="form-control" placeholder="URL / MAGNETLINK" aria-label="URL / MAGNETLINK" aria-describedby="button-submit" autofocus>
              <select class="custom-select" name="downloadTool">
                <optgroup label="Download Tool">
                  <option value="youtube-dl">Youtube-DL</option>
                  <option value="wget">wget</option>
                  <option value="torrent">Torrent</option>
                </optgroup>
              </select>
              <select class="custom-select" name="download">
                <optgroup label="Download">
                  <option value="normal">Normal</option>
                  <option value="axel">Axel</option>
                </optgroup>
              </select>
            </div>

            <div class="input-group">
              <input name="reference" type="reference" class="form-control" placeholder="REFERENCE" aria-label="REFERENCE" aria-describedby="button-submit" autofocus>
              <input name="title" type="title" class="form-control" placeholder="TITLE" aria-label="TITLE" aria-describedby="button-submit" autofocus>
              <input name="path" type="path" class="form-control" placeholder="PATH" aria-label="PATH" aria-describedby="button-submit" autofocus>
            </div>

            <div class="input-group">
              <input name="retries" type="retries" class="form-control" placeholder="RETRIES (5)" aria-label="RETRIES" aria-describedby="button-submit" autofocus>
              <input name="minSleep" type="minSleep" class="form-control" placeholder="MIN SLEEP (2s)" aria-label="MINSLEEP" aria-describedby="button-submit" autofocus>
              <input name="maxSleep" type="maxSleep" class="form-control" placeholder="MAX SLEEP (15s)" aria-label="MAXSLEEP" aria-describedby="button-submit" autofocus>
              <input name="bandwidth" type="bandwidth" class="form-control" placeholder="BANDWIDTH (unlimited)"  aria-label="BANDWIDTH" aria-describedby="button-submit" autofocus>
            </div>

            <div class="input-group">
              <input name="username" type="username" class="form-control" placeholder="USERNAME" aria-label="USERNAME" aria-describedby="button-submit" autofocus>
              <input name="password" type="password" class="form-control" placeholder="PASSWORD" aria-label="PASSWORD" aria-describedby="button-submit" autofocus>
            </div>

            <div class="input-group-append">
              <button class="btn btn-primary" type="submit" id="button-submit">Submit</button>
            </div>
          </form>
          <a href="/downloads/" target=""><button class="btn btn-primary">Downloads</button></a>
          <a href="/history/" target=""><button class="btn btn-primary">History</button></a>
        </div>
      </div>
      <footer>
        <div>
          <p class="text-muted">Web frontend for <a class="text-light" href="https://rg3.github.io/youtube-dl/">youtube-dl</a>,
            by <a class="text-light" href="https://twitter.com/manbearwiz">@manbearwiz</a>.</p>
        </div>
      </footer>
    </div>

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
